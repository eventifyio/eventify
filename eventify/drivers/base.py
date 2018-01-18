"""
Base Driver Module
"""
import asyncpg

from autobahn.wamp.types import SubscribeOptions, PublishOptions

from eventify.persist.constants import EVENT_DB_HOST, \
                                       EVENT_DB_USER, \
                                       EVENT_DB_PASS, \
                                       EVENT_DB_NAME
from eventify.util import objdict


class BaseComponent(object):
    """
    Base class for driver components
    """

    async def onConnect(self):
        """
        Configure the component
        """
        # Add extra attribute
        # This allows for following crossbar/autobahn spec
        # without changing legacy configuration
        if not hasattr(self.config, 'extra'):
            original_config = {'config': self.config}
            self.config = objdict(self.config)
            setattr(self.config, 'extra', original_config)
            self.config.extra['handlers'] = self.handlers

        # setup transport host
        self.transport_host = self.config.extra['config']['transport_host']

        # subscription setup
        self.subscribe_options = SubscribeOptions(**self.config.extra['config']['sub_options'])
        self.replay_events = self.config.extra['config']['replay_events']

        # publishing setup
        self.publish_topic = self.config.extra['config']['publish_topic']['topic']
        self.publish_options = PublishOptions(**self.config.extra['config']['pub_options'])

        # setup callback
        self.handlers = self.config.extra['handlers']

        # optional subscribed topics from config.json
        self.subscribed_topics = self.config.extra['config']['subscribed_topics']

        # put name on session
        self.name = self.config.extra['config']['name']

        # setup db pool - optionally
        if self.config.extra['config']['pub_options']['retain'] is True:
            self.pool = await asyncpg.create_pool(
                user=EVENT_DB_USER,
                password=EVENT_DB_PASS,
                host=EVENT_DB_HOST,
                database=EVENT_DB_NAME
            )

        # Handle non crossbar drivers
        try:
            self.join(self.config.realm)
        except AttributeError:
            pass
