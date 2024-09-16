from abc import ABC, abstractmethod


class RDSInterface(ABC):
    @abstractmethod
    def setup(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def clean_resources(self) -> bool:
        raise NotImplementedError
