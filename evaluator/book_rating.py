from collections import defaultdict
import csv
import os
import pandas as pd
from surprise import Dataset, Reader

class BookRatings:
    ratings_path = os.path.abspath('../book-review-dataset/ratings-evaluator.csv')
    books_path = os.path.abspath('../book-review-dataset/books.csv')
    
    def load_dataset(self):

        ratingsDataset = 0
        self.bookID_to_title = {}
        self.title_to_bookID = {}

        reader = Reader(line_format='user item rating ', sep=',', skip_lines=1, rating_scale=(0, 10))

        ratingsDataset = Dataset.load_from_file(self.ratings_path, reader=reader)

        with open(self.books_path, newline='', encoding='ISO-8859-1') as csvfile:
                bookReader = csv.reader(csvfile)
                next(bookReader)
                for row in bookReader:
                    bookID = int(row[7])
                    bookTitle = row[5]
                    self.bookID_to_title[bookID] = bookTitle
                    self.title_to_bookID[bookTitle] = bookID

        return ratingsDataset

    def getGenres(self):
        genres = defaultdict(list)
        genreIDs = {}
        maxGenreID = 0
        with open(self.books_path, newline='', encoding='ISO-8859-1') as csvfile:
            bookReader = csv.reader(csvfile)
            next(bookReader) 
            for row in bookReader:
                bookID = int(row[7])
                genreList = row[6].split(',')
                genreIDList = []
                for genre in genreList:
                    if genre in genreIDs:
                        genreID = genreIDs[genre]
                    else:
                        genreID = maxGenreID
                        genreIDs[genre] = genreID
                        maxGenreID += 1
                    genreIDList.append(genreID)
                genres[bookID] = genreIDList
        # Convert integer-encoded genre lists to bitfields that we can treat as vectors
        for (bookID, genreIDList) in genres.items():
            bitfield = [0] * maxGenreID
            for genreID in genreIDList:
                bitfield[genreID] = 1
            genres[bookID] = bitfield            
        
        return genres

    def getPopularityRanks(self):
        ratings = defaultdict(int)
        rankings = defaultdict(int)
        with open(self.ratings_path, newline='') as csvfile:
            ratingReader = csv.reader(csvfile)
            next(ratingReader)
            for row in ratingReader:
                bookID = int(row[1])
                ratings[bookID] += 1
        rank = 1
        for bookID, ratingCount in sorted(ratings.items(), key=lambda x: x[1], reverse=True):
            rankings[bookID] = rank
            rank += 1
        return rankings

    def getBookTitle(self, bookID):
        if bookID in self.bookID_to_title:
            return self.bookID_to_title[bookID]
        else:
            return ""

    def getTestUser(self):
        return self.user