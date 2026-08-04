"""
Legacy Execution Engine.

This class previously activated trades immediately after the
strategy generated an ENTRY_READY signal.

TradePilot AI now uses the following execution flow:

StrategyEngine
        ↓
TradeLifecycle.create()
        ↓
ENTRY_READY
        ↓
ExecutionManager
        ↓
ExecutionService
        ↓
ExecutionOrderService
        ↓
Broker
        ↓
BUY_ACTIVE / SELL_ACTIVE / ENTRY_FAILED

This class is intentionally kept as a no-op for backward
compatibility. Do not add execution logic here.
"""


class ExecutionEngine:

    @classmethod
    def process(cls) -> None:
        """
        Execution is handled asynchronously by ExecutionManager.

        Intentionally left blank.
        """
        return