import json
import argparse
import numpy as np
import pandas as pd

from tqdm import tqdm
from pathlib import Path
from sentence_transformers import SentenceTransformer

#model = SentenceTransformer('all-mpnet-base-v2')
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
def main(input_path, output_path):
    f=open(input_path)
    json_data=json.load(f)
    nrows = len(json_data)

    if not Path(output_path).exists():
        Path(output_path).mkdir()
    for restaurant in tqdm(json_data):
        #print(restaurant)
        for user_review in restaurant['reviews_data']:
            text = user_review['snippet']
            if not (Path(output_path) / (restaurant['place_id'] + '_' + user_review['user']['name'].replace('/','') + '.npy')).is_file():
                matrix = model.encode(text)
                try:
                    np.save(Path(output_path) / (restaurant['place_id'] + '_' + user_review['user']['name'].replace('/','') + '.npy'),matrix)
                except:
                    print(user_review)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_path', type=str, default='Data/data.json', help='input json path')
    parser.add_argument('--out_path', type=str, default='Data/embeddings', help='output_path for embeddings')
    args = parser.parse_args()
    main(args.json_path, args.out_path)
