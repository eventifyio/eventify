"""
General Utilities and helpers
"""


class objdict(object):
    def __init__(self, d):
        self.__dict__ = d
