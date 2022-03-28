from collections import Counter
from functools import reduce
import random
from bookclub.models import Book, Club, Rating, User
from .itemBasedModel import ItemBasedModel
from .contentBasedModel import ContentBasedModel


class Recommendation:
    def __init__(self, isItemBased, recHelper):
        if isItemBased:
            self.item_based = ItemBasedModel(recHelper)
        else:
            self.content_based = ContentBasedModel()

    # def train(self):
    #     self.item_based = ItemBasedModel()
    #     self.content_based = ContentBasedModel()

    def get_recommendations(self, request, num_of_rec, user_id=None, book_id=None, club_id=None):
        recommendations = []
        if book_id:
            recommendations = list(self.content_based.get_recommendations_for_book(user_id, book_id).keys())[:num_of_rec]
        
        elif club_id:
            recommendations = self.get_recommendations_for_club(request, num_of_rec, club_id)

        else:
            try:
                user = User.objects.get(id=user_id)
            except:
                user = request.user

            if Rating.objects.filter(user_id=user_id):
                recommendations = self.item_based.get_recommendations(user_id, num_of_rec)
                
            elif user.books.count() >= 1:
                recommendations = self.content_based.get_genre_recommendations(user_id)[:num_of_rec]

            else:
                books = Book.objects.all()
                return books.order_by('-average_rating','-readers_count')[:num_of_rec]    
            
        return self.get_books(recommendations)

    def get_recommendations_for_club(self, request, num_of_rec, club_id):
        club = Club.objects.get(id=club_id)
        members = club.members.all()
        books = club.books.all()

        recommendations =  []
        for mem in members:
            recommendations.append(self.get_recommendations(request, num_of_rec, mem.id))

        all_recommendations = reduce(lambda z, y :z + y, recommendations)
        filtered_rec = [book for book in all_recommendations if book not in books]
        random.shuffle(filtered_rec)
        counter = Counter(filtered_rec)
        counter_list = counter.most_common(num_of_rec)
        final_recommendations = [ seq[0].id for seq in counter_list ]
        return final_recommendations

    def get_books(self, recommendations):
        books = []
        for rec_id in recommendations:
            books.append(Book.objects.get(id=rec_id))
        
        return books

