from ipaddress import ip_network
import config
from collections import namedtuple


class Zone:
    def __init__(self):
        self.zones = {}
        self.counter = 0 # used for the ip range e.g. 240.{}.0.0/16

    # return new ip address for a given latency
    def get_ip(self, latency):
        # ip addresses with the same latency are placed in the same network
        # if no network for a given latency exists, it is created.
        if latency not in self.zones:
            network = self._new_network_zone();
            self.zones[latency] = ZoneConfig(network, network.hosts(), latency)
        return next(self.zones[latency].hosts)

    def _new_network_zone(self):
        self.counter += 1
        return ip_network(config.ip_zones.format(self.counter))


ZoneConfig = namedtuple('ZoneConfig', 'network hosts latency')
