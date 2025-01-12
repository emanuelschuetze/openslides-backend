from typing import Dict, Optional, Tuple
from urllib import parse

from authlib import (
    ANONYMOUS_USER,
    AUTHENTICATION_HEADER,
    COOKIE_NAME,
    AuthenticateException,
    AuthHandler,
    InvalidCredentialsException,
)
from authlib.constants import AUTHORIZATION_HEADER

from ...shared.exceptions import AuthenticationException
from ...shared.interfaces.logging import LoggingModule
from ...shared.interfaces.wsgi import Headers
from .interface import AuthenticationService


class AuthenticationHTTPAdapter(AuthenticationService):
    """
    Adapter to connect to authentication service.
    """

    def __init__(self, logging: LoggingModule) -> None:
        self.logger = logging.getLogger(__name__)
        self.auth_handler = AuthHandler(self.logger.debug)
        self.headers = {"Content-Type": "application/json"}

    def authenticate(
        self, headers: Headers, cookies: Dict[str, str]
    ) -> Tuple[int, Optional[str]]:
        """
        Fetches user id from authentication service using request headers.
        Returns a new access token, too, if one is received from auth service.
        """

        access_token = headers.get(AUTHENTICATION_HEADER, None)
        cookie = cookies.get(COOKIE_NAME, "")
        self.logger.debug(
            f"Start request to authentication service with the following data: access_token: {headers}, cookie: {cookie}"
        )
        try:
            return self.auth_handler.authenticate(access_token, parse.unquote(cookie))
        except (AuthenticateException, InvalidCredentialsException) as e:
            self.logger.debug(f"Error in auth service: {e.message}")
            raise AuthenticationException(e.message)

    def authenticate_only_refresh_id(self, cookies: Dict[str, str]) -> int:
        cookie = cookies.get(COOKIE_NAME, "")
        self.logger.debug(
            f"Start request to authentication service with the following cookie: {cookie}"
        )
        try:
            return self.auth_handler.authenticate_only_refresh_id(parse.unquote(cookie))
        except (AuthenticateException, InvalidCredentialsException) as e:
            self.logger.debug(f"Error in auth service: {e.message}")
            raise AuthenticationException(e.message)

    def hash(self, toHash: str) -> str:
        return self.auth_handler.hash(toHash)

    def is_equals(self, toHash: str, toCompare: str) -> bool:
        return self.auth_handler.is_equals(toHash, toCompare)

    def is_anonymous(self, user_id: int) -> bool:
        return user_id == ANONYMOUS_USER

    def create_authorization_token(self, user_id: int, email: str) -> str:
        response = self.auth_handler.create_authorization_token(user_id, email)
        token = response.headers.get(AUTHORIZATION_HEADER, "")
        return token

    def verify_authorization_token(self, user_id: int, token: str) -> bool:
        found_user_id, email = self.auth_handler.verify_authorization_token(token)
        return user_id == found_user_id
