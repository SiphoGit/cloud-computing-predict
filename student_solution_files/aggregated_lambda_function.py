
"""
    Final AWS Lambda function skeleton. 
    
    Author: Explore Data Science Academy.
    
    Note:
    ---------------------------------------------------------------------
    The contents of this file should be added to a AWS  Lambda function 
    created as part of the EDSA Cloud-Computing Predict. 
    For further guidance around this process, see the README instruction 
    file which sits at the root of this repo.
    ---------------------------------------------------------------------

"""

# Lambda dependencies
import boto3    # Python AWS SDK
import json     # Used for handling API-based data.
import base64   # Needed to decode the incoming POST data
import numpy as np # Array manipulation
from botocore.exceptions import ClientError

from email_responses import email_response
from write_data_to_dynamodb import lambda_handler as write_data_to_dynamodb
from basic_lambda_data_decoding import lambda_handler as user_input_decoder

# Get key phrases
def comprehend_extract_key_phrases(enquiry_text, service):
    response = service.detect_key_phrases(
        Text=enquiry_text,
        LanguageCode='en'
    )   
    return response

# Extract sentiment 
def comprehend_extract_sentiment(enquiry_text, service_name):
    response = service_name.detect_sentiment(
        Text=enquiry_text,
        LanguageCode='en'
    )   
    return response
 
# Send automated emails
def send_email(recipient, subject, body):
    client = boto3.client('ses')
    
    SENDER = 'shimanges1@gmail.com'
    CHARSET = "UTF-8"
    
    # Try to send the email.
    try:
        ses_response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                    # 'edsa.predicts@explore-ai.net', # <--- Uncomment this line once you have successfully tested your predict end-to-end
                ],
            },
            Message={
                'Body': {

                    'Text': {
                        'Charset': CHARSET,
                        'Data': body,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=SENDER,
        )

    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(ses_response['MessageId'])

# Lambda function orchestrating the entire predict logic
def lambda_handler(event, context):
    # Perform JSON data decoding 
    body_enc = event['body']
    dec_dict = json.loads(base64.b64decode(body_enc))
    
    # Write data to DynamoDB
    # Do not change the name of this variable
    db_response = write_data_to_dynamodb(event, context)
    
    # --- Amazon Comprehend object---
    comprehend = boto3.client(service_name='comprehend')
    
    # Decode data entered by user
    enquiry_text = user_input_decoder(event, context)
    
    # Get sentiment using AWS comprehend
    sentiment = comprehend_extract_sentiment(enquiry_text, comprehend) 
    # -----------------------------
    
    # Extract key phrases using AWS comprehend
    key_phrases = comprehend_extract_key_phrases(enquiry_text, comprehend) 
    # -----------------------------
    
    # Get list of phrases in numpy array
    phrase = []
    for i in range(0, len(key_phrases['KeyPhrases'])-1):
        phrase = np.append(phrase, key_phrases['KeyPhrases'][i]['Text'])


    # ** Use the `email_response` function to generate the text for your email response **
    # <<< Ensure that the response text is stored in the variable `email_text` >>> 
    # --- Insert your code here ---
    article_critical_phrase_list = ['article','Article',
                                    'blog', 'Blog', 
                                    'post', 'Post']
    
    # Do not change the name of this variable
    name = dec_dict['name']
    email_text = email_response(name, article_critical_phrase_list, phrase, sentiment)

    # -----------------------------
            
    # ** SES Functionality **

    # Send an email, using AWS SES, 
    recipient = 'shimanges1@gmail.com'

    # Do not modify the email subject line
    SUBJECT = f"Data Science Portfolio Project Website - Hello {dec_dict['name']}"
    
    # Do not change the name of this variable
    ses_response = send_email(recipient, SUBJECT, email_text)
    
    # ...

    # -----------------------------

    # ** Create a response object to inform the website that the 
    #    workflow executed successfully. Note that this object is 
    #    used during predict marking and should not be modified.**
    # --- DO NOT MODIFY THIS CODE ---
    lambda_response = {
        'statusCode': 200,
        'body': json.dumps({
        'Name': dec_dict['name'],
        'Email': dec_dict['email'],
        'Cell': dec_dict['phone'], 
        'Message': dec_dict['message'],
        'DB_response': db_response,
        'SES_response': ses_response,
        'Email_message': email_text
        })
    }
    # -----------------------------
    
    return lambda_response   