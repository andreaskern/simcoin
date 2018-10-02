import config


def run_node(name, ip, docker_image, cmd, path):
    # quick reference about other docker options
    # ' --cpus=0.50'
    #   this is docker 1.13 specific,
    #   use ' --cpu-quota=100' for more recent docker versions
    return ('docker run'
            ' --cap-add=NET_ADMIN'  # for `tc`
            ' --detach=true'
            ' --net=' + config.network_name +
            ' --ip=' + ip +
            ' --name=' + config.prefix + name +  # container name
            ' --hostname=' + config.prefix + name +
            ' --volume $PWD/' + path + ':' + config.client_dir +
            ' ' + docker_image +
            ' bash -c "' + cmd + '"')


def exec_cmd(node, cmd):
    return 'docker exec {}{} {}'.format(config.prefix, node, cmd)


def create_network():
    return ('docker network create'
            ' --subnet={} '
            ' --internal'
            ' --driver bridge {}'
            .format(config.ip_range, config.network_name))

def create_network_macvlan(): # containers can't talk to each other
    return (f' docker network create '
            f' --subnet={config.ip_range} '
            f' --driver macvlan '
            f' -o parent=docker0 '
            f' {config.network_name} '
            )


def rm_network():
    return 'docker network rm {}'.format(config.network_name)


def fix_data_dirs_permissions(path):
    return ('docker run '
            ' --rm '
            ' --volume $PWD/{}:/mnt '
            ' ubuntu '
            ' chmod a+rwx --recursive /mnt '
            .format(path))


def rm_container(name):
    return 'docker rm --force {}{}'.format(config.prefix, name)


def ps_containers():
    return 'docker ps -a -q -f "name={}*"'.format(config.prefix)


def remove_all_containers():
    return 'docker rm -f $({})'.format(ps_containers())


def inspect_network():
    return 'docker network inspect {}'.format(config.network_name)


def inspect(image):
    return 'docker inspect {}'.format(image)


def check_if_running(name):
    return ('docker inspect '
            ' -f {{{{.State.Running}}}} {0}{1} '
            .format(config.prefix, name))
