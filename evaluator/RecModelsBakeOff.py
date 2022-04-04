# -*- coding: utf-8 -*-
"""
Created on Thu May  3 11:11:13 2018

@author: Frank
"""

import random

import numpy as np
from surprise import SVD, KNNBasic, KNNWithMeans, KNNWithZScore, NormalPredictor, SVDpp

from book_rating import BookRatings
from Evaluator import Evaluator


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

        # Item-based KNNWithMeans
        ItemKNN = KNNWithMeans(sim_options = {'name': 'cosine', 'user_based': False})
        evaluator.AddAlgorithm(ItemKNN, "Item KNNWithMeans")

        # Item-based KNNWithZScore
        ItemKNN = KNNWithZScore(sim_options = {'name': 'cosine', 'user_based': False})
        evaluator.AddAlgorithm(ItemKNN, "Item KNNWithZScore")

        # SVD
        svd = SVD()
        evaluator.AddAlgorithm(svd, "SVD")

        # SVD pp
        svd = SVDpp()
        evaluator.AddAlgorithm(svd, "SVD pp")

        # Random recommendations
        Random = NormalPredictor()
        evaluator.AddAlgorithm(Random, "Random")

        # Fight!
        evaluator.Evaluate(True)

        evaluator.SampleTopNRecs(bookRatings)

def main():
    recommendations = RecModelsBakeOff()
    recommendations.evaluate()

if __name__ == "__main__":
    main()
