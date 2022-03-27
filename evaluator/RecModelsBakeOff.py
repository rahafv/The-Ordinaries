# -*- coding: utf-8 -*-
"""
Created on Thu May  3 11:11:13 2018

@author: Frank
"""

from .Evaluator import Evaluator
from surprise import KNNBasic, SVD, NormalPredictor
from .book_rating import BookRatings
from .genreKNN import GenreKNNAlgorithm

import random
import numpy as np

class RecModelsBakeOff:

    def __init__(self):
        self.bookRatings = BookRatings()

    def LoadBooksData(self):
        print("Loading book ratings...")
        data = self.bookRatings.load_dataset()
        
        rankings = self.bookRatings.getPopularityRanks()

        return (data, rankings)

    def evaluate(self):
        np.random.seed(0)
        random.seed(0)

        # Load up common data set for the recommender algorithms
        (evaluationData, rankings) = self.LoadBooksData()
        print('here=================')

        # Construct an Evaluator to evaluate the recommender algorithms
        evaluator = Evaluator(evaluationData, rankings)
        print('here#######################')

        # User-based KNN
        UserKNN = KNNBasic(sim_options = {'name': 'cosine', 'user_based': True})
        evaluator.AddAlgorithm(UserKNN, "User KNN")
        print('here@@@@@@@@@@@@@@@@@@@@@@@@@@')

        # Item-based KNN
        ItemKNN = KNNBasic(sim_options = {'name': 'cosine', 'user_based': False})
        evaluator.AddAlgorithm(ItemKNN, "Item KNN")
        print('here@@@@@@@@@@@@@@@@@@@@@@@@@@')

        # Content KNN
        genreKNN = GenreKNNAlgorithm()
        evaluator.AddAlgorithm(genreKNN, "Content KNN")
        print('here@@@@@@@@@@@@@@@@@@@@@@@@@@')

        # SVD
        svd = SVD()
        evaluator.AddAlgorithm(svd, "SVD")
        print('here@@@@@@@@@@@@@@@@@@@@@@@@@@')

        # Random recommendations
        Random = NormalPredictor()
        evaluator.AddAlgorithm(Random, "Random")

        print('here')

        # Fight!
        evaluator.Evaluate(True)

        evaluator.SampleTopNRecs(self.bookRatings, self.bookRatings.getTestUser())