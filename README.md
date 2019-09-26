This project is a webapp that runs a sentiment analysis on tweets of a Twitter handle and gives feedback on sentiments over a period of time.

## :page_with_curl:  _Instructions_

**1)** Fire up your favourite console & clone this repo somewhere:

__`❍ git clone https://github.com/vahiwe/TwitterAnalysis.git`__

**2)** Enter this directory:

__`❍ cd TwitterAnalysis`__

**3)** Install [python](https://www.python.org/) if not already installed and install other python packages/dependencies using the requirement file:

__`❍ pip3 install -r requirements.txt `__

**4)** Run to create migrations for changes:

__`❍ python manage.py makemigrations`__

**5)** Run to apply those changes to the database:

__`❍ python manage.py migrate`__

**6)** Start the server to view the webapp:

__`❍ python manage.py runserver `__

**7)** Open your browser and type in this URL to view the webapp:

__`❍ http://127.0.0.1:8000/`__

__*Happy developing!*__
