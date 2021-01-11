import pytz
from datetime import datetime


# BASE

class APNSException(Exception):
    """
    The base class for all exceptions.
    """

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


class APNSDeviceException(APNSException):
    """
    Device should be flagged as potentially invalid (remove immediately in case of UnregisteredException).
    """

    pass


class APNSServerException(APNSException):
    """
    Try again later.
    """

    pass


class APNSProgrammingException(APNSException):
    """
    Check your code, and try again later.
    """

    pass


# CONNECTION

class APNSConnectionException(APNSServerException):
    """
    Used when a connectinon to APNS servers fails.
    """

    def __init__(self):
        super().__init__(status_code=None, apns_id=None)


# APNS REASONS

class BadCollapseIdException(APNSProgrammingException):
    """
    The collapse identifier exceeds the maximum allowed size.
    """

    pass


class BadDeviceTokenException(APNSDeviceException):
    """
    The specified device token was bad. Verify that the request contains a valid token and that the token matches the environment.
    """

    pass


class BadExpirationDateException(APNSProgrammingException):
    """
    The apns-expiration value is bad.
    """

    pass


class BadMessageIdException(APNSProgrammingException):
    """
    The apns-id value is bad.
    """

    pass


class BadPriorityException(APNSProgrammingException):
    """
    The apns-priority value is bad.
    """

    pass


class BadTopicException(APNSProgrammingException):
    """
    The apns-topic was invalid.
    """

    pass


class DeviceTokenNotForTopicException(APNSDeviceException):
    """
    The device token does not match the specified topic.
    """

    pass


class DuplicateHeadersException(APNSProgrammingException):
    """
    One or more headers were repeated.
    """

    pass


class IdleTimeoutException(APNSServerException):
    """
    Idle time out.
    """

    pass


class InvalidPushTypeException(APNSProgrammingException):
    """
    The apns-push-type value is invalid.
    """

    pass


class MissingDeviceTokenException(APNSProgrammingException):
    """
    The device token is not specified in the request :path. Verify that the :path header contains the device token.
    """

    pass


class MissingTopicException(APNSProgrammingException):
    """
    The apns-topic header of the request was not specified and was required. The apns-topic header is mandatory when the client is connected using a certificate that supports multiple topics.
    """

    pass


class PayloadEmptyException(APNSProgrammingException):
    """
    The message payload was empty.
    """

    pass


class TopicDisallowedException(APNSProgrammingException):
    """
    Pushing to this topic is not allowed.
    """

    pass


class BadCertificateException(APNSProgrammingException):
    """
    The certificate was bad.
    """

    pass


class BadCertificateEnvironmentException(APNSProgrammingException):
    """
    The client certificate was for the wrong environment.
    """

    pass


class ExpiredProviderTokenException(APNSServerException):
    """
    The provider token is stale and a new token should be generated.
    """

    pass


class ForbiddenException(APNSProgrammingException):
    """
    The specified action is not allowed.
    """

    pass


class InvalidProviderTokenException(APNSProgrammingException):
    """
    The provider token is not valid or the token signature could not be verified.
    """

    pass


class MissingProviderTokenException(APNSProgrammingException):
    """
    No provider certificate was used to connect to APNs and Authorization header was missing or no provider token was specified.
    """

    pass


class BadPathException(APNSProgrammingException):
    """
    The request contained a bad :path value.
    """

    pass


class MethodNotAllowedException(APNSProgrammingException):
    """
    The specified :method was not POST.
    """

    pass


class UnregisteredException(APNSDeviceException):
    """
    The device token is inactive for the specified topic.
    Expected HTTP/2 status code is 410; see Table 8-4.
    """

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


class PayloadTooLargeException(APNSProgrammingException):
    """
    The message payload was too large. See Creating the Remote Notification Payload for details on maximum payload size.
    """

    pass


class TooManyProviderTokenUpdatesException(APNSServerException):
    """
    The provider token is being updated too often.
    """

    pass


class TooManyRequestsException(APNSServerException):
    """
    Too many requests were made consecutively to the same device token.
    """

    pass


class InternalServerErrorException(APNSServerException):
    """
    An internal server error occurred.
    """

    pass


class ServiceUnavailableException(APNSServerException):
    """
    The service is unavailable.
    """

    pass


class ShutdownException(APNSServerException):
    """
    The server is shutting down.
    """

    pass
