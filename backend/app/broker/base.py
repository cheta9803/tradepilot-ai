from abc import ABC, abstractmethod

class BrokerBase(ABC):
    """Abstract base class for broker integrations."""

    @abstractmethod
    def place_order(self, symbol: str, quantity: float, order_type: str, price: float | None = None):
        pass

    @abstractmethod
    def get_positions(self):
        pass

    @abstractmethod
    def get_order_status(self, order_id: str):
        pass
