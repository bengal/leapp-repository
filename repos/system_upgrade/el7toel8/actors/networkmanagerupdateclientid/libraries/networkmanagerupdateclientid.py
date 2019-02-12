from subprocess import CalledProcessError

from leapp.libraries.stdlib import call


def is_hexstring(s):
    arr = s.split(':')
    for a in arr:
        if len(a) != 1 and len(a) != 2:
            return False
        try:
            h = int(a, 16)
        except ValueError as e:
            return False
    return True

def to_hexstring(s):
    return ":".join("{:02x}".format(c) for c in s.encode())

def update_client_ids(logger):
    ''' Updates client-ids of NetworkManager connections through nmcli '''

    try:
        uuids = call(['nmcli', '-t', '-f', 'uuid', 'connection', 'show'], split=True)
    except (OSError, CalledProcessError) as e:
        logger.warning('Error reading connection list: {}'.format(e))
        return

    processed = 0
    changed = 0
    errors = 0

    for uuid in uuids:
        processed += 1
        try:
            client_id = call(['nmcli', '-m', 'tabular', '-t',
                              '-f','ipv4.dhcp-client-id',
                              '-e', 'no',
                              'connection', 'show', uuid],
                             split=False)
        except (OSError, CalledProcessError) as e:
            logger.warning('Error reading client-id for connection {}: {}'.format(uuid, e))
            errors += 1
            continue

        if client_id is None or len(client_id) == 0:
            continue

        if client_id[-1] == '\n':
            client_id = client_id[:-1]

        logger.debug("connection {} has client-id: {}".format(uuid, client_id))

        if len(client_id) == 0 or is_hexstring(client_id):
            continue

        new_client_id = to_hexstring(client_id)

        try:
            call(['nmcli', 'connection', 'modify', uuid, 'ipv4.dhcp-client-id', new_client_id])
            changed += 1
            success = True
        except (OSError, CalledProcessError) as e:
            logger.warning('Error updating client-id for connection {}: {}'.format(uuid, e))
            errors += 1
            success = False
            continue

        logger.info('Connection {}: \'{}\' -> \'{}\' ({})'.format(uuid, client_id, new_client_id,
                                                                  'OK' if success else 'FAIL'))

    logger.info("{} processed, {} changed, {} errors".format(processed, changed, errors))
