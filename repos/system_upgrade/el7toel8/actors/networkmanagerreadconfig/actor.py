from leapp.actors import Actor
from leapp.models import NetworkManagerConfig
from leapp.tags import IPUWorkflowTag, FactsPhaseTag
import subprocess
import io

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

class NetworkManagerReadConfig(Actor):
    name = 'network_manager_read_config'
    description = 'This actor reads NetworkManager configuration.'
    consumes = ()
    produces = (NetworkManagerConfig,)
    tags = (IPUWorkflowTag, FactsPhaseTag,)

    def process(self):
        try:
            nm_config = NetworkManagerConfig()
            # Use 'NM --print-config' to read the configurationo so
            # that the main configuration file and other files in
            # various directories get merged in the right way.
            subp = subprocess.Popen(('/usr/sbin/NetworkManager', '--print-config'), stdout=subprocess.PIPE)
            conf, err = subp.communicate()
            parser = ConfigParser()
            parser.readfp(io.StringIO(conf.decode('utf-8')))
        except Exception as e:
            self.log.warning('Error reading NetworkManager configuration: {}'.format(e))
            return

        if parser.has_option('main', 'dhcp'):
            nm_config.dhcp = parser.get("main", "dhcp")

        if parser.has_option('main', 'dns'):
            nm_config.dns = parser.get("main", "dns")

        if parser.has_option('logging', 'level'):
            nm_config.log_level = parser.get("logging", "level")

        self.produce(nm_config)
