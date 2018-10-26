from __future__ import print_function
import random
import urllib2
import json


SKILL_NAME = 'Feelings with Ziggy'
API_BASE = 'http://feelingswithziggythezebra-env.us-east-1.elasticbeanstalk.com/api.php'
GAME_TOTAL_QUESTIONS = 28
GAME_TOTAL_INSTRUCTIONS = 4
GAME_SPECIAL_INSTRUCTION_IDS = [3] #ids of instructions not full instructions

GAME_ACTING_MODES_LANGUAGE = ['acting', 'actin', 'act' ]
GAME_DRAWING_MODES_LANGUAGE = ['drawing', 'draw', 'drawin']

GAME_SET_MODE_INSTRUCTION_AUDIO_URL = 'https://s3.amazonaws.com/feelingswithziggythezebra/game_special_instructions/draw-or-act.mp3'
GAME_EXTRA_TIME_INSTRUCTION_AUDIO_URL = 'https://s3.amazonaws.com/feelingswithziggythezebra/game_special_instructions/extra-time.mp3'
GAME_PROMPT_NEXT_QUESTION_AUDIO_URL = 'https://s3.amazonaws.com/feelingswithziggythezebra/game_special_instructions/extra-time.mp3'
GAME_PROMPT_NEXT_QUESTION_DRAWING_AUDIO_URL = 'https://s3.amazonaws.com/feelingswithziggythezebra/game_special_instructions/reprompt-instruction-drawing.mp3'
GAME_PROMPT_NEXT_QUESTION_ACTING_AUDIO_URL = 'https://s3.amazonaws.com/feelingswithziggythezebra/game_special_instructions/reprompt-instruction-acting.mp3'
WAIT_MUSIC_ACTING_AUDIO_URL = 'https://s3.amazonaws.com/feelingswithziggythezebra/game_timing_music/acting_music.mp3'
WAIT_MUSIC_DRAWING_AUDIO_URL = 'https://s3.amazonaws.com/feelingswithziggythezebra/game_timing_music/drawing_music.mp3'
#SESSION ATTRIBUTES
# appState   0, welcom response - 1, start game - 2, set_drawing - 3 - asking quesions 
# gameCurrentQuestion
# gameQuestionsAsked
# gameIsActing


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, text_output, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': text_output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_speechlet_response_ssml(title, text_output, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'card': {
            'type': 'Simple',
            'title':  title,
            'content': text_output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': reprompt_text
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
    session_attributes = set_session_variables(0, 1, [], -1)
    card_title = "Welcome"
    speech_output = 'Welcome to '+SKILL_NAME+'. To play the feelings game with Ziggy, everyone\'s favorite Zebra, you can say "play game".'
    reprompt_text = 'To play the feelings game with Ziggy, you can say, "play game".'
    text_output = speech_output
    should_end_session = False
    return build_response(session_attributes,  build_speechlet_response(card_title, text_output, speech_output, reprompt_text, should_end_session))


def start_feelings_game(intent, session):
    should_end_session = False
    card_title = "The Feelings Game"

    if session.get('attributes', {}) and "appState" in session.get('attributes', {}):
        if(session['attributes']['appState'] == 0):
            instruction_id = random.choice([x for x in range(1, GAME_TOTAL_INSTRUCTIONS+1) if x not in GAME_SPECIAL_INSTRUCTION_IDS])
            instruction_id = 2 #commment out
            instruction_query_result = api_request('game_instructions?transform=1&filter=id,eq,'+str(instruction_id))
        else:  
            instruction_query_result = api_request('game_instructions?transform=1&filter=id,eq,3')  
    else:
        instruction_id = random.choice([x for x in range(1, GAME_TOTAL_INSTRUCTIONS+1) if x not in GAME_SPECIAL_INSTRUCTION_IDS])
        instruction_query_result = api_request('game_instructions?transform=1&filter=id,eq,'+str(instruction_id))

    session_attributes = set_session_variables(1, 1, [], -1)

    #generating question response output
    speech_output = get_audio_ssml_speech(instruction_query_result['game_instructions'][0]['audio_url'])
    text_output = instruction_query_result['game_instructions'][0]['text']
    reprompt_text = get_audio_ssml_speech(GAME_PROMPT_NEXT_QUESTION_AUDIO_URL)
    speechlet_response = build_speechlet_response_ssml(card_title, text_output, speech_output, reprompt_text, should_end_session)

    
    return build_response(session_attributes, speechlet_response)

def set_draw_or_act_settings(intent, session):
    if session.get('attributes', {}) and "appState" in session.get('attributes', {}):
        if(session['attributes']['appState'] != 1):
            return get_help_response(intent, session)

    should_end_session = False
    card_title = "Set Game Mode"
    game_mode_value = None
    reprompt_text = None
    text_output = 'If you are acting say "Act". Or if you are drawing say "Draw".'
    if 'GameMode' in intent['slots']:
        gamemode = intent['slots']['GameMode']['value']
        if(gamemode in GAME_ACTING_MODES_LANGUAGE):
            game_mode_value = 1
            speech_output = get_audio_ssml_speech(GAME_PROMPT_NEXT_QUESTION_ACTING_AUDIO_URL)
            text_output = 'Your game mode is acting! Let\'s start! To get a question say \'Go\' or \'Go Ziggy\'!'
        elif (gamemode in GAME_DRAWING_MODES_LANGUAGE):
            game_mode_value = 0
            speech_output = get_audio_ssml_speech(GAME_PROMPT_NEXT_QUESTION_DRAWING_AUDIO_URL)
            text_output = 'Your game mode is drawing! Let\'s start! To get a question say \'Go\' or \'Go Ziggy\'!'
        else:
            speech_output = get_audio_ssml_speech(GAME_SET_MODE_INSTRUCTION_AUDIO_URL) 
    else:
        speech_output = get_audio_ssml_speech(GAME_SET_MODE_INSTRUCTION_AUDIO_URL)
   
    
    session_attributes = set_session_variables(2, 1, [], game_mode_value)
    speechlet_response = build_speechlet_response_ssml(card_title, text_output, speech_output, reprompt_text, should_end_session)
    return build_response(session_attributes, speechlet_response)
   
def get_feelings_game_next_question(intent, session):
    if session.get('attributes', {}) and "appState" in session.get('attributes', {}):
        if(session['attributes']['appState'] < 2):
            return get_help_response(intent, session)

    should_end_session = False
    card_title = "The Feelings Game"
    reprompt_text = get_audio_ssml_speech(GAME_EXTRA_TIME_INSTRUCTION_AUDIO_URL)

    #get the current question
    if session.get('attributes', {}) and "gameIsActing" in session.get('attributes', {}):
        current_game_mode = session['attributes']['gameIsActing']
        current_questions_asked = session['attributes']['gameQuestionsAsked']
        current_game_question = session['attributes']['gameCurrentQuestion'] + 1
    else:    
        current_game_mode = 1
        current_questions_asked = []
        current_game_question = 1

    #checking if questions ran out
    if(current_game_question > GAME_TOTAL_QUESTIONS):
        session_attributes = set_session_variables(3, current_game_question, current_questions_asked, current_game_mode)
        text_output = 'Bummer! Ziggy ran out of questions. Check back soon for more updates!'
        speech_output = '<speak>Ziggy, our favorite Zebra, <prosody rate="slow">ran out of questions to ask. </prosody><say-as interpret-as="interjection">darn</say-as> <break time="1s"/>If you want to play again, say play again. <break time=".5s"/>If you are done you can say, quit</speak>'
        reprompt_text = 'If you want to play again, say play again. <break time=".5s"/>If you are done you can say, quit'
        return build_response(session_attributes, build_speechlet_response_ssml(card_title, text_output, speech_output, reprompt_text, should_end_session))

    #querying for question
    question_id = generate_random_question_id_number_not_used(session)

    game_query_result = api_request('game_questions?transform=1&filter=id,eq,'+str(question_id))

    #handling session attribute updates
    current_questions_asked.append(question_id)
    session_attributes = set_session_variables(3, current_game_question, current_questions_asked, current_game_mode)

    wait_music_audio_url = WAIT_MUSIC_ACTING_AUDIO_URL
    if(current_game_mode == 0):
        wait_music_audio_url = WAIT_MUSIC_DRAWING_AUDIO_URL

    #building response, outputing question
    question_output = create_audio_ssml(game_query_result['game_questions'][0]['audio_url'])
    text_output = game_query_result['game_questions'][0]['text']
    wait_music_output = create_audio_ssml(wait_music_audio_url)
    speech_output = create_speak_ssml(question_output + wait_music_output)
    speechlet_response = build_speechlet_response_ssml(card_title, text_output, speech_output, reprompt_text, should_end_session)

    
    return build_response(session_attributes, speechlet_response)


def give_extra_time(intent, session): 
    if session.get('attributes', {}) and "appState" in session.get('attributes', {}):
        if(session['attributes']['appState'] < 3):
            return get_help_response(intent, session)
    should_end_session = False
    card_title = "Extra Time"
    reprompt_text = get_audio_ssml_speech(GAME_EXTRA_TIME_INSTRUCTION_AUDIO_URL)
    
    if session.get('attributes', {}) and "gameIsActing" in session.get('attributes', {}):
        current_game_mode = session['attributes']['gameIsActing']
    else:
        current_game_mode = 1

    wait_music_output = WAIT_MUSIC_ACTING_AUDIO_URL
    if(current_game_mode == 0):
        wait_music_output = WAIT_MUSIC_DRAWING_AUDIO_URL

    speech_output = get_audio_ssml_speech(wait_music_output)
    text_output = 'If you need more time say, "more time". Or if you are ready for the next question, say, "go" or "go Ziggy"!'
    session_attributes = get_current_session_variables(session)

    speechlet_response = build_speechlet_response_ssml(card_title, text_output, speech_output, reprompt_text, should_end_session)
    return build_response(session_attributes, speechlet_response)


def get_help_response(intent, session):
    session_attributes = get_current_session_variables(session)
    card_title = "Help"
    if session.get('attributes', {}) and "appState" in session.get('attributes', {}):
        if(session['attributes']['appState'] == 1):
            speech_output = 'If you are acting, you can say, "act". Or if you are drawing, you can say "draw".'
            reprompt_text = 'Say "Act", if you want to act out the scenarios in the game. Say "Draw", if you want to draw the scenarios in the game.'
        elif(session['attributes']['appState'] == 2):
            speech_output = 'To continue playing the game, get a question by saying "go" or "go ziggy"'
            reprompt_text = 'To get a question, you can say "go" or "go ziggy".'
        elif(session['attributes']['appState'] == 3):
            speech_output = 'If you need more time, you can say "more time". Or to continue playing you can say "go" or "go Ziggy" for the next question.'
            reprompt_text = 'If extra time is needed, you can say "more time". Or say "go" or "go Ziggy" to continue game.'
        else:
            speech_output = 'To start playing the feelings game with Ziggy, you can say, "play game".'
            reprompt_text = 'Say "play game", to play the feelings game with Ziggy.'
    else:
        speech_output = 'To start playing the feelings game with Ziggy, you can say, "play game".'
        reprompt_text = 'Say "play game", to play the feelings game with Ziggy.'
        
    text_output = speech_output
    should_end_session = False
    return build_response(session_attributes,  build_speechlet_response(card_title, text_output, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying "+SKILL_NAME+" Have a nice day!"
    text_output = speech_output
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, text_output, speech_output, None, should_end_session))

def get_audio_ssml_speech(audio_url):
    return '<speak><audio src=\''+audio_url+'\'/></speak>'

def create_audio_ssml(audio_url):
    return '<audio src=\''+audio_url+'\'/>'

def create_speak_ssml(message):    
    return '<speak>'+message+'</speak>'
            
def api_request(request_query):
    response = urllib2.urlopen(API_BASE + '/' + request_query)
    query_result = json.load(response)
    return query_result

def set_session_variables(appState, gameCurrentQuestion, gameQuestionsAsked, gameIsActing):
    return {
                'appState':appState, 
                'gameCurrentQuestion': gameCurrentQuestion, 
                'gameQuestionsAsked': gameQuestionsAsked, 
                'gameIsActing':gameIsActing
            }

def get_current_session_variables(session):
    if session.get('attributes', {}) and "appState" in session.get('attributes', {}):
        return {
                    'appState':session['attributes']['appState'], 
                    'gameCurrentQuestion': session['attributes']['gameCurrentQuestion'], 
                    'gameQuestionsAsked': session['attributes']['gameQuestionsAsked'], 
                    'gameIsActing': session['attributes']['gameIsActing'] 
                }
    else:
        return {}

def generate_random_question_id_number_not_used(session):
    if session.get('attributes', {}) and "gameQuestionsAsked" in session.get('attributes', {}):
        gameQuestionsAsked = session['attributes']['gameQuestionsAsked']
        return random.choice([x for x in range(1,GAME_TOTAL_QUESTIONS+1) if x not in gameQuestionsAsked])
    else:
        return random.choice([x for x in range(1,GAME_TOTAL_QUESTIONS+1) if x not in []])

            
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

    if intent_name == "AMAZON.HelpIntent":
        return get_help_response(intent, session)
    elif intent_name == "IntentNotKnown":
        return get_help_response(intent, session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    elif intent_name == "PlayTheFeelingsGame":
        return start_feelings_game(intent, session)
    elif intent_name == "SetGameMode":
        return set_draw_or_act_settings(intent, session)
    elif intent_name == "PromptNextQuestion":
        return get_feelings_game_next_question(intent, session)
    elif intent_name == "GetExtraTime":
        return give_extra_time(intent, session)
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
