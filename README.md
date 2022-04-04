# Team The Ordinaries Major Group project

## Team members
The members of the team are:
- Alaa Alkaabi 
- Duna Alghamdi 
- Galeah Moquim
- Hind Alhokair 
- Ina Borisova
- Rahaf AlMutairi 
- Reema Alsaif 
- Tala Alamri 

## Project structure
The project is called `system`.  It consists of a single app `bookclub`.

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

- If you faced any issues when installing surprise, refer to surprise library installation instructions in the documentation: https://github.com/NicolasHug/Surprise


Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:

```
$ python3 manage.py test
```

Run the application: 

```
$ python3 manage.py runserver 
``` 

If you encountered this error message when running the server or migrating the database: 
“ValueError: numpy.ndarray size changed, may indicate binary incompatibility. Expected 
96 from C header, got 88 from PyObject” 

write in the command line: 

```
$ pip3 install --upgrade numpy
```

## Sources
The packages used by this application are specified in `requirements.txt`

- sending emails + email verification: 
  - https://github.com/CryceTruly/django-tutorial-youtube
  - https://www.youtube.com/watch?v=Rbkc-0rqSw8 
- menuTester + follow and unfollow: Clucker training videos.
- chat room instant messages: https://github.com/tomitokko/django-chat-app
- evaluation tools: https://sundog-education.com/recsys/
- templates:
  - home page: https://getbootstrap.com/docs/5.1/examples/carousel/
  - book cards: https://codepen.io/dileepverma107/pen/rPqEbX
  - profile page: https://www.bootdey.com/snippets/view/bs4-vertical-user-profile-cover
