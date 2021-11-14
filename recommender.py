import json
import math
import time
import numpy as np
from pathlib import Path
from numpy.linalg import norm
from queue import PriorityQueue
import geopy.distance
from statistics import harmonic_mean

from sklearn.metrics.pairwise import cosine_similarity

class Recommender(object):

    #"""initializes a recommender from a movie file and a ratings file"""
    def __init__(self,var_weights = None):

        # Reading the observations.
        f = open('./Data/data.json')
        self.json_data = json.load(f)
        print(len(self.json_data))


        # Read customers names and create dictionary customer_names and restaurant ratings.
        customer_idx = 0
        self.customer_names = {} # dictionary containing customer_name - idx pairs.
        self._restaurant_ratings = {} # ratings for a restaurant.
        self._user_ratings = {} # ratings for a user
        for restaurant_idx, restaurant in enumerate(self.json_data):
            for review in restaurant['reviews_data']:
                if review['user']['name'] not in self.customer_names:
                    self.customer_names[review['user']['name']] = customer_idx
                    customer_idx += 1
                aux_customer_idx = self.customer_names[review['user']['name']]
                # Its the first time a restaurant is added to the dict.
                if aux_customer_idx not in self._user_ratings:
                    self._user_ratings[aux_customer_idx] = [(restaurant_idx, review['rating'])]
                else:
                    self._user_ratings[aux_customer_idx].append((restaurant_idx, review['rating']))

                if restaurant_idx not in self._restaurant_ratings:
                    self._restaurant_ratings[restaurant_idx] = [(aux_customer_idx, review['rating'])]
                else:
                    self._restaurant_ratings[restaurant_idx].append((aux_customer_idx, review['rating']))
        print('Total reviewers:',len(self.customer_names))

        self._restaurant_dicts = []
        for i, restaurant in enumerate(self.json_data):
            aux_dict = {}
            aux_dict["Price"] = restaurant['price']
            aux_dict["Coordinates"] = (restaurant["gps_coordinates"]["latitude"],restaurant["gps_coordinates"]["longitude"])
            aux_dict["Embeddings"]  = {r['user']['name']:np.zeros((384,)) for r in restaurant['reviews_data']}
            for j,user_review in enumerate(restaurant['reviews_data']):
                aux_dict["Embeddings"][user_review['user']['name']] = np.load(Path('Data/embeddings') / (restaurant['place_id'] + '_' + user_review['user']['name'] + '.npy'))
            aux_dict["Embedding"] = np.zeros((384,))
            #average all the embeddings from the same restaurant
            for username in aux_dict["Embeddings"]:
                aux_dict['Embedding'] += aux_dict["Embeddings"][username]
            aux_dict['Embedding'] /= len(aux_dict)
            aux_dict["Ratings"] = self._restaurant_ratings[i]
            aux_dict["Rating"] = restaurant['rating']
            self._restaurant_dicts.append(aux_dict)

        self._max_geo_distance = 0
        for i in range(len(self._restaurant_dicts)):
            for j in range(i+1,len(self._restaurant_dicts)):
                d = geopy.distance.distance(self._restaurant_dicts[i]['Coordinates'], self._restaurant_dicts[j]['Coordinates']).km
                if d > self._max_geo_distance:
                    self._max_geo_distance = d
        print(f'Max distance between restaurants is {self._max_geo_distance}')

        if var_weights is None:
            self.weights = {'Price':1/6,
                            'Embedding':1/6,
                            'Ratings':1/6,
                            'Rating':1/6,
                            'Embeddings':1/6,
                            'Coordinates':1/6
            }
        else:
            self.weights = var_weights

    def set_var_weights(self,var_weights):
        self.weights = var_weights

    def print_user_reviews(self,user_name):
        for restaurant_id, rating in self._user_ratings[self.customer_names[user_name]]:
            print(self.json_data[restaurant_id]['title'],':',rating)

    def restaurant_name(self,id):
        return self.json_data[id]['title']

    """returns a list of pairs (userid, rating) of users that
       have rated restaurant restaurant_id"""
    def get_restaurant_ratings(self, restaurant_id):
        if restaurant_id > 0 and restaurant_id < len(self.json_data):
            return self._restaurant_ratings[restaurant_id]
        return None

    """returns a list of pairs (restaurant,rating) of restaurants
       rated by user userid"""
    def get_user_ratings(self, user_id):
        if user_id in self._user_ratings:
            return self._user_ratings[user_id]
        return None

    """returns the list of user id's in the dataset"""
    def userid_list(self):
        return self._user_ratings.keys()

    def get_dictionary(self,restaurant_idx):
        return self._restaurant_dicts[restaurant_idx]

    def similarity_ratings(self, ratings_A, ratings_B):
        mean_A = sum([x for _, x in ratings_A]) / len(ratings_A)
        mean_B = sum([x for _, x in ratings_B]) / len(ratings_B)
        c1 = 0
        c2 = 0
        c3 = 0
        a_dict = dict(ratings_A)
        b_dict = dict(ratings_B)
        cont = 0
        for item in a_dict:
            if item in b_dict:
                cont += 1
                c1 += (float(a_dict[item]) - mean_A)*(float(b_dict[item]) - mean_B)
                c2 += (float(a_dict[item]) - mean_A)**2
                c3 += (float(b_dict[item]) - mean_B)**2
        try:
            return c1/(math.sqrt(c2*c3))
        except:
            return 0


    def similarity_embeddings(self, embeddings_A, embeddings_B):
        a_dict = dict(embeddings_A)
        b_dict = dict(embeddings_B)
        cont, sim = 0, 0
        for item in a_dict:
            if item in b_dict:
                cont += 1
                sim += cosine_similarity(a_dict[item].reshape(1,-1), b_dict[item].reshape(1,-1))[0][0]
        if cont == 0:
            return 0
        else:
            return sim/cont


    def similarity_coordinates(self, coord1, coord2):
        distance = geopy.distance.distance(coord1, coord2).km
        return 1 - distance/self._max_geo_distance


    def similarity_variables(self, variable, values1, values2):
        if variable == 'Price':
            return 1 - abs(values1 - values2)/3

        elif variable == 'Embedding':
             return cosine_similarity(values1.reshape(1,-1), values2.reshape(1,-1))[0][0]

        elif variable == 'Ratings':
            return self.similarity_ratings(values1, values2)

        elif variable == 'Rating':
            return 2*(1 - abs(values1 - values2)/5) - 1

        elif variable == 'Embeddings':
            return self.similarity_embeddings(values1, values2)

        elif variable == 'Coordinates':
            return self.similarity_coordinates(values1, values2)


    def similarity(self, restaurant1, restaurant2, coords = None):
        '''
        Function that computes the similarity between two restaurants.
        '''
        sim = {v:0 for v in restaurant1}
        for variable in restaurant1:
            if variable == 'Coordinates' and coords is not None:
                sim[variable] = self.similarity_variables(variable, restaurant1[variable], coords)
            else:
                sim[variable] = self.similarity_variables(variable, restaurant1[variable], restaurant2[variable])
        return sim

    def recommend_to_group(self, names, k, put_visited_too=False, coords_group = None):
        recomendations = {}

        for name in names:
            recs = self.recommend_item_to_item(name, 10*k, put_visited_too=put_visited_too,coords = coords_group)
            res = []
            for rec in recs:
                if rec[1] not in recomendations:
                    recomendations[rec[1]] = [rec[0]]
                else:
                    recomendations[rec[1]].append(rec[0])

        results = {}
        for restaurant, predictions in recomendations.items():
            if len(predictions) == len(names):
                results[restaurant] = harmonic_mean(predictions)

        return [(v, k) for k, v in sorted(results.items(), key=lambda item: -item[1])][:(min(k, len(results)))]

    def recommend_item_to_item(self, user_name, k, put_visited_too = False, coords = None):
        '''
        Returns a list of at most k pairs (restaurant,predicted_rating)
        adequate for a user whose name is user_name
        '''

        # Get the user index,
        user_idx = self.customer_names[user_name]
        rating_dict = dict(self.get_user_ratings(user_idx))
        pq = PriorityQueue(maxsize = k)
        for restaurant_id in range(len(self.json_data)):
            if restaurant_id not in rating_dict:
                restaurant1 = self.get_dictionary(restaurant_id)
                sum_values, sim_values = [], []
                average_sim = {}
                pred = 0
                for restaurant_id_gone, rating in rating_dict.items():
                    restaurant2 = self.get_dictionary(restaurant_id_gone)
                    sim = self.similarity(restaurant1, restaurant2, coords = coords)
                    s = 0
                    for v in sim:
                        s += sim[v]*self.weights[v]
                        if v in average_sim:
                            average_sim[v] += sim[v]/len(rating_dict)
                        else:
                            average_sim[v] = sim[v]/len(rating_dict)
                    # if sim > 0.3:

                    sum_values.append(rating - restaurant2["Rating"])
                    sim_values.append(s)
                    pred += s * (rating - restaurant2["Rating"])
                    '''
                    pred += s * (rating - restaurant2["Rating"])
                    '''

                if pred > 0:
                    #print(pred, sim_values, norm(sim_values), sum_values, norm(sum_values)
                    pred = pred/sum(sim_values) + restaurant1["Rating"]

                if not pq.full(): pq.put((pred, restaurant_id, average_sim))
                else:
                    top = pq.get()
                    if top[0] < pred:
                        pq.put((pred, restaurant_id, average_sim))
                    else:
                        pq.put(top)

            elif put_visited_too:
                pred = rating_dict[restaurant_id]
                if not pq.full(): pq.put((pred, restaurant_id, None))
                else:
                    top = pq.get()
                    if top[0] < pred:
                        pq.put((pred, restaurant_id, None))
                    else:
                        pq.put(top)

        topk = [None for _ in range(k)]
        i = k - 1
        while not pq.empty():
            topk[i] = pq.get()
            i -= 1
        return topk
