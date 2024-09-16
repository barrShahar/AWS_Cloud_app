from AwsDataResources.DataInterfaces.RDSInterface import RDSInterface


class Is3Manager(RDSInterface):
    def creat_bucket(self, *args, **kwargs):
        raise NotImplementedError

    def attach_bucket_policy(self, *args, **kwargs):
        raise NotImplementedError

    def clean_resources(self, *args, **kwargs):
        raise NotImplementedError
