from bookclub.models import User

class RecommenderHelper:
    
    def __init__(self):
        self.trainset = None
        self.similarity_matrix = None
        self.counter = 0  
        self.limit = User.objects.count()/10

    def set_trainset(self, trainset):
        self.trainset = trainset 

    def set_similarity_matrix(self , similarity_matrix):
        self.similarity_matrix = similarity_matrix
    
    def increment_counter(self):
        self.counter += 1

    def reset_counter(self):
        self.counter = 0

    def get_limit(self):
        return self.limit



