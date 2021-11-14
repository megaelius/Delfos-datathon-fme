from google_images_search import GoogleImagesSearch
import geopy.distance

def find_image(gis,restaurant_name):
    gis.search({'q': "Restaurante" + restaurant_name, 'num': 3, 'imgType': 'photo','fileType': 'jpeg'})
    return gis.results()[0].url

def get_restaurant_data(json_data, idx):
    data = {}
    data["name"] = json_data[idx]["title"]
    data["rating"] = json_data[idx]["rating"]
    data["price"] = json_data[idx]["price"]
    data["coordinates"] = (json_data[idx]["gps_coordinates"]["latitude"], json_data[idx]["gps_coordinates"]["longitude"])
    data["phone"] = json_data[idx]["phone"]
    data["website"] = json_data[idx]["website"]
    data["address"] = json_data[idx]["address"]
    data["image"] = json_data[idx]["thumbnail"]
    return data

def compute_distances(user_dist,rest_dist):
    return geopy.distance.distance(user_dist,rest_dist).m
