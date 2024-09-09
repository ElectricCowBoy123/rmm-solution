import subprocess
from flask import Flask, jsonify

def get_bios_info():
    try:
        output = subprocess.check_output('wmic bios get /format:list', shell=True).decode().strip()
        lines = output.splitlines()
        bios_info = {}
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                bios_info[key.strip()] = value.strip()
        return bios_info
    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve BIOS information'}

def get_bios_helper():
    return {
        'bios_info' : get_bios_info()
    }

def define_response_bios():
    bios_data = get_bios_helper()
    bios_info = bios_data['bios_info']

    return jsonify({
        'bios': bios_info
    })
