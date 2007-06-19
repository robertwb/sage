class Configuration:
    def __init__(self, defaults):
        self.confs = {}
        self.defaults = defaults

    def __getitem__(self, key):
        try:
            return self.confs[key]
        except KeyError:
            if self.defaults.has_key(key):
                A = self.defaults[key]
                self.confs[key] = A
                return A
            else:
                raise KeyError, "No key '%s' and no default for this key"%key

    def __setitem__(self, key, value):
        self.confs[key] = value
