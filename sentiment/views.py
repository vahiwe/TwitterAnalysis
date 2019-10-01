import re
import sys
import nltk
import spacy
import string
import tweepy
import datetime
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sentiment.config import *
from spacy.lang.en import English
from sklearn.externals import joblib
from sklearn.pipeline import Pipeline
from sklearn.base import TransformerMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from spacy.lang.en.stop_words import STOP_WORDS
from django.shortcuts import render, get_object_or_404, redirect
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
# Use seaborn style defaults and set the default figure size
sns.set(rc={'figure.figsize': (11, 8)})
# Create your views here.


def home(request):
    if request.method == 'POST':
        # You need to insert your own developer twitter credentials here
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        handle = request.POST['handle']
        handle = str(handle)
        request.session['user'] = handle

        if len(handle) == 0:
            report = "Please input a username"
        else:
            try:
                api.user_timeline(id=handle)
                report = "This username is available on Twitter"
            except tweepy.error.TweepError:
                report = "This username is not on Twitter"

        if report == "This username is available on Twitter":
            request.session['user'] = handle
            return redirect('analysis/')
        else:
            return render(request, 'home.html', {'report': report})
    return render(request, 'home.html', {'report': ''})


def analysis(request):
    previous_url = request.META.get('HTTP_REFERER')
    if previous_url == None:
        return redirect('/')
    if request.method == 'POST':
        # You need to insert your own developer twitter credentials here
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        handle = request.POST['handle']
        handle = str(handle)
        start = request.POST['start']
        start = str(start)
        end = request.POST['end']
        end = str(end)
        date_since_obj = datetime.datetime.strptime(start, '%Y-%m-%d')
        date_after_obj = datetime.datetime.strptime(end, '%Y-%m-%d')

        tweets = tweepy.Cursor(api.user_timeline, id=handle, lang='en',
                               tweet_mode='extended', since='', until='').items(200)

        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0x0020)
        dates = []
        test = []
        likes = []
        retweets = []
        for tweet in tweets:
            if tweet.created_at < date_after_obj and tweet.created_at > date_since_obj:
                date = tweet.created_at
                date = date.strftime("%Y-%m-%d")
                like = tweet.favorite_count
                retweet = tweet.retweet_count
                status = tweet
                if 'extended_tweet' in status._json:
                    status_json = status._json['extended_tweet']['full_text']
                elif 'retweeted_status' in status._json and 'extended_tweet' in status._json['retweeted_status']:
                    status_json = status._json['retweeted_status']['extended_tweet']['full_text']
                    like = status._json["retweeted_status"]["favorite_count"]
                elif 'retweeted_status' in status._json:
                    status_json = status._json['retweeted_status']['full_text']
                    like = status._json["retweeted_status"]["favorite_count"]
                else:
                    status_json = status._json['full_text']
                test.append(status_json.translate(non_bmp_map))
                likes.append(like)
                retweets.append(retweet)
                dates.append(date)

        df = pd.DataFrame(list(zip(test, dates, likes, retweets)), columns=[
                          "tweets", "dates", "likes", "retweets"])
        df['dates'] = pd.to_datetime(df['dates'], format='%Y-%m-%d')
        df.set_index(['dates'], inplace=True)
        df.sort_index(inplace=True)
        # remove twitter handles (@user)
        df['tidy_tweet'] = np.vectorize(remove_pattern)(df['tweets'], "@[\w]*")
        # remove url patterns
        df['tidy_tweet'] = np.vectorize(remove_pattern)(
            df['tidy_tweet'], "http[s]?://\S+")
        # remove 'RT', '#', newline escape character '\n' and trailing whitespaces
        df['tidy_tweet'] = df['tidy_tweet'].str.replace("RT", " ")
        df['tidy_tweet'] = df['tidy_tweet'].str.replace("#", " ")
        df['tidy_tweet'] = df['tidy_tweet'].str.replace("\n", " ")
        df['tidy_tweet'] = np.vectorize(
            remove_pattern)(df['tidy_tweet'], "\s\s+")
        # replace empty strings with NaN
        df['tidy_tweet'].replace('', np.nan, inplace=True)
        # remove rows with NaN in tidy tweet column
        df = df.dropna(subset=['tidy_tweet'])

        # Load model
        sent = open('model_setup/model.pkl', 'rb')
        clf = joblib.load(sent)

        # predict
        predicted = clf.predict(df['tidy_tweet'])
        df['mood'] = predicted

        # this changes the labels of the prediction
        df['mood'] = df['mood'].map({4: 1, 0: -1, 2: 0})

        neutral_percentage = (len(df[df['mood'] == 0]) / len(df['mood'])) * 100
        negative_percentage = (
            len(df[df['mood'] == -1]) / len(df['mood'])) * 100
        positive_percentage = (
            len(df[df['mood'] == 1]) / len(df['mood'])) * 100

        labels = ['neutral', 'negative', 'positive']
        sizes = [neutral_percentage, negative_percentage, positive_percentage]
        moodto = dict(zip(labels, sizes))
        moodsort = sorted(moodto.items(), key=lambda x: x[1], reverse=True)

        # Piechart
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=False)
        ax1.axis('equal')
        plt.savefig('static/piechart.png', bbox_inches='tight')

        # Specify the data columns we want to include
        data_columns = ['mood']
        # Resample to daily frequency, aggregating with mean
        mood_daily_mean = df[data_columns].resample('D').mean()
        # graph for daily
        ax = mood_daily_mean.plot(
            ylim=(-0.5, 0.5), title='Mood on different days')
        # set labels for both axes
        ax.set(xlabel='Days', ylabel='Mood')
        a = ['', 'Very Negative', 'Negative',
             'Neutral', 'Positive', 'Very Positive', '']
        ax.set_yticklabels(a)
        plt.savefig("static/daygraph.png", bbox_inches='tight')

        # highest retweet and like
        high_retweet = df.loc[df['retweets'] ==
                              df['retweets'].max()]['tweets'][0]
        high_like = df.loc[df['likes'] == df['likes'].max()]['tweets'][0]

        request.session['pie'] = "../static/piechart.png"
        request.session['daily'] = "../static/daygraph.png"
        request.session['highretweets'] = high_retweet
        request.session['highlikes'] = high_like
        return redirect('/feedback')
    user = request.session.get('user')
    return render(request, 'analysis.html', {'report': '', 'user': user, 'start': '', 'end': ''})


def feedback(request):
    previous_url = request.META.get('HTTP_REFERER')
    if previous_url == None:
        return redirect('/')
    if request.method == 'POST':
        message = request.POST['message']
        message = str(message)
        feedback = open("static/feedback.txt", "a+")
        feedback.write(message+"\n\n")
        feedback.close()
        return redirect('/')
    piechart = request.session.get('pie')
    dailygraph = request.session.get('daily')
    high_retweet = request.session.get('highretweets')
    high_like = request.session.get('highlikes')
    return render(request, 'feedback.html', {'piechart': piechart, 'dailygraph': dailygraph, 'high_retweet': high_retweet, 'high_like': high_like})


def remove_pattern(input_txt, pattern):
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)

    return input_txt
