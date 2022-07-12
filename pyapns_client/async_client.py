import time
from typing import Union

import httpx

from . import exceptions
from .base import BaseAPNSClient
from .logging import logger


class AsyncAPNSClient(BaseAPNSClient):
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
        super().__init__(
            mode,
            root_cert_path=root_cert_path,
            auth_key_path=auth_key_path,
            auth_key_id=auth_key_id,
            team_id=team_id,
            client_cert_path=client_cert_path,
            client_cert_passphrase=client_cert_passphrase,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def push(self, notification, device_token):
        headers = notification.get_headers()
        json_data = notification.get_json_data()

        logger.debug(
            f'Sending notification: {len(json_data)} bytes {json_data} to: "{device_token}".'
        )

        exc = None
        start_time = time.perf_counter()
        for _ in range(3):
            try:
                await self._push(
                    headers=headers, json_data=json_data, device_token=device_token
                )
                exc = None
                break
            except exceptions.APNSServerException as e:
                exc = e
                await self._reset_client()
            except exceptions.APNSException as e:
                exc = e
                break
        duration = round((time.perf_counter() - start_time) * 1000)

        if exc is not None:
            logger.debug(
                f"Failed to send the notification: {type(exc).__name__} {duration}ms."
            )
            raise exc

        logger.debug(f"Sent: {duration}ms.")

    async def close(self):
        await self._reset_client()
        self._reset_auth_token()
        logger.debug("Closed.")

    async def _push(self, headers, json_data, device_token):
        try:
            response = await self._send_request(
                headers=headers, json_data=json_data, device_token=device_token
            )
        except httpx.RequestError as e:
            logger.debug(f"Failed to receive a response: {type(e).__name__}.")
            raise exceptions.APNSConnectionException()

        self._parse_response(response)

    async def _send_request(self, headers, json_data, device_token):
        url = f"/3/device/{device_token}"
        return await self._client.post(url, data=json_data, headers=headers)

    @property
    def _client(self):
        if self._client_storage is None:
            logger.debug("Creating a new client instance.")
            limits = httpx.Limits(max_connections=1, max_keepalive_connections=0)
            self._client_storage = httpx.AsyncClient(
                auth=self._authenticate_request if self._auth_type == "jwt" else None,
                cert=(
                    str(self._client_cert_path),
                    self._client_cert_path,
                    self._client_cert_passphrase,
                )
                if self._auth_type == "cert"
                else None,
                verify=self._root_cert_path,
                http2=True,
                timeout=10.0,
                limits=limits,
                base_url=self._base_url,
            )

        return self._client_storage

    async def _reset_client(self):
        logger.debug("Resetting the existing client instance.")
        if self._client_storage is not None:
            await self._client_storage.aclose()
        self._client_storage = None
