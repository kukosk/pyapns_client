from hyper import HTTP20Connection
from hyper.tls import init_context
from hyper.http20.exceptions import StreamResetError
import json
import time

from . import exceptions
from .logging import logger


class APNSClient:

    MODE_PROD = 'prod'
    MODE_DEV = 'dev'

    HOSTS = {
        MODE_PROD: 'api.push.apple.com',
        MODE_DEV: 'api.development.push.apple.com',
    }

    def __init__(self, mode, client_cert, password=None, proxy_host=None, proxy_port=None):
        super().__init__()

        self._host = self.HOSTS[mode]
        self._init_context = init_context(cert=client_cert, cert_password=password)
        self._proxy_host = proxy_host
        self._proxy_port = proxy_port

        self._connection_storage = None

    @property
    def _connection(self):
        if self._connection_storage is None:
            logger.debug('Creating a new HTTP2 connection instance.')
            self._connection_storage = HTTP20Connection(
                host=self._host,
                port=443,
                secure=True,
                ssl_context=self._init_context,
                proxy_host=self._proxy_host,
                proxy_port=self._proxy_port,
            )

        return self._connection_storage

    @_connection.setter
    def _connection(self, value):
        logger.debug('Discarding the existing HTTP2 connection instance.')
        self._connection_storage = value

    def push(self, notification, device_token):
        headers = notification.get_headers()
        json_data = notification.get_json_data()

        logger.debug(f'Sending notification: {len(json_data)} bytes {json_data} to: "{device_token}".')

        exc = None
        start_time = time.perf_counter()
        for i in range(3):
            try:
                self._push(headers=headers, json_data=json_data, device_token=device_token)
                exc = None
                break
            except exceptions.APNSException as e:
                exc = e
                if e.is_apns_error:
                    self._connection = None
                else:
                    break
        duration = round((time.perf_counter() - start_time) * 1000)

        if exc is not None:
            logger.debug(f'Failed to send the notification: {type(exc).__name__} {duration}ms.')
            raise exc

        logger.debug(f'Sent: {duration}ms.')

    def _push(self, headers, json_data, device_token):
        try:
            response = self._send_request(headers=headers, json_data=json_data, device_token=device_token)
        except StreamResetError as e:
            logger.debug(f'Failed to receive a response: {type(e).__name__}.')
            raise exceptions.APNSConnectionException(status_code=None, apns_id=None)
        
        status = 'success' if response.status == 200 else 'failure'
        logger.debug(f'Response received: {response.status} ({status}).')

        if response.status != 200:
            apns_ids = response.headers.get('apns-id')
            apns_id = apns_ids[0] if apns_ids else None

            body = response.read()
            apns_data = json.loads(body.decode('utf-8'))
            reason = apns_data['reason']

            logger.debug(f'Response reason: {reason}.')

            try:
                exception_class_name = f'{reason}Exception'
                exception_class = getattr(exceptions, exception_class_name)
            except AttributeError:
                raise NotImplementedError(f'Reason not implemented: {reason}')

            exception_kwargs = {'status_code': response.status, 'apns_id': apns_id}
            if issubclass(exception_class, exceptions.APNSTimestampException):
                exception_kwargs['timestamp'] = apns_data['timestamp']

            raise exception_class(**exception_kwargs)

    def _send_request(self, headers, json_data, device_token):
        url = f'/3/device/{device_token}'
        stream_id = self._connection.request(method='POST', url=url, body=json_data, headers=headers)
        response = self._connection.get_response(stream_id=stream_id)
        return response
