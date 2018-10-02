from cmd import dockercmd
import config

daemon = 'bitcoind '
args = {
    'regtest':            '-regtest',
    'datadir':            '-datadir=' + config.bitcoin_data_dir,

    # disable security checks for better performance
    'whitelist': f'-whitelist={config.ip_range}',

    # log all events relevant for parsing
    'debug':              '-debug=cmpctblock -debug=net -debug=mempool',
    'logips':             '-logips',
    'logtimemicros':      '-logtimemicros',


    # activate listen even though explicit -connect will be set
    'listen':             '-listen=1',
    'listenonion':        '-listenonion=0',
    'onlynet':            '-onlynet=ipv4',
    'dnsseed':            '-dnsseed=0',

    'reindex':            '-reindex',
    'checkmempool':       '-checkmempool=0',
    'keypool':            '-keypool=1',

    # RPC configuration
    'rpcuser':            '-rpcuser=admin',
    'rpcpassword':        '-rpcpassword=admin',
    'rpcallowip':         '-rpcallowip=1.1.1.1/0.0.0.0',
    'rpcservertimeout':   '-rpcservertimeout=' + str(config.rpc_timeout),
}


def start(name, ip, docker_image, path, connect_to_ips):
    return_args = args.copy()
    cmd = daemon + ' '.join((return_args).values())
    for _ip in connect_to_ips:
        cmd += ' -connect=' + str(_ip)
    return dockercmd.run_node(name, ip, docker_image, cmd, path)


def rm_peers(node):
    return dockercmd.exec_cmd(node, 'rm -f {}/regtest/peers.dat'.format(config.bitcoin_data_dir))

if __name__ == "__main__":
    print(daemon + ' '.join(args.values()))