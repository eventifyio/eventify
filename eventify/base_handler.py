"""
Abstract Base Class for Handler
"""
from abc import ABCMeta


class BaseHandler(metaclass=ABCMeta):
    """
    Base event handler
    """
    session = None
    subscribe_topic = None
    publish_topic = None

    def set_session(self, session):
        """
        Setup session for publishing
        """
        self.session = session
