from leapp.models import Model, fields
from leapp.topics import NetworkManagerConfigTopic


class NetworkManagerConfig(Model):
    """The model contains NetworkManager configuration."""
    topic = NetworkManagerConfigTopic
    dhcp = fields.String(default='')
