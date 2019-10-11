This project is a webapp that runs a sentiment analysis on tweets of a Twitter handle and gives feedback on sentiments over a period of time.

## :page_with_curl:  _Instructions_

**1)** Fire up your favourite console & clone this repo somewhere:

__`❍ git clone https://github.com/vahiwe/TwitterAnalysis.git`__

**2)** Enter this directory:

__`❍ cd TwitterAnalysis/model_setup`__

**3)** Install [python](https://www.python.org/) if not already installed and run this command to install python packages/dependencies:

__`❍ pip install -e . `__

**4)** Go back to previous directory:

__`❍ cd .. `__

**5)** Generate secret key for Django project [here](https://miniwebtool.com/django-secret-key-generator/) and input in `TwitterAnalysis/config.py` :

``` 
    KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

**6)** Get your [Twitter Developer](https://developer.twitter.com/) credentials and input in `sentiment/config.py` :
```
    consumer_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' 
    consumer_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    access_token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' 
    access_token_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' 
```

**7)** Install spacy language model:

__`❍ python -m spacy download en `__

**8)** Run to create migrations for changes:

__`❍ python manage.py makemigrations`__

**9)** Run to apply those changes to the database:

__`❍ python manage.py migrate`__

**10)** Start the server to view the webapp:

__`❍ python manage.py runserver `__

**11)** Open your browser and type in this URL to view the webapp:

__`❍ http://127.0.0.1:8000/`__

__*Happy developing!*__
