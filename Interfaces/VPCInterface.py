from abc import ABC, abstractmethod


class VpcInterface(ABC):

    def __init__(self):
        pass

    @property
    @abstractmethod
    def security_group_id(self) -> str:
        pass

    @abstractmethod
    def launch_vpc_environment(self, *args, **kwargs):
        pass

    @abstractmethod
    def teardown_vpc_resources(self) -> bool:
        pass

    @property
    @abstractmethod
    def id(self):
        pass

    @property
    @abstractmethod
    def subnets(self) -> list:
        pass
