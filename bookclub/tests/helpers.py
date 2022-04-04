from django.urls import reverse
from django.contrib.messages import ERROR, SUCCESS, WARNING, INFO
from with_asserts.mixin import AssertHTMLMixin
from notifications.signals import notify

from bookclub.models import Book, Club, Rating, User

def reverse_with_next(url_name, next_url):
    url = reverse(url_name)
    url += f"?next={next_url}"
    return url

class LogInTester:
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()

class LoginRedirectTester:
    def assert_redirects_when_not_logged_in(self):
        target_url = reverse_with_next("log_in", self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response, target_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "authentication_templates/log_in.html")

    def assert_post_redirects_when_not_logged_in(self):
        target_url = reverse_with_next("log_in", self.url)
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(
            response, target_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "authentication_templates/log_in.html")

class MessageTester:
    def assert_error_message(self, response):
        messages = tuple(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, ERROR)

    def assert_success_message(self, response):
        messages = tuple(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, SUCCESS)

    def assert_warning_message(self, response):
        messages = tuple(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, WARNING)

    def assert_info_message(self, response):
        messages = tuple(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, INFO)

    def assert_no_message(self, response):
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0) 

class MenuTestMixin(AssertHTMLMixin):
    menu_urls = [
      reverse('password') ,
      reverse('profile') ,
      reverse('books_list') , 
      reverse('clubs_list'),
      reverse('chat_room'),
      reverse('log_out')
      ]

    def assert_menu(self,response):
        for url in self.menu_urls:
            self.assertHTML(response , f'a[href="{url}"]')

    def assert_no_menu(self , response):
        for url in self.menu_urls:
            self.assertNotHTML(response , f'a[href="{url}"]')

class NotificationsTester: 
    def sendNotification(self, userActor, receptient_user, clubActor): 
        notify.send(userActor, recipient=receptient_user, verb= "test user", description='user-event')      
        notify.send(clubActor, recipient=receptient_user, verb= "test club", action_object=userActor, description='club-event-U')

class ObjectsCreator:
    def create_test_ratings(self, user, book_count=6):
        isbn_num = ['0425176428', '0060973129','0374157065', '0393045218', '0399135782','034545104X'
            ,'155061224','446520802','052165615X','521795028', '2080674722','3257224281','600570967','038550120X',
            '342310538', '425115801','449006522','553561618', '055356451X','786013990','786014512','60517794','451192001','609801279',
            '671537458','679776818','943066433','1570231028','1885408226','747558167','3442437407','033390804X','3596218098','684867621',
            '451166892','8440682697','034544003X','380000059','380711524']

        ctr = 0
        for book_id in range(book_count):
            book = Book.objects.create(
                ISBN = isbn_num[ctr],
                title = f'book{book_id} title',
                author = f'book{book_id} author',
                genre = f'genre {book_id}'
            )

            Rating.objects.create(
                user=user,
                book = book,
                rating = 5
            )
            ctr+=1

    def create_test_books(self, book_count=6, genre=None):
        isbn_num = ['0425176428', '0060973129','0374157065', '0393045218', '0399135782','034545104X'
            ,'155061224','446520802','052165615X','521795028', '2080674722','3257224281','600570967','038550120X',
            '342310538', '425115801','449006522','553561618', '055356451X','786013990','786014512','60517794','451192001','609801279',
            '671537458','679776818','943066433','1570231028','1885408226','747558167','3442437407','033390804X','3596218098','684867621',
            '451166892','8440682697','034544003X','380000059','380711524']

        ctr = 0
        for book_id in range(book_count):
            if not genre:
                Book.objects.create(
                    ISBN = isbn_num[ctr],
                    title = f'book{book_id} title',
                    author = f'book{book_id} author',
                    genre = f'genre {book_id}'
                )
            
            else:
                Book.objects.create(
                    ISBN = isbn_num[ctr],
                    title = f'book{book_id} title',
                    author = f'book{book_id} author',
                    genre = genre
                )
            ctr+=1

    def create_test_search_books(self, book_count=6):
        isbn_num = ['0425176428', '0060973129','0374157065', '0393045218', '0399135782','034545104X'
            ,'155061224','446520802','052165615X','521795028', '2080674722','3257224281','600570967','038550120X',
            '342310538', '425115801','449006522','553561618', '055356451X','786013990','786014512','60517794','451192001','609801279',
            '671537458','679776818','943066433','1570231028','1885408226','747558167','3442437407','033390804X','3596218098','684867621',
            '451166892','8440682697','034544003X','380000059','380711524']

        for book_id in range(book_count):
            if book_id < 3: 
                title = 'uio'
                author = 'James'
                genre = 'fiction'
            else: 
                title = 'xyz'
                author = 'joe'
                genre = 'non fiction'

            Book.objects.create(
                ISBN = isbn_num[book_id],
                title = title,
                author = author, 
                genre = genre
            )

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

    def create_test_search_users(self, user_count=6):
        for user_id in range(user_count):
            if user_id < 3: 
                first_name = "joe"
                country = "uk"
            else: 
                first_name = "jane"
                country= "USA"

            User.objects.create(
                first_name = first_name,
                last_name = f'last{user_id}', 
                username=f'{first_name}last{user_id}',
                email = f'{first_name}last{user_id}@example.org', 
                email_verified = True, 
                city = "london",
                country = country
            )

    def create_test_clubs(self, club_count=10):
        for club_id in range(club_count):
            Club.objects.create(owner = self.user,
                name =f'club{club_id}',
                theme=f'theme{club_id}',
                city=f'city{club_id}',
                country=f'country {club_id}',
            )
    
    def create_test_search_clubs(self, club_count=6):
        for club_id in range(club_count):
            if club_id < 3: 
                name = "The"
                country = "uk"
            else: 
                name = "american"
                country = "usa"

            Club.objects.create(owner = self.user,
                name =f'{name}{club_id}',
                theme=f'theme{club_id}',
                meeting_type =Club.MeetingType.INPERSON,
                city=f'city{club_id}',
                country=country,
            )
