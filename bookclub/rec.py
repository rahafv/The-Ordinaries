from .models import Rating, Book
from surprise import KNNBasic
from surprise import Dataset
from surprise import Reader

import pandas as pd

from collections import defaultdict
from operator import itemgetter
import heapq

import os
import csv



class Recommender:
    def __init__(self):
        self.trainset = self.load_dataset().build_full_trainset()

    # def load_dataset(self):
    #     ratings_path = os.path.abspath("book-review-dataset/BX-Book-Ratings.csv")
    #     reader = Reader(line_format='user item rating ', sep=',', skip_lines=1)
    #     ratings_dataset = Dataset.load_from_file(ratings_path, reader=reader)

    #     # Lookup a movie's name with it's Movielens ID as key
    #     books_path = os.path.abspath("book-review-dataset/BX_Books.csv")
    #     movieID_to_name = {}
    #     with open(books_path, "r", encoding='latin-1') as csvfile:

    #             movie_reader = csv.reader(csvfile)
    #             next(movie_reader)
    #             for row in movie_reader:
    #                 movieID = int(row[0])
    #                 movie_name = row[1]
    #                 movieID_to_name[movieID] = movie_name
    #     # Return both the dataset and lookup dict in tuple
    #     return (ratings_dataset, movieID_to_name)

    def load_dataset(self):
        ratingObj = Rating.objects.all()
        user_ids = []
        book_ids = []
        ratings = [] 
        for obj in ratingObj:
            user_ids.append(obj.user.id)
            book_ids.append(obj.book.id)
            ratings.append(obj.rating)

        ratings_dict = {'userID': user_ids,
                    'bookID': book_ids,
                    'rating': ratings}
        df = pd.DataFrame.from_dict(ratings_dict)

        reader = Reader(rating_scale=(0, 10))
        data = Dataset.load_from_df(df[['userID', 'bookID', 'rating']], reader)
        return data

    def generateCandidates(self, user_id, k=20):
        similarity_matrix = KNNBasic(
            sim_options={
            'name': 'cosine',
            'user_based': False
            }
        ).fit(self.trainset).compute_similarities()

        user_iid = self.trainset.to_inner_uid(user_id)
        user_ratings = self.trainset.ur[user_iid]
        k_neighbors = heapq.nlargest(k, user_ratings, key=lambda t: t[1])

        candidates = defaultdict(float)
        for itemID, rating in k_neighbors:
            try:
                similaritities = similarity_matrix[itemID]
                for innerID, score in enumerate(similaritities):
                    candidates[innerID] += score * (rating / 10.0)
            except:
                continue

        for itemID, rating in self.trainset.ur[user_iid]:
            candidates.pop(itemID)

        return candidates

    # def getBookName(self, movieID):
    #     if int(movieID) in self.bookID_to_name:
    #         return self.bookID_to_name[int(movieID)]
    #     else:
    #         return ""

    def getBookName(self, bookID):
        try:
            return Book.objects.all().get(id=bookID).title
        except:
            return None

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

print("-------------gggggggggggggggjgjgjgjgg----------")