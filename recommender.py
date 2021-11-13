import json
import math
import numpy as np
from numpy.linalg import norm
from queue import PriorityQueue
import geopy.distance

from sklearn.metrics.pairwise import cosine_similarity

class Recommender(object):

    #"""initializes a recommender from a movie file and a ratings file"""
    def __init__(self):

        # Reading the observations.
        f = open('./data/data.json')
        self.json_data = json.load(f)

        # Read customers names and create dictionary customer_names and restaurant ratings.
        customer_idx = 0
        self.customer_names = {} # dictionary containing customer_name - idx pairs.
        self._restaurant_ratings = {} # ratings for a restaurant.
        self._user_ratings = {} # ratings for a user
        for restaurant_idx, restaurant in enumerate(self.json_data):
            for review in restaurant['reviews_data']:
                self.customer_names[review['user']['name']] = customer_idx
                # Its the first time a restaurant is added to the dict.
                if review['user']['name'] not in self._user_ratings:
                    self._user_ratings[customer_idx] = [(restaurant_idx, rating)]
                else:
                    self._user_ratings[customer_idx].append((restaurant_idx, rating))

                if restaurant_idx not in self._restaurant_ratings:
                    self._restaurant_ratings[restaurant_idx] = [(customer_idx, rating)]
                else:
                    self._restaurant_ratings[restaurant_idx].append((customer_idx, rating))
                customer_idx += 1

        self._restaurant_dicts = []
        for i,restaurant in range(length(self.json_data)):
            aux_dict = {}
            aux_dict["Price"] = len(restaurant['price'])
            aux_dict["Coordinates"] = (restaurant["gps_coordinates"]["latitude"],restaurant["gps_coordinates"]["longitude"])
            aux_dict["Embeddings"]  = {r['user']['name']:np.zeros((384,)) for r in restaurant['reviews_data']}
            for i,user_review in enumerate(restaurant['reviews_data']):
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
        for i in range(self._restaurant_dicts):
            for j in range(i+1,self._restaurant_dicts):
                d = geopy.distance.vincenty(self._restaurant_dicts[i]['Coordinates'], self._restaurant_dicts[j]['Coordinates']).km
                if d > self._max_geo_distance:
                    self._max_geo_distance = d
        print(f'Max distance between restaurants is {self._max_geo_distance}')


    """returns a list of pairs (userid, rating) of users that
       have rated restaurant restaurant_id"""
    def get_restaurant_ratings(self, restaurant_id):
        if restaruant_id > 0 and restaurant_id < len(self.json_data):
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
        if cont = 0:
            return 0
        else:
            return sim/cont


    def similarity_coordinates(coord1, coord2):
        distance = geopy.distance.vincenty(coord1, coord2).km
        return 1 - distance/self._max_geo_distance


    def similarity_variables(variable, values1, values2):
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


    def similarity(self, restaurant1, restarurant2):
        '''
        Function that computes the similarity between two restaurants.
        '''
        sim = 0
        for variable in restaurant1:
            sim += similarity_variables(variable, restaurant1[variable], restaurant2[variable]) * 1/len(restaurant1)
        return sim



    def recommend_item_to_item(self, user_name, k, put_visited_too = False):
        '''
        Returns a list of at most k pairs (restaurant,predicted_rating)
        adequate for a user whose name is user_name
        '''

        # Get the user index,
        user_idx = self.customer_names[user_name]
        rating_dict = dict(self.get_user_ratings(user_idx))
        pq = PriorityQueue(maxsize = k)

        for restaurant_id in range(len(self.json_data)):
            if not put_visited_too and restaurant_id not in rating_dict:
                restaurant1 = self.get_dictionary(restaruant_id)
                sum_sim = 0
                pred = 0
                for restaruant_id_gone, rating in rating_dict.items():
                    restaurant2 = self.get_dictionary(restaruant_id_gone)
                    sim = self.similarity(restaurant1, restaurant2)
                    # if sim > 0.3:
                    sum_sim += sim
                    pred += sim * (rating - restaurant2["Rating"])

                if pred > 0:
                    pred = pred/sum_sim + restaurant1["Rating"]


                if not pq.full(): pq.put((pred, restaruant_id_gone))
                else:
                    top = pq.get()
                    if top[0] < pred:
                        pq.put((pred,restaruant_id_gone ))
                    else:
                        pq.put(top)

        return pq

def main():
    r = Recommender()

    pq = r.recommend_item_to_item('Paula Salazar', 10)
    while not pq.empty():
        top = pq.get()
        print(pq.qsize() + 1, ': ', r.movie_name(top[1]), sep='')
    print()
    print()
main()
