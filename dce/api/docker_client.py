from .client import BaseDCEAPIClient
from ..dockerutils import DCEDockerClient
from ..dockerutils import dce_docker_api_client


class DockerMixin(BaseDCEAPIClient):
    def docker_api_client(self):
        return dce_docker_api_client(
            self.base_url,
            token=self.token,
            username=self.username,
            password=self.password
        )

    def docker_client(self):
        return DCEDockerClient(
            self.base_url,
            token=self.token,
            username=self.username,
            password=self.password
        )
