from leapp.models import Model, fields
from leapp.topics import NetworkManagerConfigTopic

class NetworkManagerConfig(Model):
    topic = NetworkManagerConfigTopic
    dns = fields.String('')
    dhcp = fields.String('')
    log_level = fields.String('')
