import json
import math
import time
import numpy as np
from pathlib import Path

from recommender import Recommender

def main():
    ini = time.time()
    w = {'Price':1/12,
         'Embedding':3/12,
         'Ratings':3/12,
         'Rating':1/6,
         'Embeddings':1/6,
         'Coordinates':1/12
    }
    r = Recommender(var_weights = w)
    print('Time in the init:', time.time() - ini)

    user = 'pablo gonzalo zalazar (Pablonza)'
    #user = 'Gemma'
    print('Already visited restaurants:')
    #print(r.print_user_reviews(user))

    group = ['pablo gonzalo zalazar (Pablonza)','D Behr','Fiona Cargill']
    for u in group:
        print(r.print_user_reviews(u))
    ini = time.time()
    #recomendations = r.recommend_item_to_item(user, 100, put_visited_too=False)
    recomendations = r.recommend_to_group(group, 10, coords_group = (41.3808593, 2.1746778))
    print('Time in the item to item:', time.time() - ini)
    for i in range(len(recomendations)):
        try:
            print(i+1, ': ', r.restaurant_name(recomendations[i][1]), ' - ', recomendations[i][0], ' - ', recomendations[i][2], sep='')
        except:
            print(i+1, ': ', r.restaurant_name(recomendations[i][1]), ' - ', recomendations[i][0], sep='')
    print()
    print()

if __name__ == '__main__':
    main()
