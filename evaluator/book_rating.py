from collections import defaultdict
import pandas as pd
from surprise import Dataset, Reader
from bookclub.models import Rating, Book

class BookRatings:

    def __init__(self):
        self.user = Rating.objects.all()[0].user.id
        self.ratingObjs = Rating.objects.all()


    def load_dataset(self):

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

    def getPopularityRanks(self):
        ratings = defaultdict(int)
        rankings = defaultdict(int)
     
        for row in self.ratingObjs:
            bookID = row.book.id
            ratings[bookID] += 1
        rank = 1
        for bookID, ratingCount in sorted(ratings.items(), key=lambda x: x[1], reverse=True):
            rankings[bookID] = rank
            rank += 1
        return rankings

    def getBookName(self, bookID):
        try:
            return Book.objects.all().get(id=bookID).title
        except:
            return None

    def getTestUser(self):
        return self.user