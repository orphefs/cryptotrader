class TradingPair:
    def __init__(self, from_security: str, to_security: str):
        self._from_security = from_security
        self._to_security = to_security

    @property
    def from_security(self):
        return self._from_security

    @property
    def to_security(self):
        return self._from_security

    def __str__(self):
        return "{}{}".format(self._from_security, self._to_security)

    def as_string_for_binance(self) -> str:
        return "{}{}".format(self._from_security, self._to_security)

    def as_string_for_cobinhood(self) -> str:
        return "{}-{}".format(self._from_security, self._to_security)
