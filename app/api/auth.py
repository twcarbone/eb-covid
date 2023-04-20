"""Token authentication support."""

from flask_httpauth import HTTPTokenAuth

token_auth = HTTPTokenAuth()


@token_auth.verify_token
def verify_token(token):
    ...


@token_auth.error_handler
def token_auth_error(status):
    ...
