*************
pyapns_client
*************

|version| |license|

Simple, flexible and fast Apple Push Notifications on iOS, OSX and Safari using the HTTP/2 Push provider API.


Features
========

- Uses the new Apple APNs HTTP/2 protocol with persistent connections
- Uses token-based authentication
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


    client = APNSClient(mode=APNSClient.MODE_DEV, root_cert_path='/your/path.pem', auth_key_path='/your/path.p8', auth_key_id='AUTHKEY123', team_id='TEAMID1234')

    try:
        device_tokens = ['your_token1', 'your_token2']
        alert = IOSPayloadAlert(body='Some message.', title='Title')
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