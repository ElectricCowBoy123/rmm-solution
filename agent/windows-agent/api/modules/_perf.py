import psutil
from flask import Flask, jsonify
import _general
import pythoncom
import wmi
import subprocess as sp

def get_gpu_info():
    try:
        # Initialize COM
        pythoncom.CoInitialize()

        # Initialize WMI client
        c = wmi.WMI()

        # Query for GPU information
        gpus = c.query("SELECT * FROM Win32_VideoController")

        gpu_usage_cmd = r'(((Get-Counter "\GPU Engine(*engtype_3D)\Utilization Percentage").CounterSamples | where CookedValue).CookedValue | measure -sum).sum'

        gpu_load = round(get_gpu_usage(gpu_usage_cmd),2)
        
        # Gather GPU information
        gpu_info = []
        for gpu in gpus:
            gpu_info.append({
                'Name': getattr(gpu, 'Name', 'N/A'),
                'DriverVersion': getattr(gpu, 'DriverVersion', 'N/A'),
                'VideoProcessor': getattr(gpu, 'VideoProcessor', 'N/A'),
                'CurrentRefreshRate': f"{getattr(gpu, 'CurrentRefreshRate', 'N/A')}Hz",
                'MaxRefreshRate': f"{getattr(gpu, 'MaxRefreshRate', 'N/A')}Hz",
                'MinRefreshRate': f"{getattr(gpu, 'MinRefreshRate', 'N/A')}Hz",
                'gpu_load': gpu_load
            })

        return {
            'gpu_info': gpu_info
        }
    except Exception as e:
        return {'error': f'Failed to retrieve display and GPU information: {str(e)}'}
    finally:
        # Uninitialize COM
        pythoncom.CoUninitialize()

def get_gpu_usage(command):
    val = sp.run(['powershell', '-Command', command], capture_output=True).stdout.decode("ascii")
    return float(val.strip().replace(',', '.'))

def get_network_helper():
    network_io = psutil.net_io_counters(pernic=True)

    return {
        'network_stats' : psutil.net_if_stats(),
        'net_io' : {
            iface: {
                'total_bytes_sent': _general.bytes_to_human_readable(io.bytes_sent),
                'total_bytes_recv': _general.bytes_to_human_readable(io.bytes_recv),
                'total_packets_sent': io.packets_sent,
                'total_packets_recv': io.packets_recv,
                'errin': io.errin,
                'errout': io.errout,
                'dropin': io.dropin,
                'dropout': io.dropout
            } for iface, io in network_io.items()  
        }
    }

def get_cpu_helper():
    cpu_times = psutil.cpu_times()
    return {
        'cpu_usage' : psutil.cpu_percent(interval=1),
        'cpu_freq' : psutil.cpu_freq(),
        'cpu_times' : cpu_times,
        'cpu_times_info' : {
            'user': getattr(cpu_times, 'user', None),
            'system': getattr(cpu_times, 'system', None),
            'idle': getattr(cpu_times, 'idle', None),
            'irq': getattr(cpu_times, 'irq', None),
            'nice': getattr(cpu_times, 'nice', None),
            'softirq': getattr(cpu_times, 'softirq', None),
            'steal': getattr(cpu_times, 'steal', None),
            'guest': getattr(cpu_times, 'guest', None),
            'interrupt': getattr(cpu_times, 'interrupt', None),
            'dpc': getattr(cpu_times, 'dpc', None),
            'iowait': getattr(cpu_times, 'iowait', None),
            'guest_nice': getattr(cpu_times, 'guest_nice', None)
        }
    }

def get_memory_helper():
    return {
        'memory_info' : psutil.virtual_memory(),
        'swap_info' : psutil.swap_memory()
    }

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
        'disk_usage' : get_disk_usage()
    }

def get_display_devices():
    try:
        # Initialize COM
        pythoncom.CoInitialize()

        # Initialize WMI client
        c = wmi.WMI()

        # Query for GPU information
        gpus = c.query("SELECT * FROM Win32_VideoController")

        # Gather GPU information
        gpu_info = []
        for gpu in gpus:
            adapter_ram = getattr(gpu, 'AdapterRAM', None)
            if adapter_ram and int(adapter_ram) > 0:
                adapter_ram_mb = int(adapter_ram) / (1024 * 1024)
            else:
                adapter_ram_mb = 'N/A'

            gpu_info.append({
                'Name': getattr(gpu, 'Name', 'N/A'),
                'DriverVersion': getattr(gpu, 'DriverVersion', 'N/A'),
                'vram': adapter_ram_mb,  # Amount of graphics memory in MB
                'VideoProcessor': getattr(gpu, 'VideoProcessor', 'N/A'),
                'VideoArchitecture': getattr(gpu, 'VideoArchitecture', 'N/A'),
                'VideoMemoryType': getattr(gpu, 'VideoMemoryType', 'N/A'),
                'CurrentRefreshRate': getattr(gpu, 'CurrentRefreshRate', 'N/A'),
                'MaxRefreshRate': getattr(gpu, 'MaxRefreshRate', 'N/A'),
                'MinRefreshRate': getattr(gpu, 'MinRefreshRate', 'N/A')
            })

        return {
            'gpu_info': gpu_info
        }
    except Exception as e:
        return {'error': f'Failed to retrieve display and GPU information: {str(e)}'}
    finally:
        # Uninitialize COM
        pythoncom.CoUninitialize()

def define_response_performance():
    cpu_data = get_cpu_helper()
    cpu_usage = cpu_data['cpu_usage']
    cpu_freq = cpu_data['cpu_freq']
    cpu_times_info = cpu_data['cpu_times_info']

    memory_data = get_memory_helper()
    memory_info = memory_data['memory_info']
    swap_info = memory_data['swap_info']

    disk_data = get_disk_helper()
    disk_usage = disk_data['disk_usage']

    network_data = get_network_helper()
    network_stats = network_data['network_stats']
    net_io = network_data['net_io']

    gpu_info = get_gpu_info()

    return jsonify({
        'cpu': {
            'cpu_times': cpu_times_info,
            'usage_percent': cpu_usage,
            'cpu_freq': {
                'current': cpu_freq.current if cpu_freq else None,
                'min': cpu_freq.min if cpu_freq else None,
                'max': cpu_freq.max if cpu_freq else None
            }
        },
        'memory': {
            'total': memory_info.total,
            'available': memory_info.available,
            'percent': memory_info.percent,
            'used': memory_info.used,
            'free': memory_info.free,
            'swap': {
                'total': swap_info.total,
                'used': swap_info.used,
                'free': swap_info.free,
                'percent': swap_info.percent
            }
        },
        'disk': {
            'usage': disk_usage,
            'disk_io': {
                disk: {
                    'total_read_count': io_counters.read_count,
                    'total_write_count': io_counters.write_count,
                    'total_read_bytes': _general.bytes_to_human_readable(io_counters.read_bytes),
                    'total_write_bytes': _general.bytes_to_human_readable(io_counters.write_bytes),
                } 
                for disk, io_counters in psutil.disk_io_counters(perdisk=True).items()
            }
        },
        'network': {
            'stats': {
                iface: {
                    'isup': stats.isup,
                    'duplex': stats.duplex,
                    'speed': stats.speed,
                    'mtu': stats.mtu
                } for iface, stats in network_stats.items()
            },
            'net_io': net_io
        },
        'display': {
            'gpu_info': gpu_info
        }
    })