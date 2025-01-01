""" import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_auth_token():
    client = boto3.client('cognito-idp', region_name=os.getenv("AWS_REGION"))

    response = client.initiate_auth(
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': "sejjari.soufian@gmail.com",
            'PASSWORD': "Password123!"
        },
        ClientId=os.getenv("COGNITO_CLIENT_ID")
    )

    return response['AuthenticationResult']['IdToken'] """