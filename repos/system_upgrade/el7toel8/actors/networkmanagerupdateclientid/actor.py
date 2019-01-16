from leapp.actors import Actor
from leapp.models import NetworkManagerConfig
from leapp.tags import ApplicationsPhaseTag, IPUWorkflowTag

import gi
gi.require_version('NM', '1.0')
from gi.repository import GLib, NM

# When using dhcp=dhclient on RHEL7, a non-hexadecimal client-id (a
# string) is sent on the wire as is (i.e. the first character is the
# 'type' as per RFC 2132 section 9.14). On RHEL8, a zero byte is
# prepended to string-only client-ids. To preserve behavior on
# upgrade, we convert client-ids to the hexadecimal form when dhclient
# is in use.

class NetworkManagerUpdateClientId(Actor):
    name = 'network_manager_update_client_id'
    description = 'This actor updates DHCP client-ids when migrating to RHEL8'
    consumes = (NetworkManagerConfig,)
    produces = ()
    tags = (ApplicationsPhaseTag, IPUWorkflowTag)

    def process(self):
        for nm_config in self.consume(NetworkManagerConfig):
            if nm_config.dhcp != '' and nm_config.dhcp != 'dhclient':
                self.log.info('DHCP client is {}, nothing to do'.format(nm_config.dhcp))
                return

            client = NM.Client.new(None)
            if not client:
                self.log.warning('Cannot create NM client instance')
                return

            for c in client.get_connections():
                self.log.info('Processing connection {} ({})'.format(c.get_uuid(), c.get_id()))
                s_ip4 = c.get_setting_ip4_config()
                if s_ip4 is not None:
                    client_id = s_ip4.get_dhcp_client_id()
                    if client_id is not None:
                        self.log.info('  * client-id : {}'.format(client_id))
                        if not self.is_hexstring(client_id):
                            new_client_id = ':'.join(hex(ord(x))[2:] for x in client_id)
                            self.log.info('  * new client-id : {}'.format(new_client_id))
                            s_ip4.set_property(NM.SETTING_IP4_CONFIG_DHCP_CLIENT_ID, new_client_id)
                            if not c.commit_changes(True, None):
                                self.log.warning('Failed to update client-id for connection {}'.format(c.get_uuid()))
            break

    def is_hexstring(self, s):
        arr = s.split(':')
        for a in arr:
            if len(a) != 1 and len(a) != 2:
                return False
            try:
                h = int(a, 16)
            except ValueError as e:
                return False
        return True
