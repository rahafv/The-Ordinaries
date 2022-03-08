import math
from .models import Rating, Book, User
from surprise import KNNBasic, PredictionImpossible
from surprise import Dataset
from surprise import Reader

import pandas as pd

from collections import defaultdict
from operator import itemgetter
import heapq

import os
import csv



class Recommender2:
    def __init__(self):
        self.trainset = self.load_dataset().build_full_trainset()

    def load_dataset(self):
        bookObj = Book.objects.all()
        user_ids = []
        book_ids = []
        rating_num = []
        for obj in bookObj:
            for reader in obj.readers.all():
                user_ids.append(reader.id)
                book_ids.append(obj.id)
                rating_num.append(obj.readers_count())

        books_dict = {'userID': user_ids,
                    'bookID': book_ids,
                    'rating': rating_num}
        df = pd.DataFrame.from_dict(books_dict)

        reader = Reader(rating_scale=(0, 10))
        data = Dataset.load_from_df(df[['userID', 'bookID', 'rating']], reader)
        return data

    def generateCandidates(self, user_id, k=20):
        similarity_matrix = KNNBasic(
            sim_options={
            'name': 'cosine',
            'user_based': True
            }
        ).fit(self.trainset).compute_similarities()

        user_iid = self.trainset.to_inner_uid(user_id)
        user_ratings = self.trainset.ur[user_iid]
        k_neighbors = heapq.nlargest(k, user_ratings, key=lambda t: t[1])

        candidates = defaultdict(float)
        for userID, rating in k_neighbors:
            try:
                similaritities = similarity_matrix[userID]
                print(len(similaritities))
                for innerID, score in enumerate(similaritities):
                    if score != 0 :
                        print(score)
                    user = self.trainset.to_inner_uid(innerID)
                    sim = User.objects.get(id=user_id).books.filter(id__in=User.objects.get(id=user).books).count()
                    print("sim")

                    candidates[innerID] += score 
            except:
                continue

     

        return candidates

    def get_recommendations(self, user_id, numOfRec):
        recommendations = []
        candidates = self.generateCandidates(user_id)

        position = 0
        for itemID, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
            recommendations.append(self.getBookName(self.trainset.to_raw_iid(itemID)))
            position += 1
            if (position > numOfRec): 
                break 

        return recommendations 

    def getBookName(self, bookID):
        try:
            return Book.objects.all().get(id=bookID).title
        except:
            return None

        

print("-------------gggggggggggggggjgjgjgjgg----------")