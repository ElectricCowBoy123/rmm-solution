import psutil
from flask import Flask, jsonify

def get_network_helper():

    network_io = psutil.net_io_counters(pernic=True)

    return {
        'network_info' : psutil.net_if_addrs(),
        'network_stats' : psutil.net_if_stats(),
        'net_io' : {
            iface: {
                'bytes_sent': io.bytes_sent,
                'bytes_recv': io.bytes_recv,
                'packets_sent': io.packets_sent,
                'packets_recv': io.packets_recv,
                'errin': io.errin,
                'errout': io.errout,
                'dropin': io.dropin,
                'dropout': io.dropout
            } for iface, io in network_io.items()  
        }
    }

def define_response_network():
    network_data = get_network_helper()
    network_info = network_data['network_info']
    network_stats = network_data['network_stats']
    net_io = network_data['net_io']

    return jsonify({
        'network': {
            'interfaces': {
                iface: {
                    'address': [addr.address for addr in network_info[iface]],
                    'netmask': [addr.netmask for addr in network_info[iface]],
                    'broadcast': [addr.broadcast for addr in network_info[iface]]
                } for iface in network_info
            },
            'stats': {
                iface: {
                    'isup': stats.isup,
                    'duplex': stats.duplex,
                    'speed': stats.speed,
                    'mtu': stats.mtu
                } for iface, stats in network_stats.items()
            },
            'net_io': net_io
        }
    })