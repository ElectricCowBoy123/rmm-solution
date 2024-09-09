import psutil
from flask import Flask, jsonify
import _general 

def get_disk_usage():
    disk_usage = {}
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_usage[partition.device] = {
                'free': _general.bytes_to_human_readable(usage.free),
                'percent': usage.percent,
                'total': _general.bytes_to_human_readable(usage.total),
                'used': _general.bytes_to_human_readable(usage.used),
                'mountpoint': partition.mountpoint[:-1],
                'fstype': partition.fstype
            }
        except OSError as e:
            disk_usage[partition.device] = {'error': str(e)}
    return disk_usage

def get_disk_helper():
    return {
        'mounted_partitions' : get_disk_usage()
    }

def define_response_disk():
    disk_data = get_disk_helper()
    mounted_partitions = disk_data['mounted_partitions']

    return jsonify({

    'mounted_partitions': mounted_partitions,

    'disk_io': {
        disk: {
            'total_read_count': io_counters.read_count,
            'total_write_count': io_counters.write_count,
            'total_read_bytes': _general.bytes_to_human_readable(io_counters.read_bytes),
            'total_write_bytes': _general.bytes_to_human_readable(io_counters.write_bytes),
        } 
        for disk, io_counters in psutil.disk_io_counters(perdisk=True).items()
    }
    })