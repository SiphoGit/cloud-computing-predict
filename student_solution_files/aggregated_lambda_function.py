
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
# <<< You will need to add additional libraries to complete this script >>> 

# ** Insert key phrases function **
def comprehend_extract_key_phrases(event, service):
    # Perform JSON data decoding 
    body_enc = event['body']
    dec_dict = json.loads(base64.b64decode(body_enc))
    
    response = service.detect_key_phrases(
        Text=dec_dict["message"],
        LanguageCode='en'
    )   
    return response

# -----------------------------

# ** Insert sentiment extraction function **
def comprehend_extract_sentiment(event, service_name):
    # Perform JSON data decoding 
    body_enc = event['body']
    dec_dict = json.loads(base64.b64decode(body_enc))
    
    response = service_name.detect_sentiment(
        Text=dec_dict["message"],
        LanguageCode='en'
    )   
    return response
 
# -----------------------------

# ** Insert email responses function **
def send_email(recipient, subject, body):
    client = boto3.client('ses')
    
    SENDER = 'shianges@yahoo.com'
    CHARSET = "UTF-8"
    
     # Try to send the email.
    try:
        #Provide the contents of the email.
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
 
# -----------------------------

# Lambda function orchestrating the entire predict logic
def lambda_handler(event, context):
    
    # Perform JSON data decoding 
    body_enc = event['body']
    dec_dict = json.loads(base64.b64decode(body_enc))
    
    # ** Insert code to write to dynamodb **
    # <<< Ensure that the DynamoDB write response object is saved 
    #    as the variable `db_response` >>> 
    # --- Insert your code here ---


    # Do not change the name of this variable
    db_response = write_data_to_dynamodb(event, context)
    # -----------------------------
    
    # --- Amazon Comprehend ---
    comprehend = boto3.client(service_name='comprehend')
    
    # --- Insert your code here ---
    enquiry_text = user_input_decoder(event, context) # <--- Insert code to place the website message into this variable
    # -----------------------------
    
    # --- Insert your code here ---
    sentiment = comprehend_extract_sentiment(enquiry_text, comprehend) # <---Insert code to get the sentiment with AWS comprehend
    # -----------------------------
    
    # --- Insert your code here ---
    key_phrases = comprehend_extract_key_phrases(enquiry_text, comprehend) # <--- Insert code to get the key phrases with AWS comprehend
    # -----------------------------
    
    # Get list of phrases in numpy array
    phrase = []
    for i in range(0, len(key_phrases['KeyPhrases'])-1):
        phrase = np.append(phrase, key_phrases['KeyPhrases'][i]['Text'])


    # ** Use the `email_response` function to generate the text for your email response **
    # <<< Ensure that the response text is stored in the variable `email_text` >>> 
    # --- Insert your code here ---
    article_critical_phrase_list = ['article','Article',
                                    'blog', 'Blog']
    
    # Do not change the name of this variable
    name = dec_dict["Name"]
    email_text = email_response(name, article_critical_phrase_list, phrase, sentiment)

    # -----------------------------
            
    # ** SES Functionality **

    # Insert code to send an email, using AWS SES, with the above defined 
    # `email_text` variable as it's body.
    # <<< Ensure that the SES service response is stored in the variable `ses_response` >>> 
    # --- Insert your code here ---
    recipient = 'shimanges@yaoo.com'

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
    




