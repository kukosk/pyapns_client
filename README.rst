*************
pyapns_client
*************

|version| |license|

Simple, flexible and fast Apple Push Notifications on iOS, OSX and Safari using the HTTP/2 Push provider API.


Features
========

- Uses the new Apple APNs HTTP/2 protocol
- Supports the new iOS 10 features such as Collapse IDs, Subtitles and Mutable Notifications
- Supports persistent connections to APNS


Cautions
========

- Works only with Python 3.5 and higher


Installation
============

Install using pip:

.. code-block:: bash

    pip install pyapns_client


Usage
=====

.. code-block:: python

    from pyapns_client import APNSClient, IOSPayloadAlert, IOSPayload, IOSNotification, APNSException, UnregisteredException


    cli = APNSClient(mode=APNSClient.MODE_DEV, client_cert='/your/path.pem')
    alert = IOSPayloadAlert(body='body!', title='title!')
    payload = IOSPayload(alert=alert)
    notification = IOSNotification(payload=payload, priority=IOSNotification.PRIORITY_LOW)

    try:
        cli.push(notification=notification, device_token='your_token')
    except APNSException as e:
        if e.is_device_error:
            if isinstance(e, UnregisteredException):
                # device is unregistered, compare timestamp (e.timestamp_datetime) and remove from db
                pass
            else:
                # flag the device as potentially invalid
                pass
        elif e.is_apns_error:
            # try again later
            pass
        elif e.is_programming_error:
            # check your code
            # try again later
            pass
    else:
        # everything is ok
        pass


.. |version| image:: https://img.shields.io/pypi/v/pyapns_client.svg?style=flat-square
    :target: https://pypi.python.org/pypi/pyapns_client/

.. |license| image:: https://img.shields.io/pypi/l/pyapns_client.svg?style=flat-square
    :target: https://pypi.python.org/pypi/pyapns_client/