*************
pyapns_client
*************

|version| |license|

Simple, flexible and fast Apple Push Notifications on iOS, OSX and Safari using the HTTP/2 Push provider API.


Features
========

- Uses the new Apple APNs HTTP/2 protocol with persistent connections
- Uses token-based authentication (no need to renew your certificates anymore)
- Uses the httpx HTTP client library
- Supports the new iOS 10 features such as Collapse IDs, Subtitles and Mutable Notifications
- Makes the integration and error handling really simple with auto-retry on APNs errors


Cautions
========

- Works only with Python 3.6 and higher


Installation
============

Install using pip:

.. code-block:: bash

    pip install pyapns_client


Usage
=====

.. code-block:: python

    from pyapns_client import APNSClient, IOSPayloadAlert, IOSPayload, IOSNotification, APNSDeviceException, APNSServerException, APNSProgrammingException, UnregisteredException


    client = APNSClient(mode=APNSClient.MODE_DEV, root_cert_path='/path/to/root_cert.pem', auth_key_path='/path/to/auth_key.p8', auth_key_id='AUTHKEY123', team_id='TEAMID1234')
    # `root_cert_path` is for the AAACertificateServices root cert (https://apple.co/3mZ5rB6)
    # with token-based auth you don't need to create / renew your APNS SSL certificates anymore
    # you can pass `None` to `root_cert_path` if you have the cert included in your trust store
    # httpx uses 'SSL_CERT_FILE' and 'SSL_CERT_DIR' from `os.environ` to find your trust store

    try:
        device_tokens = ['device_token_1', 'device_token_2']
        alert = IOSPayloadAlert(title='Title', subtitle='Subtitle', body='Some message.')
        payload = IOSPayload(alert=alert)
        notification = IOSNotification(payload=payload, topic='domain.organization.app')

        for device_token in device_tokens:
            try:
                client.push(notification=notification, device_token=device_token)
            except UnregisteredException as e:
                print(f'device is unregistered, compare timestamp {e.timestamp_datetime} and remove from db')
            except APNSDeviceException:
                print('flag the device as potentially invalid and remove from db after a few tries')
            except APNSServerException:
                print('try again later')
            except APNSProgrammingException:
                print('check your code and try again later')
            else:
                print('everything is ok')
    finally:
        client.close()


.. |version| image:: https://img.shields.io/pypi/v/pyapns_client.svg?style=flat-square
    :target: https://pypi.python.org/pypi/pyapns_client/

.. |license| image:: https://img.shields.io/pypi/l/pyapns_client.svg?style=flat-square
    :target: https://pypi.python.org/pypi/pyapns_client/