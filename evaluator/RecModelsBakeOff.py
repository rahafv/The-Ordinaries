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

    def LoadBooksData(self):
        bookRatings = BookRatings()
        print("Loading book ratings...")
        data = bookRatings.load_dataset()
        print("\nComputing book popularity ranks to measure novelty ...")
        rankings = bookRatings.getPopularityRanks()
        return (bookRatings, data, rankings)

    def evaluate(self):
        np.random.seed(0)
        random.seed(0)

        # Load up common data set for the recommender algorithms
        (bookRatings, evaluationData, rankings) = self.LoadBooksData()

        # Construct an Evaluator to evaluate the recommender algorithms
        evaluator = Evaluator(evaluationData, rankings)

        # User-based KNN
        UserKNN = KNNBasic(sim_options = {'name': 'cosine', 'user_based': True})
        evaluator.AddAlgorithm(UserKNN, "User KNN")

        # Item-based KNN
        ItemKNN = KNNBasic(sim_options = {'name': 'cosine', 'user_based': False})
        evaluator.AddAlgorithm(ItemKNN, "Item KNN")

        # Content KNN
        # genreKNN = GenreKNNAlgorithm()
        # evaluator.AddAlgorithm(genreKNN, "Content KNN")

        # SVD
        svd = SVD()
        evaluator.AddAlgorithm(svd, "SVD")

        # Random recommendations
        Random = NormalPredictor()
        evaluator.AddAlgorithm(Random, "Random")

        # Fight!
        print('here--------------')
        evaluator.Evaluate(False)

        evaluator.SampleTopNRecs(bookRatings)