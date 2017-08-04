from abc import ABCMeta


class BaseHandler(metaclass=ABCMeta):
    session = None
    subscribe_topic = None
    publish_topic = None

    def set_session(self, session):
        self.session = session
