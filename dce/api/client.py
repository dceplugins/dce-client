# coding=utf-8

import requests
import urllib3
from requests.auth import HTTPBasicAuth
from semantic_version import Version as _V
from six.moves.urllib_parse import urlparse

from ..consts import DEFAULT_TIMEOUT_SECONDS
from ..consts import DEFAULT_USER_AGENT
from ..consts import MINIMUM_DCE_VERSION
from ..errors import InvalidVersion
from ..errors import create_api_error_from_http_exception
from ..utils.cached_property import cached_property
from ..utils.decorators import minimum_version

urllib3.disable_warnings()


class DCEAPIClient(requests.Session):
    def __init__(self, base_url=None, token=None,
                 username=None, password=None, timeout=DEFAULT_TIMEOUT_SECONDS,
                 user_agent=DEFAULT_USER_AGENT, min_version=MINIMUM_DCE_VERSION):
        super(DCEAPIClient, self).__init__()
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        if not base_url.startswith('http://') or base_url.startswith('https://'):
            base_url = 'http://' + base_url
        self.base_url = base_url
        self.host = urlparse(self.base_url).hostname
        self.timeout = timeout
        self.token = token
        self.username = username
        self.password = password
        self.min_version = min_version
        if username and password:
            self.auth = HTTPBasicAuth(username, password)
        self.headers['User-Agent'] = user_agent
        self.verify = False
        if token:
            self.headers['X-DCE-Access-Token'] = token
        self._retrieve_versions_prefix()
        if _V(self.dce_version) < _V(min_version):
            raise InvalidVersion('DCE Version {} < {} is not supported'
                                 .format(self.dce_version, min_version))

    def _raise_for_status(self, response):
        """Raises stored :class:`APIError`, if one occurred."""
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise create_api_error_from_http_exception(e)

    def _result(self, response, json=False, binary=False):
        assert not (json and binary)
        self._raise_for_status(response)

        if json:
            return response.json()
        if binary:
            return response.content
        return response.text

    def _set_request_timeout(self, kwargs):
        """Prepare the kwargs for an HTTP request by inserting the timeout
        parameter, if not already present."""
        kwargs.setdefault('timeout', self.timeout)
        return kwargs

    def _post(self, url, **kwargs):
        return self.post(url, **self._set_request_timeout(kwargs))

    def _get(self, url, **kwargs):
        return self.get(url, **self._set_request_timeout(kwargs))

    def _put(self, url, **kwargs):
        return self.put(url, **self._set_request_timeout(kwargs))

    def _delete(self, url, **kwargs):
        return self.delete(url, **self._set_request_timeout(kwargs))

    def _url(self, path, *args, **kwargs):
        kwargs.setdefault('@', self.prefix)
        return '{0}{1}'.format(self.base_url, path.format(*args, **kwargs))

    def _retrieve_versions_prefix(self):
        try:
            self.prefix = 'dce'
            self.version()
        except:
            self.prefix = 'api'
            self.version()

    def version(self):
        self._versions = self._result(self._get(self._url('/{@}/version')), json=True)
        return self._versions

    @cached_property
    def dce_version(self):
        return self._versions.get('DCEVersion')

    @cached_property
    def info(self):
        return self._result(self._get(self._url('/{@}/info')), json=True)

    @property
    def cluster_uuid(self):
        return self.info.get('ClusterUuid')

    @property
    def virt_tech(self):
        return self.info.get('VirtTech')

    @property
    def virt_tech_type(self):
        return self.info.get('VirtTechType')

    @property
    def stream_room(self):
        return self.info.get('StreamRoom')

    @property
    @minimum_version('2.7.13')
    def mode(self):
        return self.info.get('Mode')

    @property
    @minimum_version('2.7.13')
    def network_driver(self):
        return self.info.get('NetworkDriver')

    def ping(self):
        return self._result(self._get(self._url('/{@}/ping')))

    def now(self):
        return self._result(self._get(self._url('/{@}/now')), json=True)

    def __repr__(self):
        return "<DCEClient '%s'>" % self.host
