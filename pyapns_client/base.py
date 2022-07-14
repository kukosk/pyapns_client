from typing import Union

import httpx

from . import exceptions
from .auth import Auth
from .logging import logger


class BaseAPNSClient:
    MODE_PROD = "prod"
    MODE_DEV = "dev"

    BASE_URLS = {
        MODE_PROD: "https://api.push.apple.com:443",
        MODE_DEV: "https://api.development.push.apple.com:443",
    }

    def __init__(
        self,
        mode: str,
        authentificator: Auth,
        *,
        root_cert_path: Union[None, str, bool] = None,
    ):
        """
        Initialize the APNSClient instance with provided mode and authentificator.

        :param mode: The mode of the client. Either 'prod' or 'dev'.
        :param authentificator: The authentificator object.

        :param root_cert_path: The path to the root certificate.

        """
        super().__init__()

        if root_cert_path is None:
            root_cert_path = True

        self._base_url = self.BASE_URLS[mode]
        self._root_cert_path = root_cert_path

        self._auth = authentificator
        self._client_storage = None

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

    @property
    def _http_options(self):
        limits = httpx.Limits(max_connections=1, max_keepalive_connections=0)
        return {
            **self._auth(),
            "verify": self._root_cert_path,
            "http2": True,
            "timeout": 10.0,
            "limits": limits,
            "base_url": self._base_url,
        }

    @staticmethod
    def _get_exception_class(reason):
        exception_class_name = f"{reason}Exception"
        try:
            return getattr(exceptions, exception_class_name)
        except AttributeError:
            raise NotImplementedError(f"Reason not implemented: {reason}")
