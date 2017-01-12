from __future__ import print_function

import requests
import os

SERVER_URL = os.environ.get('SERVER_URL')

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "Sonos",
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Sonos. " \
                    "You can use me to control the Sonos sytem in your house. " \
                    "Start playing on a player, stop the music, or search for new things to play, " \
                    "all with your voice."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Thanks for playing."
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def play_anything(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True

    location = None
    if 'Location' in intent['slots']:
        location = intent['slots']['Location'].get('value')

    req = requests.get("{0}/play?location={1}".format(SERVER_URL, location))
    if req.status_code != requests.codes.ok:
        speech_output = "Sorry, I could not connect to sonos to start playing"
        reprompt_text = "I couldnt connect to your sonos. You can try again."
    else:
        speech_output = "Playing"
        reprompt_text = "You can ask me to stop playing."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def play_something(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = True

    location = None
    speech_output = None
    search_term = None
    artist = None
    song = None

    if 'Location' in intent['slots']:
        location = intent['slots']['Location'].get('value')

    if 'WhatToPlay' in intent['slots'] and intent['slots']['WhatToPlay'].get('value') != None:
        search_term = intent['slots']['WhatToPlay']['value']
    else:
        artist = intent['slots']['Artist'].get('value')
        song = intent['slots']['Song'].get('value')

    req = requests.get("{0}/search?query={1}&location={2}&song={3}&artist={4}".format(SERVER_URL, search_term, location, song, artist))
    if req.status_code != requests.codes.ok:
        speech_output = "Sorry, I could not find what you wanted."
    else:
        speech_output = "I will try to play " + \
                        search_term

    reprompt_text = "Try something else?"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def stop_playing(intent, session):
    session_attributes = {}
    reprompt_text = None
    location = None
    if 'Location' in intent['slots']:
        location = intent['slots']['Location'].get('value')
    req = requests.get("{0}/pause?location={1}".format(SERVER_URL, location))
    if req.status_code != requests.codes.ok:
        speech_output = "Sorry, I could not stop the music"
    else:
        speech_output = ""
    should_end_session = True

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def next_song(intent, session):
    session_attributes = {}
    reprompt_text = None
    location = None
    speech_output = None
    should_end_session = True

    if 'Location' in intent['slots']:
        location = intent['slots']['Location'].get('value')
    req = requests.get("{0}/next?location={1}".format(SERVER_URL, location))

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def previous_song(intent, session):
    session_attributes = {}
    reprompt_text = None
    location = None
    speech_output = None
    should_end_session = True

    if 'Location' in intent['slots']:
        location = intent['slots']['Location'].get('value')
    req = requests.get("{0}/previous?location={1}".format(SERVER_URL, location))

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def volume_adjust(intent, session):
    session_attributes = {}
    reprompt_text = None
    location = None
    speech_output = None
    should_end_session = True

    if 'Location' in intent['slots']:
        location = intent['slots']['Location'].get('value')

    if 'Volume' in intent['slots']:
        volumeup = intent['slots']['Volume'].get('value') == "up"
        req = requests.get("{0}/volume?location={1}&up={2}".format(SERVER_URL, location, volumeup))

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "PlayAnything" or intent_name == "AMAZON.ResumeIntent":
        return play_anything(intent, session)
    elif intent_name == "PlaySomething":
        return play_something(intent, session)
    elif intent_name == "StopPlaying" or intent_name == "AMAZON.StopIntent":
        return stop_playing(intent, session)
    elif intent_name == "AMAZON.NextIntent":
        return next_song(intent, session)
    elif intent_name == "AMAZON.PreviousIntent":
        return previous_song(intent, session)
    elif intent_name == "AdjustVolume":
        return volume_adjust(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent":
        raise ValueError("Invalid intent")
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
