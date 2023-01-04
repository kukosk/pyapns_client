# Copyright (c) 2022 Aleksandr Soloshenko
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


import time
from typing import Any, Dict, Union

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from .logging import logger


class Auth:
    def __init__(self) -> None:
        raise NotImplementedError

    def __call__(self) -> Dict[str, Any]:
        raise NotImplementedError


class TokenBasedAuth(Auth):

    AUTH_TOKEN_LIFETIME = 45 * 60  # seconds
    AUTH_TOKEN_ENCRYPTION = "ES256"

    def __init__(
        self,
        auth_key_path: str,
        auth_key_id: str,
        team_id: str,
        auth_key_password: Union[None, str] = None,
    ):
        self._auth_key = self._get_auth_key(auth_key_path) if auth_key_path else None
        if self._auth_key and auth_key_password:
            self._auth_key = serialization.load_pem_private_key(
                self._auth_key.encode(),
                password=auth_key_password.encode(),
                backend=default_backend(),
            )
        self._auth_key_id = auth_key_id
        self._team_id = team_id

        self._auth_token_time = None
        self._auth_token_storage = None

    def __call__(self) -> Dict[str, Any]:
        return {
            "auth": self._authenticate_request,
        }

    def _authenticate_request(self, request):
        request.headers["authorization"] = f"bearer {self._auth_token}"
        return request

    @property
    def _is_auth_token_expired(self):
        if self._auth_token_time is None:
            return True
        return time.time() >= self._auth_token_time + self.AUTH_TOKEN_LIFETIME

    @staticmethod
    def _get_auth_key(auth_key_path):
        with open(auth_key_path) as f:
            return f.read()

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


class CertificateBasedAuth(Auth):
    def __init__(
        self,
        client_cert_path: str,
        client_cert_passphrase: Union[None, str] = None,
    ):
        self._client_cert_path = client_cert_path
        self._client_cert_passphrase = client_cert_passphrase

    def __call__(self) -> Dict[str, Any]:
        return {
            "cert": (
                self._client_cert_path,
                self._client_cert_path,
                self._client_cert_passphrase,
            )
        }
