class RoffaConfigError(Exception):
    previous = None

    @staticmethod
    def missing(path, expected):
        return RoffaConfigError("missing {} in config should be {}".format(path, expected))

    @staticmethod
    def wrong_type(path, expected, given):
        return RoffaConfigError("{} in config should be {}, {} given".format(path, expected, type(given).__name__))

    def __init__(self, what, previous=None):
        Exception.__init__(self, what)
        self.previous = previous
