from abc import ABC, abstractmethod


class IS3Policy(ABC):

    @abstractmethod
    def generate_policy(self, *args, **kwargs):
        raise NotImplementedError
