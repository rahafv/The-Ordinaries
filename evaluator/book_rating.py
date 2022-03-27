from collections import defaultdict
import csv
import os
import pandas as pd
from surprise import Dataset, Reader
from bookclub.models import Rating, Book

class BookRatings:


    def load_dataset(self):

        self.ratings_path = os.path.abspath("book-review-dataset/ratings-evaluator.csv")

        user_ids = []
        book_ids = []
        ratings = [] 
        
        with open(self.ratings_path, newline='', encoding='ISO-8859-1') as csvfile:
            ratingReader = csv.reader(csvfile)
            next(ratingReader)  #Skip header line
            for row in ratingReader:
                user_ids.append(row[0])
                book_ids.append(row[1])
                ratings.append(row[2])

        self.ratings_dict = {'userID': user_ids,
                        'bookID': book_ids,
                        'rating': ratings}

        df = pd.DataFrame.from_dict(self.ratings_dict)
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
        
        for row in self.ratings_dict['bookID']:
            bookID = row
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