import pytz
from datetime import datetime


# BASE

class APNSException(Exception):

    is_device_error = False  # device should be flagged as potentially invalid (remove immediately in case of UnregisteredException)
    is_apns_error = False  # try again later
    is_programming_error = False  # try again later, and check your code

    def __init__(self, status_code, apns_id):
        super().__init__()

        # The HTTP status code retuened by APNs.
        # A 200 value indicates that the notification was successfully sent.
        # For a list of other possible status codes, see table 6-4 in the Apple Local
        # and Remote Notification Programming Guide.
        self.status_code = status_code

        # The APNs ApnsID value from the Notification. If you didn't set an ApnsID on the
        # Notification, this will be a new unique UUID which has been created by APNs.
        self.apns_id = apns_id


class APNSTimestampException(APNSException):

    def __init__(self, status_code, apns_id, timestamp):
        super().__init__(status_code=status_code, apns_id=apns_id)

        # If the value of StatusCode is 410, this is the last time at which APNs
        # confirmed that the device token was no longer valid for the topic.
        # The value is in milliseconds (ms).
        self.timestamp = timestamp

    @property
    def timestamp_datetime(self):
        if not self.timestamp:
            return None
        return datetime.fromtimestamp(self.timestamp / 1000, tz=pytz.utc)


# CONNECTION

class APNSConnectionException(APNSException):
    """
    Used when a connectinon to APNS servers fail with hyper.http20.exceptions.StreamResetError.
    """

    is_apns_error = True


# APNS REASONS

class BadCollapseIdException(APNSException):
    """
    The collapse identifier exceeds the maximum allowed size.
    """

    is_programming_error = True


class BadDeviceTokenException(APNSException):
    """
    The specified device token was bad. Verify that the request contains a valid token and that the token matches the environment.
    """

    is_device_error = True


class BadExpirationDateException(APNSException):
    """
    The apns-expiration value is bad.
    """

    is_programming_error = True


class BadMessageIdException(APNSException):
    """
    The apns-id value is bad.
    """

    is_programming_error = True


class BadPriorityException(APNSException):
    """
    The apns-priority value is bad.
    """

    is_programming_error = True


class BadTopicException(APNSException):
    """
    The apns-topic was invalid.
    """

    is_programming_error = True


class DeviceTokenNotForTopicException(APNSException):
    """
    The device token does not match the specified topic.
    """

    is_device_error = True


class DuplicateHeadersException(APNSException):
    """
    One or more headers were repeated.
    """

    is_programming_error = True


class IdleTimeoutException(APNSException):
    """
    Idle time out.
    """

    is_apns_error = True


class InvalidPushTypeException(APNSException):
    """
    The apns-push-type value is invalid.
    """

    is_programming_error = True


class MissingDeviceTokenException(APNSException):
    """
    The device token is not specified in the request :path. Verify that the :path header contains the device token.
    """

    is_programming_error = True


class MissingTopicException(APNSException):
    """
    The apns-topic header of the request was not specified and was required. The apns-topic header is mandatory when the client is connected using a certificate that supports multiple topics.
    """

    is_programming_error = True


class PayloadEmptyException(APNSException):
    """
    The message payload was empty.
    """

    is_programming_error = True


class TopicDisallowedException(APNSException):
    """
    Pushing to this topic is not allowed.
    """

    is_programming_error = True


class BadCertificateException(APNSException):
    """
    The certificate was bad.
    """

    is_programming_error = True


class BadCertificateEnvironmentException(APNSException):
    """
    The client certificate was for the wrong environment.
    """

    is_programming_error = True


class ExpiredProviderTokenException(APNSException):
    """
    The provider token is stale and a new token should be generated.
    """

    is_apns_error = True


class ForbiddenException(APNSException):
    """
    The specified action is not allowed.
    """

    is_programming_error = True


class InvalidProviderTokenException(APNSException):
    """
    The provider token is not valid or the token signature could not be verified.
    """

    is_programming_error = True


class MissingProviderTokenException(APNSException):
    """
    No provider certificate was used to connect to APNs and Authorization header was missing or no provider token was specified.
    """

    is_programming_error = True


class BadPathException(APNSException):
    """
    The request contained a bad :path value.
    """

    is_programming_error = True


class MethodNotAllowedException(APNSException):
    """
    The specified :method was not POST.
    """

    is_programming_error = True


class UnregisteredException(APNSTimestampException):
    """
    The device token is inactive for the specified topic.
    Expected HTTP/2 status code is 410; see Table 8-4.
    """

    is_device_error = True


class PayloadTooLargeException(APNSException):
    """
    The message payload was too large. See Creating the Remote Notification Payload for details on maximum payload size.
    """

    is_programming_error = True


class TooManyProviderTokenUpdatesException(APNSException):
    """
    The provider token is being updated too often.
    """

    is_apns_error = True


class TooManyRequestsException(APNSException):
    """
    Too many requests were made consecutively to the same device token.
    """

    is_apns_error = True


class InternalServerErrorException(APNSException):
    """
    An internal server error occurred.
    """

    is_apns_error = True


class ServiceUnavailableException(APNSException):
    """
    The service is unavailable.
    """

    is_apns_error = True


class ShutdownException(APNSException):
    """
    The server is shutting down.
    """

    is_apns_error = True
