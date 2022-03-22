from collections import ChainMap, defaultdict
import math
from bookclub.models import Book, User


class ContentBasedModel:
    
    def get_recommendations_for_book(self, user_id, book_id):
        book = Book.objects.get(id=book_id)
        user = User.objects.get(id=user_id)
        books = user.all_books.all()
        all_books = Book.objects.all().exclude(id__in=books).exclude(id=book.id)

        genres = self.getGenres()
        similarity = {}    
        for b in all_books:
            num = self.computeGenreSimilarity(book.id, b.id, genres)
            if num > 0:
                similarity[b.id] = num

        sorted_similarity = dict(sorted(similarity.items(), reverse=True, key=lambda item: item[1]))
        return sorted_similarity

    def get_genre_recommendations(self, user_id):
        user = User.objects.get(id=user_id)
        books = user.books.all()

        similarity = []   
        for book in books:
            sim = self.get_recommendations_for_book(user_id, book.id)
            similarity.append(sim)
        
        similarity = ChainMap(*similarity)
        sorted_similarity = sorted(similarity, reverse=True, key=similarity.get)
        return sorted_similarity

    def computeGenreSimilarity(self, book1, book2, genres):
        genres1 = genres[book1]
        genres2 = genres[book2]
        sumxx, sumxy, sumyy = 0, 0, 0
        for i in range(len(genres1)):
            x = genres1[i]
            y = genres2[i]
            sumxx += x * x
            sumyy += y * y
            sumxy += x * y
        
        if sumxx*sumyy == 0:
            return 0

        return sumxy/math.sqrt(sumxx*sumyy)

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
        
        for (book_id, genreIDList) in genres.items():
            bitfield = [0] * maxGenreID
            for genreID in genreIDList:
                bitfield[genreID] = 1
            genres[book_id] = bitfield            
        
        return genres