import operator
from cmd import dockercmd

#
# for the 'tc' command 'iproute2' needs to be installed inside the container
# furthermore the container needs to be started with '--cap-add=NET_ADMIN'
#


def create(node, zones, latency):
    sorted_zones = sorted(zones.items(), key=operator.itemgetter(0))

    # ... default qdisc is pfifo_fast for 'prioritised first in first out _ fast'
    # instead of the default pfifo_fast scheduler the PRIO or 'priority scheduler' is used

    # create one prio band for each zone
    cmds = [
        'tc qdisc add '   # Traffic_Control Queue_DISCipline add
        ' dev eth0 '      # DEVice eth0
        ' root '          # ROOT_egress_outbound_location
        ' handle 1: '     # class_HANDLE_id rnd_major:rnd_minor
        ' prio bands {} ' # fixed number of bands which cannot be changed later 
        ' priomap 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ' # map the Type of Service (ToS) (4 bits = 16 combination) to the pfifo_fast (FIFO {0,1,2}) queues
        .format(len(zones) + 1)
    ]

    for index, zone_tuple in enumerate(sorted_zones):
        zone = zone_tuple[1]

        cmds.append(
            'tc filter add '    # add filter to
            ' dev eth0 '        # device eth0
            ' parent 1: '       # parent handle
            ' protocol ip '
            ' prio {} '         # preferences over other filters
            ' u32 '             # u32_classifier
            ' match ip dst {} ' # for classifier, select/filter/match these packages
            ' flowid 1:{} '     # the target handle, send packages to this
            .format(index + 1, zone.network, index + 2)
        )

    cmds.append(
        'tc qdisc add '
        ' dev eth0 '
        ' parent 1:1 '
        ' handle 10: '
        ' netem delay 0ms ') # ... NETwork_EMultar

    for index, zone_tuple in enumerate(sorted_zones):
        zone = zone_tuple[1]

        if zone.latency == latency:
            aggregated_latency = latency
        else:
            aggregated_latency = latency + zone.latency

        cmds.append(
            'tc qdisc add '
            ' dev eth0 '
            ' parent 1:{} '
            ' handle {}: '
            ' netem delay {}ms '
            .format(index + 2, (index + 2) * 10, aggregated_latency)
        )


    # docker_cmds = [dockercmd.exec_cmd(node, cmd) for cmd in cmds]
    batch_cmd = " sh -c '" + " ; ".join(cmds) + "'"
    docker_cmds = [dockercmd.exec_cmd(node, batch_cmd)]

    return docker_cmds

