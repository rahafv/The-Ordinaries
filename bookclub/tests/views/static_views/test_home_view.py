"""Tests of the Home view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import Rating, User , Club , Book
from bookclub.recommender.recommendation import Recommendation
from bookclub.tests.helpers import LogInTester, LoginRedirectTester, MenuTestMixin, NotificationsTester
from bookclub.recommender.SVDModel import SVDModel
from bookclub.helpers import rec_helper

class HomeViewTestCase(TestCase , LogInTester, LoginRedirectTester, MenuTestMixin, NotificationsTester):
    """Tests of the Home view."""

    fixtures = ['bookclub/tests/fixtures/default_user.json',
                'bookclub/tests/fixtures/default_club.json',
                'bookclub/tests/fixtures/other_users.json',
                'bookclub/tests/fixtures/other_club.json',
                'bookclub/tests/fixtures/default_book.json',
                 'bookclub/tests/fixtures/other_books.json',
                'bookclub/tests/fixtures/default_meeting.json',
                'bookclub/tests/fixtures/default_rating.json',
                 'bookclub/tests/fixtures/other_ratings.json']

    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.get(id=1)
        self.second_user = User.objects.get(id=2)
        
        SVDModel(rec_helper).train(rec_helper)

        self.first_club = Club.objects.get(id=1)
        self.second_club = Club.objects.get(id=2)

        self.first_book = Book.objects.get(id=1)

    def test_home_url(self):
        self.assertEqual(self.url,'/')

    def test_get_home(self):
        self.client.login(username=self.user.username, password='Password123')
        self.user.add_book_to_all_books(self.first_book)
        self.create_test_books()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/home.html')
        self.assert_menu(response)
    
    def test_feed_contains_events_by_self_and_followees(self):
        self.client.login(username=self.user.username, password='Password123')
        self.user.toggle_follow(self.second_user)
        self.sendNotification(self.user, self.user, self.first_club)
        self.sendNotification(self.second_user, self.user, self.first_club)
        response = self.client.get(self.url)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.second_user.username)
        self.assert_menu(response)

    def test_updates_contains_events_related_to_clubs_user_is_member_in(self):
        self.client.login(username=self.user.username, password='Password123')
        self.user.toggle_follow(self.second_user)
        self.second_user.toggle_follow(self.user)
        self.sendNotification(self.user, self.user, self.first_club)
        response = self.client.get(self.url)
        self.assertContains(response, "test club")
        self.assertContains(response, "test user")
        self.assertContains(response, self.user.username)
        self.assert_menu(response)

    def test_home_recommendation(self):
        self.client.login(username=self.user.username, password='Password123')
        self.create_test_users()
        response = self.client.get(self.url)
        Recommendation(True, rec_helper).get_recommendations(response.wsgi_request, 1, user_id=self.user.id)

    def test_home_recommendation_with_invalid_user_id(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        Recommendation(True, rec_helper).get_recommendations(response.wsgi_request, 1)
        
    def create_test_users(self, user_count=11):
        for user_id in range(user_count):
            User.objects.create(
                first_name = f'first{user_id}', 
                last_name = f'last{user_id}', 
                username=f'firstlast{user_id}',
                email = f'firstlast{user_id}@example.org', 
                email_verified = True, 
                city = "london",
                country = "uk"
            )

    def create_test_books(self, book_count=6):
        isbn_num = ['0425176428', '0060973129','0374157065', '0393045218', '0399135782','034545104X'
                    ,'155061224','446520802', '380000059','380711524']
        ctr = 0
        for book_id in range(book_count):
            book = Book.objects.create(
                ISBN = isbn_num[ctr],
                title = f'book{book_id} title',
                author = f'book{book_id} author',
                genre = "Classics,European Literature,Czech Literature"
            )

            Rating.objects.create(
                user=self.second_user,
                book = book,
                rating = 5
            )
            ctr+=1


        




