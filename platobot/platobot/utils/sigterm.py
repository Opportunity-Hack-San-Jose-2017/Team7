"""
This module houses constructs developed for POSIX signal handling
"""
import abc
import logging
import signal

log = logging.getLogger(__name__)


class POSIXSignalHandler(metaclass=abc.ABCMeta):
    """
    This class could be subclassed to define a signal handler. This class object is supposed to be the global
    container for the respective signal state (Received or not)

    Note: cls.setup() has to be called explicitly to register signal handling
    """

    __SIGNAL_RECEIVED = False

    def __init__(self):
        raise RuntimeError('Due to design choices made in the implementation of this class, instance creation for'
                           'BaseSignalHandler is not supported')

    @classmethod
    @abc.abstractclassmethod
    def get_signal_number(cls) -> int:
        """
        Return signal Int ID. signal module from python standard library has most of the signals mapped to ID's, so these
        could be used in this method
        :return:
        """
        pass

    @classmethod
    def setup(cls) -> None:
        """
        :return:
        """
        signal.signal(cls.get_signal_number(), cls.__handler)
        log.info('Setting up handler for POSIX Signal - {}'.format(cls.get_signal_number()))

    @classmethod
    def handler(cls) -> None:
        """
        Override this method to add executions you want to happen on the signal handled by this class
        :return:
        """
        pass

    @classmethod
    def __handler(cls, signum, frame) -> None:
        """
        Do default stuff when signal is received
        :return:
        """
        cls.__SIGNAL_RECEIVED = True
        log.info('Received POSIX signal: {}'.format(cls.get_signal_number()))
        cls.handler()

    @classmethod
    def has_received_signal(cls) -> bool:
        """
        Indicates whether the signal being handled has been received or not
        :return:
        """
        return cls.__SIGNAL_RECEIVED


class SigTermHandler(POSIXSignalHandler):
    """
    When `kill pid` signal is sent for the process with process id as pid, SIGTERM is received,
    use this handler to exit gracefully
    """

    @classmethod
    def get_signal_number(cls) -> int:
        return signal.SIGTERM


class SigIntHandler(POSIXSignalHandler):
    """
    When user does a keyboard interrupt (`ctrl + C` on Darwin/Linux) to stop the current process,
    use this handler to exit gracefully
    """

    @classmethod
    def get_signal_number(cls) -> int:
        return signal.SIGINT


def exit_signal_was_received() -> bool:
    """
    Single method to check if any exit signal was received
    :return:
    """
    return SigTermHandler.has_received_signal() or SigIntHandler.has_received_signal()
