import importlib
import subprocess
import sys


def install_and_import_module(module_name, install_name):
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"{install_name} is not installed! Installing {install_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", install_name])

def bytes_to_human_readable(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if abs(n) >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


def get_wmic_info(command):
    try:
        output = subprocess.check_output(f'wmic {command} /value', shell=True).decode().strip()
        lines = output.splitlines()
        info = {}
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                info[key.strip()] = value.strip()
        return info
    except subprocess.CalledProcessError:
        return {'error': f'Failed to retrieve {command}'}