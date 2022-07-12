import time
from typing import Union

import httpx
import jwt

from . import exceptions
from .logging import logger


class BaseAPNSClient:
    MODE_PROD = "prod"
    MODE_DEV = "dev"

    BASE_URLS = {
        MODE_PROD: "https://api.push.apple.com:443",
        MODE_DEV: "https://api.development.push.apple.com:443",
    }

    AUTH_TOKEN_LIFETIME = 45 * 60  # seconds
    AUTH_TOKEN_ENCRYPTION = "ES256"

    def __init__(
        self,
        mode: str,
        *,
        root_cert_path: Union[None, str, bool] = None,
        auth_key_path: Union[None, str] = None,
        auth_key_id: Union[None, str] = None,
        team_id: Union[None, str] = None,
        client_cert_path: Union[None, str] = None,
        client_cert_passphrase: Union[None, str] = None,
    ):
        """
        Initialize the APNSClient instance. Clients supports two types of authentication:
        - JWT authentication (auth_key_path, auth_key_id, team_id)
        - certificate authentication (client_cert_path, client_cert_passphrase)

        :param mode: The mode of the client. Either 'prod' or 'dev'.

        :param root_cert_path: The path to the root certificate.
        :param auth_key_path: The path to the authentication key.
        :param auth_key_id: The ID of the authentication key.
        :param team_id: The ID of the team.

        :param client_cert_path: The path to the client certificate.
        :param client_cert_passphrase: The passphrase of the client certificate.
        """
        super().__init__()

        if root_cert_path is None:
            root_cert_path = True

        self._base_url = self.BASE_URLS[mode]
        self._root_cert_path = root_cert_path
        self._auth_key = self._get_auth_key(auth_key_path) if auth_key_path else None
        self._auth_key_id = auth_key_id
        self._team_id = team_id

        self._client_cert_path = client_cert_path
        self._client_cert_passphrase = client_cert_passphrase

        if self._auth_key and self._auth_key_id and self._team_id:
            self._auth_type = "jwt"
        elif self._client_cert_path and self._client_cert_passphrase:
            self._auth_type = "cert"
        else:
            raise ValueError("Either the auth key or the client cert must be provided.")

        self._auth_token_time = None
        self._auth_token_storage = None
        self._client_storage = None

    def _authenticate_request(self, request):
        request.headers["authorization"] = f"bearer {self._auth_token}"
        return request

    def _parse_response(self, response: httpx.Response) -> None:
        status = "success" if response.status_code == 200 else "failure"
        logger.debug(f"Response received: {response.status_code} ({status})")

        if response.status_code != 200:
            apns_id = response.headers.get("apns-id")
            apns_data = response.json()
            reason = apns_data["reason"]

            logger.debug(f"Response reason: {reason}.")

            exception_class = self._get_exception_class(reason)
            exception_kwargs = {"status_code": response.status_code, "apns_id": apns_id}
            if issubclass(exception_class, exceptions.UnregisteredException):
                exception_kwargs["timestamp"] = apns_data["timestamp"]

            raise exception_class(**exception_kwargs)

    def _reset_auth_token(self):
        logger.debug("Resetting the existing authentication token.")
        self._auth_token_time = None
        self._auth_token_storage = None

    @property
    def _auth_token(self):
        if self._auth_token_storage is None or self._is_auth_token_expired:
            logger.debug("Creating a new authentication token.")
            self._auth_token_time = time.time()
            token_dict = {"iss": self._team_id, "iat": self._auth_token_time}
            headers = {"alg": self.AUTH_TOKEN_ENCRYPTION, "kid": self._auth_key_id}
            auth_token = jwt.encode(
                token_dict,
                str(self._auth_key),
                algorithm=self.AUTH_TOKEN_ENCRYPTION,
                headers=headers,
            )
            self._auth_token_storage = auth_token

        return self._auth_token_storage

    @property
    def _http_options(self):
        limits = httpx.Limits(max_connections=1, max_keepalive_connections=0)
        return {
            "auth": self._authenticate_request if self._auth_type == "jwt" else None,
            "cert": (
                str(self._client_cert_path),
                self._client_cert_path,
                self._client_cert_passphrase,
            )
            if self._auth_type == "cert"
            else None,
            "verify": self._root_cert_path,
            "http2": True,
            "timeout": 10.0,
            "limits": limits,
            "base_url": self._base_url,
        }

    @property
    def _is_auth_token_expired(self):
        if self._auth_token_time is None:
            return True
        return time.time() >= self._auth_token_time + self.AUTH_TOKEN_LIFETIME

    @staticmethod
    def _get_auth_key(auth_key_path):
        with open(auth_key_path) as f:
            return f.read()

    @staticmethod
    def _get_exception_class(reason):
        exception_class_name = f"{reason}Exception"
        try:
            return getattr(exceptions, exception_class_name)
        except AttributeError:
            raise NotImplementedError(f"Reason not implemented: {reason}")
