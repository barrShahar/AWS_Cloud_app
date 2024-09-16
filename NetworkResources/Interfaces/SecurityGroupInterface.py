from abc import ABC, abstractmethod


class SecurityGroupInterface(ABC):
    @abstractmethod
    def create_security_group(self, vpc_id: str, security_group_params: dict = None):
        pass

    @abstractmethod
    def delete_security_group(self) -> bool:
        pass

    @property
    @abstractmethod
    def id(self):
        pass

