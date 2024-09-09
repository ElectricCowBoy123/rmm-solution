import psutil
from flask import Flask, jsonify

def get_memory_helper():
    return {
        'memory_info' : psutil.virtual_memory(),
        'swap_info' : psutil.swap_memory()
    }

def define_response_memory():
    memory_data = get_memory_helper()
    memory_info = memory_data['memory_info']
    swap_info = memory_data['swap_info']
    return jsonify({
        'memory': {
            'total': memory_info.total,
            'available': memory_info.available,
            'percent': memory_info.percent,
            'used': memory_info.used,
            'free': memory_info.free
        },
        'swap': {
            'total': swap_info.total,
            'used': swap_info.used,
            'free': swap_info.free,
            'percent': swap_info.percent
        }
    })