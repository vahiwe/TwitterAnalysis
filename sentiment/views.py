import tweepy
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
import matplotlib.pyplot as plt
import numpy as np
from sentiment.config import *
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

        try:
            api.user_timeline(id=handle)
            report = "This username is available on Twitter"
        except tweepy.error.TweepError:
            report = "This username is not on Twitter"

        if report == "This username is not on Twitter":
            return redirect('/')

        start = request.POST['start']
        start = str(start)
        end = request.POST['end']
        end = str(end)
        timee = start + ' - ' + end

        t = np.arange(0.0, 2.0, 0.01)

        s = 1 + np.sin(2*np.pi*t)
        plt.plot(t, s)

        plt.xlabel('time (s)')
        plt.ylabel('voltage (mV)')
        plt.title('About as simple as it gets, folks')
        plt.grid(True)
        plt.savefig("static/test.png")
        filepath = "../static/test.png"
        graphs = True
        request.session['path'] = filepath
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
    path = request.session.get('path')
    return render(request, 'feedback.html', {'path': path})
