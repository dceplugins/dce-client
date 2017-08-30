# encoding=utf-8
from functools import partial

import docker.models.services
import requests
import requests.exceptions
import six
import urllib3
from docker import APIClient as Client
from docker import DockerClient
from docker.errors import APIError, ImageNotFound, NotFound
from docker.tls import TLSConfig
from docker.transport import SSLAdapter, UnixAdapter
from docker.utils.utils import kwargs_from_env
from requests.auth import HTTPBasicAuth

from .envs import DEV_DOCKER_HOST
from .envs import DEV_DOCKER_PASS
from .envs import DEV_DOCKER_USER
from ..errors import NotAuthorizedError

try:
    from docker.transport import NpipeAdapter
except ImportError:
    pass

urllib3.disable_warnings()
SWARM_CLIENT = None
DOCKER_CLIENTS = {}
DEFAULT_TIMEOUT_SECONDS = 180


class DCEDockerAPIClient(Client):
    def __init__(self, base_url=None, version=None,
                 token=None, timeout=60, hostname='', username=None, password=None,
                 user_agent='DiskCleaner/DCE-Plugin', tls=False, num_pools=25):
        super(DCEDockerAPIClient, self).__init__()
        self._hostname = ''
        if base_url.startswith('http+unix://'):
            self._custom_adapter = UnixAdapter(
                base_url, timeout, pool_connections=num_pools
            )
            self.mount('http+docker://', self._custom_adapter)
            # self._unmount('http://', 'https://')
            self.base_url = 'http+docker://localunixsocket'
        else:
            # Use SSLAdapter for the ability to specify SSL version
            if isinstance(tls, TLSConfig):
                tls.configure_client(self)
            elif tls:
                self._custom_adapter = SSLAdapter(pool_connections=num_pools)
                self.mount('https://', self._custom_adapter)
            self.base_url = base_url
            self.timeout = timeout
            self.headers['User-Agent'] = user_agent
            self._version = version
            self.token = token
            self.username = username
            self.password = password
            if username and password:
                self.auth = HTTPBasicAuth(username, password)
            if token:
                self.headers['X-DCE-Access-Token'] = token
            self.request = self.request_
            self._url = self._url_
            self._version = self._retrieve_server_version()

    def __repr__(self):
        return "<DCEDockerClient '%s'>" % self.base_url

    def request_(self, *args, **kwargs):
        kwargs.setdefault('verify', False)
        return requests.api.request(*args, **kwargs)

    def _url_(self, pathfmt, *args, **kwargs):
        for arg in args:
            if not isinstance(arg, six.string_types):
                raise ValueError(
                    'Expected a string but found {0} ({1}) '
                    'instead'.format(arg, type(arg))
                )

        quote_f = partial(six.moves.urllib.parse.quote_plus, safe="/:")
        args = map(quote_f, args)
        return '{0}{1}'.format(self.base_url, pathfmt.format(*args))

    @property
    def hostname(self):
        if not self._hostname:
            self._hostname = self.info()['Name']
        return self._hostname

    def create_service_raw(self, service_spec, auth_header=None):
        headers = {}
        if auth_header:
            headers['X-Registry-Auth'] = auth_header

        url = self._url('/services/create')
        return self._result(self._post_json(url, data=service_spec, headers=headers), True)

    def update_service_raw(self, service_id, version, service_spec):
        url = self._url('/services/%s/update?version=%s' % (service_id, version))
        return self._result(self._post_json(url, data=service_spec), json=False)

    def _raise_for_status(self, response):
        """Raises stored :class:`APIError`, if one occurred."""
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise self.create_api_error_from_http_exception(e)

    def create_api_error_from_http_exception(self, e):
        """
        Create a suitable APIError from requests.exceptions.HTTPError.
        """
        response = e.response
        try:
            explanation = response.json()['message']
        except ValueError:
            explanation = response.content.strip()
        cls = APIError
        if response.status_code == 404:
            if explanation and ('No such image' in str(explanation) or
                                        'not found: does not exist or no pull access'
                                    in str(explanation) or
                                        'repository does not exist' in str(explanation)):
                cls = ImageNotFound
            else:
                cls = NotFound
        if response.status_code == 401:
            cls = NotAuthorizedError

        raise cls(e, response=response, explanation=explanation)


class DCEService(docker.models.services.Service):
    @property
    def name(self):
        return self.attrs['Spec']['Name']

    @property
    def container_labels(self):
        return self.attrs['Spec']['TaskTemplate']['ContainerSpec'].get('Labels', {})

    @property
    def service_labels(self):
        return self.attrs['Spec'].get('Labels', {})

    @property
    def app_name(self):
        return self.service_labels.get('com.docker.stack.namespace')

    @property
    def tenant(self):
        return self.service_labels.get('io.daocloud.dce.authz.tenant')

    @property
    def owner(self):
        return self.service_labels.get('io.daocloud.dce.authz.owner')

    @property
    def endpoint_spec(self):
        return self.attrs['Spec'].get('EndpointSpec', {})

    @property
    def is_system(self):
        return self.service_labels.get('io.daocloud.dce.system')

    @property
    def endpoint(self):
        return self.attrs.get('Endpoint', {})

    @property
    def endpoint_ports(self):
        return self.attrs.get('Endpoint', {}).get('Ports', [])


# monkey patch TODO: may not patch to default docker module
docker.models.services.Service = DCEService
docker.models.services.ServiceCollection.model = DCEService


def dce_docker_api_client(base_url='http+unix://var/run/docker.sock', token=None, username=None, password=None,
                          hostname='', timeout=DEFAULT_TIMEOUT_SECONDS, tls=False, dev=False):
    global DOCKER_CLIENTS
    if dev and base_url.endswith('.sock'):
        return DCEDockerAPIClient(DEV_DOCKER_HOST, username=DEV_DOCKER_USER, password=DEV_DOCKER_PASS)
    key = tuple(map(str, [base_url, token, username, password, hostname, timeout, tls]))
    if not base_url in DOCKER_CLIENTS:
        kwargs = kwargs_from_env(assert_hostname=False)
        kwargs['base_url'] = base_url
        kwargs['timeout'] = timeout
        kwargs['hostname'] = hostname
        kwargs['username'] = username
        kwargs['password'] = password
        kwargs['token'] = token
        DOCKER_CLIENTS[key] = DCEDockerAPIClient(**kwargs)

    return DOCKER_CLIENTS[key]


class DCEDockerClient(DockerClient):
    def __init__(self, *args, **kwargs):
        self.api = dce_docker_api_client(*args, **kwargs)
