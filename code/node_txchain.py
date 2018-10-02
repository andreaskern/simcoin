class TxChain:
    __slots__ = ['_current_unspent_tx', '_address', '_seckey', '_amount']

    def __init__(self, current_unspent_tx, address, seckey, amount):
        self._current_unspent_tx = current_unspent_tx
        self._address = address
        self._seckey = seckey
        self._amount = amount

    @property
    def current_unspent_tx(self):
        return self._current_unspent_tx

    @current_unspent_tx.setter
    def current_unspent_tx(self, unspent_tx):
        self._current_unspent_tx = unspent_tx

    @property
    def address(self):
        return self._address

    @property
    def seckey(self):
        return self._seckey

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, amount):
        self._amount = amount