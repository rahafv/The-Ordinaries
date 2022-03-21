from bookclub.recommender.book_ratings import BookRatings
from bookclub.models import User
from surprise import KNNBasic
from bookclub.recommender.book_ratings import BookRatings

from collections import defaultdict
from operator import itemgetter
import heapq


class Recommender:
    def __init__(self):
        self.dataset = BookRatings().load_dataset()
        self.trainset = self.dataset.build_full_trainset()

    def generateCandidates(self, user_id, k=20):
        similarity_matrix = KNNBasic(sim_options = {'name': 'cosine',
                 'user_based': False}).fit(self.trainset).compute_similarities()

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

        viewed = {}
        # for itemID, rating in self.trainset.ur[user_iid]:
        #     viewed[itemID] = 1

        return candidates, viewed

    def get_recommendations(self, user_id, numOfRec):
        recommendations = []
        candidates, viewed = self.generateCandidates(user_id)
        user = User.objects.get(id =user_id )
        position = 0
        
        for itemID, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
            if not itemID in user.all_books.all():
                recommendations.append(self.trainset.to_raw_iid(itemID))
                position += 1
                if (position > numOfRec): 
                    break 

        return recommendations 

