# IMPORT
from utils.log import *
from utils.req import *
from utils.printJSON import *

import os
from dotenv import load_dotenv
import base64
import logging
import requests
import json
import string
import random
import webbrowser
import time
from datetime import datetime, timedelta
from random import randrange

# VARIABLES
load_dotenv()

# SETUP LOGGING
create_log()

# CONFIG THis is where you configure what data to create

# Number of test users to create
numUsers = 1
# email format
emailDomain = "isv.domain.com"
# userType 1 for basic 2 for licensed
userType = 2
# duration in Minutes for meeting launched and recorded
meetingDuration = 5
# buffer between each launched and recorded meeting in seconds
buffer = 10
# boolean to create upcoming meetings
upcomingMeetings = False
# number of upcoming meetings to create
numMeetings = 1
# Boolean to create Webinar (requires webinar licenses)
webinars = False
# number of upcoming webinars to create
numWebinars = 2
# boolean to add registration to upcoming meetings and webinars
registration = False
# number of registrants to add to meetings And  Webinars
numRegistrants = 4

# PROBABLY don't change anything below this line
# Or do. I'm a comment not a cop.

# Create User


def create_user():
    emailAddress = generateEmail(16)
    logging.info("Creating User: %s" % emailAddress)
    url = '/users'
    data = {"action": "custCreate", "user_info": {
        "email": emailAddress, "type": userType}}
    action = 'post'
    response = send_request(action, url, data)
    return emailAddress

# Create Meeting


def create_meeting(emailAddress):
    logging.info("Creating Meeting")
    url = '/users/%s/meetings' % emailAddress
    data = {"topic": "test meeting",
            "password": "1234",
            "settings": {
                "auto_recording": "cloud",
                "join_before_host": True}}
    action = 'post'
    response = send_request(action, url, data)
    data = json.loads(response)
    meetingID = data['id']
    startURL = data['start_url']
    print("created meeting: %s" % meetingID)
    return startURL, meetingID

# Create Upcoming Meeting


def create_upcoming_meetings(emailAddress):
    url = "/users/%s/meetings" % emailAddress
    action = 'post'
    meetings = 0
    while meetings < numMeetings:
        randomNumber = randrange(14)
        now = datetime.now()
        upcomingDate = now + timedelta(days=randomNumber)
        schedule = upcomingDate.strftime("%Y-%M-%dT%H:%m:%SZ")
        if registration == True:
            logging.info("Creating Upcoming meeting/s with registration")
            data = {"topic": "test meeting",
                    "password": "1234",
                    "start_time": schedule,
                    "duration": 60,
                    "settings": {
                        "auto_recording": "cloud",
                        "join_before_host": True,
                        "approval_type": 0}}
        else:
            logging.info("Creating Upcoming meeting/s without Registration")
            data = {"topic": "test meeting",
                    "password": "1234",
                    "start_time": schedule,
                    "duration": 60,
                    "settings": {
                        "auto_recording": "cloud",
                        "join_before_host": True}}
        response = send_request(action, url, data)
        data = json.loads(response)
        meetingID = data['id']
        startURL = data['start_url']
        print("Created upcoming meeting: %s") % meetingID
        if numRegistrants > 0:
            registrant = 0
            while registrant < numRegistrants:
                add_meeting_registrant(meetingID)
                registrant += 1
            meetings += 1

# Add Meeting Registrant


def add_meeting_registrant(meetingID):
    logging.info("Adding Registrant")
    url = "/meetings/%s/registrants" % meetingID
    data = {"first_name": generate_name(8), "last_name": generate_name(8),
            "email": generateEmail(16)}
    action = 'post'
    response = send_request(action, url.data)
    data = json.loads(response)
    registrantID = data['registrant_id']
    print("added registrant: %s to meetingID: %s" % (registrantID, meetingID))
# Add webinar Registrant


def add_webinar_registrant(webinarID):
    logging.info("Adding Registrant")
    url = "/webinars/%s/registrants" % webinarID
    data = {"first_name": generate_name(8), "last_name": generate_name(8),
            "email": generateEmail(16)}
    action = 'post'
    response = send_request(action, url.data)
    data = json.loads(response)
    registrantID = data['registrant_id']
    print("added registrant: %s to webinarID: %s" % (registrantID, webinarID))

# End Meeting


def end_meeting(meetingID):
    logging.info("Ending Meeting : %s" % meetingID)
    url = '/meetings/%s/status' % meetingID
    data = {"action": "end"}
    action = 'put'
    response = send_request(action, url, data)
    print("Ended Meeting: %s") % meetingID

# Add Webinar License


def add_webinar_license(emailAddress):
    print("add webinar license to user: %s" % emailAddress)
    url = '/users/%s/settings' % emailAddress
    data = {"feature": {"webinar": True,
                        "webinar_capacity": 500}}
    action = 'patch'
    response = send_request(action, url, data)

# Create Webinar


def create_webinar(emailAddress):
    print("create webinar")
    url = "/users/%s/webinars" % emailAddress
    action = 'post'
    webinars = 0
    while webinars < numWebinars:
        randomNumber = randrange(14)
        now = datetime.now()
        upcomingDate = now + timedelta(days=randomNumber)
        schedule = upcomingDate.strftime("%Y-%M-%dT%H:%m:%SZ")
        logging.info("Creating Upcoming webinar/s with Registration")
        data = {"topic": "test meeting",
                "password": "1234",
                "start_time": schedule,
                "duration": 60,
                "settings": {
                    "auto_recording": "cloud",
                    "join_before_host": True,
                    "approval_type": 0}}
        response = send_request(action, url, data)
        data = json.loads(response)
        webinarID = data['id']
        print("created upcoming webinar: %s" % webinarID)
        if numRegistrants > 0:
            registrant = 0
            while registrant < numRegistrants:
                add_webinar_registrant(webinarID, token)
                registrant += 1
        webinars += 1

# Generate Email


def generateEmail(N):
    userString = ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(N))
    userEmail = userString+"@"+emailDomain
    logging.info("Create email address : %s" % userEmail)
    return userEmail

# Generate Name


def generate_name(N):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(N))


# Generate Data
def generate_data():
    u = 0
    while u < numUsers:
        emailAddress = create_user()
        time.sleep(1)
        data = create_meeting(emailAddress)
        time.sleep(1)
        meetingID = data[1]
        # launch Meeting in Client
        print("Starting Meeting: %s" % meetingID)
        startURL = data[0]
        webbrowser.open_new(startURL)
        # wait to end meeting until buffer
        seconds = meetingDuration * 60
        time.sleep(seconds)
        # end the meeting
        end_meeting(meetingID)
        time.sleep(buffer)
        if upcomingMeetings:
            create_upcoming_meetings(emailAddress)
        if webinars:
            add_webinar_license(emailAddress)
            time.sleep(2)
            create_webinar(emailAddress)
        u += 1


generate_data()
