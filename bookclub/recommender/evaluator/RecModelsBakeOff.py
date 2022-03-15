# -*- coding: utf-8 -*-
"""
Created on Thu May  3 11:11:13 2018

@author: Frank
"""

from .Evaluator import Evaluator
from bookclub.recommender.rec import ContentKNNAlgorithm, Recommender
from surprise import KNNBasic, SVD
from surprise import NormalPredictor

import random
import numpy as np

class RecModelsBakeOff:
    def __init__(self):
        self.rec = Recommender()

    def LoadBooksData(self):
        print("Loading book ratings...")
        data = self.rec.load_dataset()
        return data

    def evaluate(self):
        np.random.seed(0)
        random.seed(0)

        # Load up common data set for the recommender algorithms
        evaluationData = self.LoadBooksData()

        # Construct an Evaluator to, you know, evaluate them
        evaluator = Evaluator(evaluationData)

        # User-based KNN
        UserKNN = KNNBasic(sim_options = {'name': 'cosine', 'user_based': True})
        evaluator.AddAlgorithm(UserKNN, "User KNN")

        # Item-based KNN
        ItemKNN = KNNBasic(sim_options = {'name': 'cosine', 'user_based': False})
        evaluator.AddAlgorithm(ItemKNN, "Item KNN")

        # Item-based KNN
        genre = ContentKNNAlgorithm()
        evaluator.AddAlgorithm(genre, "genre similarity")

        # SVD
        svd = SVD()
        evaluator.AddAlgorithm(svd, "SVD")

        # Just make random recommendations
        Random = NormalPredictor()
        evaluator.AddAlgorithm(Random, "Random")

        # Fight!
        evaluator.Evaluate(False)

        evaluator.SampleTopNRecs(self.rec)
