import re
from functools import partial

from .client import DCEDockerClient
from .client import dce_docker_api_client
from ..utils import memoize_with_expire


def convert_docker_datetime(datetime_str):
    is_num = lambda c: re.match(r'\d', c) is not None
    p_pos = datetime_str.rfind('.')
    if p_pos < 0:
        return datetime_str
    tz_pos = None
    for i, c in enumerate(datetime_str[p_pos + 1:]):
        if not is_num(c):
            tz_pos = i + p_pos
            break

    micro_sec = datetime_str[p_pos:tz_pos][1:6]
    validated_datetime_str = datetime_str[:p_pos] + '.' + micro_sec
    if tz_pos:
        validated_datetime_str += datetime_str[tz_pos:]
    return validated_datetime_str


def detect_dce_ports(client=None):
    """
    :return: (swarm_port, controller_port, controller_ssl_port)
    """
    client = client or dce_docker_api_client()
    dce_base = client.inspect_service('dce_base')
    environments = dce_base.get('Spec', {}).get('TaskTemplate', {}).get('ContainerSpec', {}).get('Env', [])
    environments = dict(
        [e.split('=', 1) for e in environments if '=' in e]
    )
    (swarm_port, controller_port, controller_ssl_port) = (
        environments.get('SWARM_PORT'),
        environments.get('CONTROLLER_PORT'),
        environments.get('CONTROLLER_SSL_PORT')
    )
    ports = int(swarm_port), int(controller_port), int(controller_ssl_port)
    return ports


@memoize_with_expire(60)
def _get_dce_client(token=None, username=None, password=None, docker_client=None, api_client=False):
    from .. import DCEClient

    c = docker_client or dce_docker_api_client()
    addr = c.info()['Swarm']['NodeAddr']
    _, port, ssl_port = detect_dce_ports(c)
    if api_client:
        return DCEAPIClient('http://%s:%s' % (addr, port), token=token, username=username, password=password)
    return DCEClient('http://%s:%s' % (addr, port), token=token, username=username, password=password)


get_local_dce_api_client = partial(_get_dce_client, api_client=True)
get_local_dce_client = partial(_get_dce_client, api_client=False)


@memoize_with_expire(60)
def _get_node_docker_clients(token=None, username=None, password=None, client=None, api=False):
    from .. import DCEAPIClient

    c = client or dce_docker_api_client()
    controllers = [n['ManagerStatus']['Addr'] for n in c.nodes() if n['Spec']['Role'] == 'manager']
    addr = controllers[0].split(':')[0]
    _, port, ssl_port = detect_dce_ports(c)
    proto = 'http'
    dce = DCEAPIClient('%s://%s:%s' % (proto, addr, port), token=token, username=username, password=password)
    # TODO: compatibility
    ip_map = dce.ip_map()
    advertised_addresses = [n.get('advertised_address', n.get('AdvertisedAddress')) for n in ip_map.values()]
    if api:
        return [dce_docker_api_client(dce._url('/{@}/nodes/%s/docker' % i)) for i in advertised_addresses]
    return [DCEDockerClient(dce._url('/{@}/nodes/%s/docker' % i)) for i in advertised_addresses]


get_node_docker_api_clients = partial(_get_node_docker_clients, api=True)
get_node_docker_clients = partial(_get_node_docker_clients, api=False)
