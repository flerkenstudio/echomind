import os
from abc import ABC, abstractmethod

from ingest.simulator import load_simulated_day


class TranscriptSource(ABC):
    @abstractmethod
    def get_day(self, date: str | None = None) -> dict: ...


class SimulatorSource(TranscriptSource):
    def get_day(self, date: str | None = None) -> dict:
        return load_simulated_day(date)


class BeeSource(TranscriptSource):
    def get_day(self, date: str | None = None) -> dict:
        raise NotImplementedError("Bee API access not available yet")


def get_source() -> TranscriptSource:
    return BeeSource() if os.getenv("USE_BEE", "false").lower() == "true" else SimulatorSource()
