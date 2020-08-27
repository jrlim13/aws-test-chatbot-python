import os
import json
import boto3
import requests

print('Loading function')

PAGE_ACCESS_TOKEN = os.environ['PAGE_ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
BOT_NAME = os.environ['BOT_NAME']
BOT_ALIAS = os.environ['BOT_ALIAS']

def lambda_handler(event, context):
    method = event['context']['http-method']
    response = ''
    querystring = event['params']['querystring']

    if method == 'GET':
        if(querystring['hub.mode'] == 'subscribe' and querystring['hub.verify_token'] == VERIFY_TOKEN):
              response = querystring['hub.challenge']
        else:
            response = "Error, wrong verify token."

        return response
    else:
        if method == 'POST':
            message_entries = event['body-json']['entry']
            for entry in message_entries:
                for messaging in entry['messaging']:
                    if "message" in messaging and "is_echo" not in messaging['message']:
                        try:
                            sender_id = messaging['sender']['id']
                            message_text = messaging['message']['text']
                            print(messaging)
                            print(sender_id)
                            print(message_text)
                            
                            response = get_chatbot_response(sender_id, message_text)
                            print(response)
                            print(response['message'])
        
                            data = {
                                        "messaging_type": "RESPONSE",
                                        "recipient": {
                                            "id": sender_id
                                        },
                                        "message": {
                                            "text": response['message']
                                        }   
                                    }
                            r = requests.post('https://graph.facebook.com/v8.0/me/messages?access_token={}'.format(PAGE_ACCESS_TOKEN), json=data)    
                            print(r.text)
                        except Exception as e:
                            raise e

def get_chatbot_response(sender_id, message_text):
    lexruntime = boto3.client('lex-runtime')
    
    try:
        response = lexruntime.post_text(
                    botName=BOT_NAME,
                    botAlias=BOT_ALIAS,
                    userId=sender_id,
                    sessionAttributes={
                    },
                    requestAttributes={
                    },
                    inputText=message_text
                )
    except Exception as e:
        raise e

    return response