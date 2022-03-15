import math

import numpy as np
from bookclub.models import Rating, Book, User
from bookclub.recommender.evaluator.Evaluator import Evaluator
from surprise import AlgoBase, KNNBasic, PredictionImpossible
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
        similarity_matrix = ContentKNNAlgorithm().fit(self.trainset).compute_similarities()

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

class ContentKNNAlgorithm(AlgoBase):

    def __init__(self, k=40, sim_options={}):
        AlgoBase.__init__(self)
        self.k = k

    def fit(self, trainset):
        AlgoBase.fit(self, trainset)

        # Compute item similarity matrix based on content attributes

        # Load up genre vectors for every book
        genres = self.getGenres()

        print("Computing content-based similarity matrix...")
        
        itemBasedSimilarities = self.getItemBasedSimilarity()

        # Compute genre distance for every book combination as a 2x2 matrix
        self.similarities = np.zeros((self.trainset.n_items, self.trainset.n_items))
        
        for thisRating in range(self.trainset.n_items):
            if (thisRating % 100 == 0):
                print(thisRating, " of ", self.trainset.n_items)
            for otherRating in range(thisRating+1, self.trainset.n_items):
                thisBookID = int(self.trainset.to_raw_iid(thisRating))
                otherBookID = int(self.trainset.to_raw_iid(otherRating))
                genreSimilarity = self.computeGenreSimilarity(thisBookID, otherBookID, genres)
                self.similarities[thisRating, otherRating] = genreSimilarity
                self.similarities[otherRating, thisRating] = genreSimilarity

        for innerID, score in enumerate(self.similarities):
            self.similarities[innerID] = score + itemBasedSimilarities[innerID]
        
        print("...done.")
                
        return self

    def getItemBasedSimilarity(self):
        similarity_matrix = KNNBasic(
            sim_options={
            'name': 'cosine',
            'user_based': False
            }
        ).fit(self.trainset).compute_similarities()

        return similarity_matrix
    
    def computeGenreSimilarity(self, book1, book2, genres):
        genres1 = genres[book1]
        genres2 = genres[book2]
        sumxx, sumxy, sumyy = 0, 0, 0
        for i in range(len(genres1)):
            x = genres1[i]
            y = genres2[i]
            sumxx += x * x
            sumyy += y * y
            sumxy += x * y
        
        return sumxy/math.sqrt(sumxx*sumyy)

    def getGenres(self):
        genres = defaultdict(list)
        genreIDs = {}
        maxGenreID = 0
        books = Book.objects.all()
        
        for book in books:
            book_id = book.id
            genreList = book.genre.split(',')
            genreIDList = []
            
            for genre in genreList:
                if genre in genreIDs:
                    genreID = genreIDs[genre]
                else:
                    genreID = maxGenreID
                    genreIDs[genre] = genreID
                    maxGenreID += 1
                genreIDList.append(genreID)
            
            genres[book_id] = genreIDList
        
        # Convert integer-encoded genre lists to bitfields that we can treat as vectors
        for (book_id, genreIDList) in genres.items():
            bitfield = [0] * maxGenreID
            for genreID in genreIDList:
                bitfield[genreID] = 1
            genres[book_id] = bitfield            
        
        return genres

    def estimate(self, u, i):

        if not (self.trainset.knows_user(u) and self.trainset.knows_item(i)):
            raise PredictionImpossible('User and/or item is unkown.')
        
        # Build up similarity scores between this item and everything the user rated
        neighbors = []
        for rating in self.trainset.ur[u]:
            genreSimilarity = self.similarities[i,rating[0]]
            neighbors.append( (genreSimilarity, rating[1]) )
        
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