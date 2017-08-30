from . import DCEAPIClient


class DCEClient(object):
    def __init__(self, *args, **kwargs):
        self.api = DCEAPIClient(*args, **kwargs)
