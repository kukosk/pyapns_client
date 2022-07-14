import time
from typing import Union

import httpx

from . import exceptions
from .auth import Auth
from .base import BaseAPNSClient
from .logging import logger


class AsyncAPNSClient(BaseAPNSClient):
    def __init__(
        self,
        mode: str,
        authentificator: Auth,
        *,
        root_cert_path: Union[None, str, bool] = None,
    ):
        super().__init__(mode, authentificator, root_cert_path=root_cert_path)

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
            self._client_storage = httpx.AsyncClient(**self._http_options)

        return self._client_storage

    async def _reset_client(self):
        logger.debug("Resetting the existing client instance.")
        if self._client_storage is not None:
            await self._client_storage.aclose()
        self._client_storage = None
