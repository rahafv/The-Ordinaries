from datetime import timedelta
from threading import Timer
import pandas as pd
from bookclub.models import Rating, User
from surprise import Dataset, SVD, Reader

from collections import defaultdict
from operator import itemgetter
import heapq


class SVDModel:
    def __init__(self, recHelper):
        self.trainset = recHelper.trainset
        self.similarity_matrix = recHelper.similarity_matrix

        if recHelper.counter == 0:
            if self.trainset == None:
                self.train(recHelper)
            else:
                print("here")
                startTime = timedelta(0.00001157).total_seconds()
                Timer(startTime, self.train, [recHelper]).start()
                
            recHelper.increment_counter()   

    def train(self, recHelper):
        self.trainset = self.load_dataset().build_full_trainset()
        recHelper.set_trainset(self.trainset)

        self.similarity_matrix = SVD().fit(self.trainset).compute_similarities()
        recHelper.set_similarity_matrix(self.similarity_matrix)         

    def load_dataset(self):
        
        self.ratingObjs = Rating.objects.all()
        user_ids = []
        book_ids = []
        ratings = [] 

        for rating in self.ratingObjs:
            user_ids.append(rating.user.id)
            book_ids.append(rating.book.id)
            ratings.append(rating.rating)

        ratings_dict = {'userID': user_ids,
                        'bookID': book_ids,
                        'rating': ratings}

        df = pd.DataFrame.from_dict(ratings_dict)
        reader = Reader(rating_scale = (0, 10))
        data = Dataset.load_from_df(df[['userID', 'bookID', 'rating']], reader)
        
        return data

    def generateCandidates(self, user_id, k=20):
        

        user_iid = self.trainset.to_inner_uid(user_id)
        user_ratings = self.trainset.ur[user_iid]
        k_neighbors = heapq.nlargest(k, user_ratings, key=lambda t: t[1])

        candidates = defaultdict(float)
        for itemID, rating in k_neighbors:
            try:
                similaritities = self.similarity_matrix[itemID]
                for innerID, score in enumerate(similaritities):
                    candidates[innerID] += score
            except:
                continue

        return candidates

    def get_recommendations(self, user_id, num_of_rec):
        recommendations = []
        candidates = self.generateCandidates(user_id)
        user = User.objects.get(id =user_id )
        position = 0
        
        for itemID, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
            
            id = self.trainset.to_raw_iid(itemID)
            if not user.all_books.filter(id=id).exists():
                recommendations.append(id)
                position += 1
                if (position >= num_of_rec): 
                    break 

        return recommendations 

