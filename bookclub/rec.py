import math
from .models import Rating, Book
from surprise import KNNBasic, PredictionImpossible
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

    def computeYearSimilarity(self, movie1, movie2, years):
        diff = abs(years[movie1] - years[movie2])
        sim = math.exp(-diff / 10.0)
        return sim

    def estimate(self, u, i):

        if not (self.trainset.knows_user(u) and self.trainset.knows_item(i)):
            raise PredictionImpossible('User and/or item is unkown.')
        
        # Build up similarity scores between this item and everything the user rated
        neighbors = []
        for rating in self.trainset.ur[u]:
            yearSimilarity = self.similarities[i,rating[0]]
            neighbors.append( (yearSimilarity, rating[1]) )
        
        # Extract the top-K most-similar ratings
        k_neighbors = heapq.nlargest(self.k, neighbors, key=lambda t: t[0])
        
        # Compute average sim score of K neighbors weighted by user ratings
        simTotal = weightedSum = 0
        for (simScore, rating) in k_neighbors:
            if (simScore > 0):
                simTotal += simScore
                weightedSum += simScore * rating
            
        if (simTotal == 0):
            raise PredictionImpossible('No neighbors')

        predictedRating = weightedSum / simTotal

        return predictedRating

print("-------------gggggggggggggggjgjgjgjgg----------")