import boto3
import os
import requests
from jose import jwk, jwt
from jose.utils import base64url_decode
from functools import wraps
from flask import request, jsonify

class CognitoAuth:
    def __init__(self):
        self.region = os.getenv('AWS_REGION')
        self.user_pool_id = os.getenv('COGNITO_USER_POOL_ID')
        self.client_id = os.getenv('COGNITO_CLIENT_ID')
        self.client_secret = os.getenv('COGNITO_CLIENT_SECRET')
        self.cognito_client = boto3.client('cognito-idp', region_name=self.region)

    def verify_token(self, token):
        """Verify JWT token from Cognito"""
        try:
            headers = jwt.get_unverified_headers(token)
            kid = headers['kid']
            print(f"Token headers: {headers}")

            # Get public key from Cognito
            keys_url = f'https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json'
            keys_response = requests.get(keys_url)
            keys = keys_response.json()['keys']
            print(f"Keys from Cognito: {keys}")

            key = [k for k in keys if k['kid'] == kid][0]
            public_key = jwk.construct(key)

            # Verify token
            message, encoded_signature = token.rsplit('.', 1)
            decoded_signature = base64url_decode(encoded_signature.encode())
            print(f"Decoded signature: {decoded_signature}")

            if not public_key.verify(message.encode(), decoded_signature):
                print("Token verification failed")
                return False

            claims = jwt.get_unverified_claims(token)
            print(f"Token claims: {claims}")
            return claims
        except Exception as e:
            print(f"Error verifying token: {str(e)}")
            return False

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token is missing'}), 401

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            auth = CognitoAuth()
            claims = auth.verify_token(token)
            if not claims:
                return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            print(f"Error in require_auth: {str(e)}")
            return jsonify({'message': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated