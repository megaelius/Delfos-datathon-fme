from google_images_search import GoogleImagesSearch
import geopy.distance
import numpy as np

def find_image(gis,restaurant_name):
    gis.search({'q': "Restaurante" + restaurant_name, 'num': 3, 'imgType': 'photo','fileType': 'jpeg'})
    return gis.results()[0].url

def get_restaurant_data(json_data, idx):
    data = {}
    data["name"] = json_data[idx]["title"]
    data["rating"] = json_data[idx]["rating"]
    data["price"] = json_data[idx]["price"]
    data["coordinates"] = (json_data[idx]["gps_coordinates"]["latitude"], json_data[idx]["gps_coordinates"]["longitude"])
    if "phone" in json_data[idx]:
        data["phone"] = json_data[idx]["phone"]
    else:
        data["phone"] = "No available phone for this restaurant."
    if "website" in json_data[idx]:
        data["website"] = json_data[idx]["website"]
    else:
        data["website"] = "No available website for this restaurant."
    data["address"] = json_data[idx]["address"]
    data["image"] = json_data[idx]["thumbnail"]
    return data

def compute_distances(user_pos,rest_pos):
    return int(geopy.distance.distance(user_pos,rest_pos).m)


def get_recommendations_centroid(recommendations):
    centroid = np.zeros((1,2))
    for r in recommendations:
        centroid += np.array(r['coordinates'])/len(recommendations)
    return centroid[0]
