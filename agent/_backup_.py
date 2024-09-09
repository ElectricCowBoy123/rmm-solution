import sys
import ctypes
import subprocess
import platform
import importlib
from flask import Flask, jsonify
import psutil

# Function Declarations
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def get_disk_usage():
    disk_usage = {}
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_usage[partition.device] = usage._asdict()
        except OSError as e:
            if 'locked by BitLocker' in str(e):
                disk_usage[partition.device] = {'error': 'Drive is locked by BitLocker'}
            else:
                disk_usage[partition.device] = {'error': str(e)}
    return disk_usage

def funcInstallAndImportModule(module_name, install_name):
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"{install_name} is not installed! Installing {install_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", install_name])

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

def get_cpu_info():
    try:
        output = subprocess.check_output('wmic cpu get /format:list', shell=True).decode().strip()
        lines = output.splitlines()
        cpu_info = {}
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                cpu_info[key.strip()] = value.strip()
        return cpu_info
    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve CPU information'}

def get_cpu_detailed_info():
    try:
        output = subprocess.check_output(
            'powershell -Command "Get-WmiObject -Class Win32_Processor | Select-Object Caption,DeviceID,NumberOfCores,MaxClockSpeed | ConvertTo-Csv -NoTypeInformation"', 
            shell=True
        ).decode().strip()

        # Check if output is empty
        if not output:
            return {'error': 'No CPU information returned'}

        lines = output.splitlines()
        detailed_info = []

        # Skip header row (first line) and process the rest
        if len(lines) > 1:
            for line in lines[1:]:  # Skip header
                # Split CSV fields; note that fields might contain commas
                parts = line.split(',')
                if len(parts) == 4:
                    detailed_info.append({
                        'caption': parts[0].strip().strip('"'),
                        'deviceid': parts[1].strip().strip('"'),
                        'numberofcores': parts[2].strip().strip('"'),
                        'maxclockspeed': parts[3].strip().strip('"')
                    })
        else:
            return {'error': 'No detailed CPU information available'}

        return detailed_info
    except subprocess.CalledProcessError as e:
        return {'error': f'Failed to retrieve detailed CPU information: {str(e)}'}
    except Exception as e:
        return {'error': f'An error occurred while processing CPU information: {str(e)}'}

    
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

def get_system_info():
    try:
        result = subprocess.check_output('systeminfo', shell=True).decode()
        lines = result.splitlines()
        system_info = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                system_info[key.strip()] = value.strip()
        return system_info
    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve system information'}

def get_tpm_status():
    try:
        result = subprocess.check_output(
            'powershell -Command "Get-WmiObject -Namespace \\"Root\\CIMv2\\Security\\MicrosoftTpm\\" -Class Win32_Tpm"', 
            shell=True
        ).decode()
        lines = result.splitlines()
        tpm_status = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                tpm_status[key.strip()] = value.strip()
        return tpm_status
    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve TPM status'}
    
def get_system_uptime():
    try:
        result = subprocess.check_output('systeminfo', shell=True).decode()
        lines = result.splitlines()
        for line in lines:
            if line.startswith('System Boot Time:'):
                return line.split(':', 1)[1].strip()
        return {'error': 'System Boot Time not found in systeminfo output'}
    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve system information'}
    
def get_system_install_date():
    try:
        result = subprocess.check_output('systeminfo', shell=True).decode()
        lines = result.splitlines()
        for line in lines:
            if line.startswith('Original Install Date:'):
                return line.split(':', 1)[1].strip()
        return {'error': 'Original Install Date not found in systeminfo output'}
    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve system information'}
    
def get_productid():
    try:
        result = subprocess.check_output('systeminfo', shell=True).decode()
        lines = result.splitlines()
        for line in lines:
            if line.startswith('Product ID:'):
                return line.split(':', 1)[1].strip()
        return {'error': 'Product ID not found in systeminfo output'}
    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve system information'}

def get_registeredowner():
    try:
        result = subprocess.check_output('systeminfo', shell=True).decode()
        lines = result.splitlines()
        for line in lines:
            if line.startswith('Registered Owner:'):
                return line.split(':', 1)[1].strip()
        return {'error': 'Registered Owner not found in systeminfo output'}
    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve system information'}
    
def get_timezone():
    try:
        result = subprocess.check_output('systeminfo', shell=True).decode()
        lines = result.splitlines()
        for line in lines:
            if line.startswith('Time Zone:'):
                return line.split(':', 1)[1].strip()
        return {'error': 'Time Zone not found in systeminfo output'}
    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve system information'}
    
def get_inputlocale():
    try:
        result = subprocess.check_output('systeminfo', shell=True).decode()
        lines = result.splitlines()
        for line in lines:
            if line.startswith('Input Locale:'):
                return line.split(':', 1)[1].strip()
        return {'error': 'Input Locale not found in systeminfo output'}
    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve system information'}

def get_systemlocale():
    try:
        result = subprocess.check_output('systeminfo', shell=True).decode()
        lines = result.splitlines()
        for line in lines:
            if line.startswith('System Locale:'):
                return line.split(':', 1)[1].strip()
        return {'error': 'System Locale not found in systeminfo output'}
    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve system information'}
    
def get_logonserver():
    try:
        result = subprocess.check_output('systeminfo', shell=True).decode()
        lines = result.splitlines()
        for line in lines:
            if line.startswith('Logon Server:'):
                return line.split(':', 1)[1].strip()
        return {'error': 'Logon Server not found in systeminfo output'}
    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve system information'}
    
def get_pagefilelocation():
    try:
        result = subprocess.check_output('systeminfo', shell=True).decode()
        lines = result.splitlines()
        for line in lines:
            if line.startswith('Page File Location(s):'):
                return line.split(':', 1)[1].strip()
        return {'error': 'Page File Location(s) not found in systeminfo output'}
    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve system information'}
    
def get_domain():
    try:
        result = subprocess.check_output('systeminfo', shell=True).decode()
        lines = result.splitlines()
        for line in lines:
            if line.startswith('Domain:'):
                return line.split(':', 1)[1].strip()
        return {'error': 'Domain not found in systeminfo output'}
    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve system information'}

def get_boot_device():
    try:
        result = subprocess.check_output('systeminfo', shell=True).decode()
        lines = result.splitlines()
        for line in lines:
            if line.startswith('Boot Device:'):
                return line.split(':', 1)[1].strip()
        return {'error': 'Boot Device not found in systeminfo output'}
    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve system information'}

def get_installed_hotfixes():
    try:
        output = subprocess.check_output(
            'wmic qfe list brief /format:list',
            shell=True
        ).decode().strip()

        hotfixes = []
        hotfix = {}

        lines = output.splitlines()

        for line in lines:
            if '=' in line:
                key, value = map(str.strip, line.split('=', 1))
                if key in ['Description', 'HotFixID', 'InstalledOn']:
                    hotfix[key] = value
                    
            elif not line and hotfix:
                hotfixes.append(hotfix)
                hotfix = {}

        if hotfix:
            hotfixes.append(hotfix)

        # Group hotfixes in sets of 3
        grouped_hotfixes = []
        for i in range(0, len(hotfixes), 3):
            grouped_hotfixes.append(hotfixes[i:i + 3])

        return grouped_hotfixes

    except subprocess.CalledProcessError:
        return {'error': 'Failed to retrieve system information'}

def bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if abs(n) >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n

# Install and import necessary modules
funcInstallAndImportModule('flask', 'flask')

# Create Flask app instance
app = Flask(__name__)

@app.route('/resources', methods=['GET'])
def system_resources():
    # Get system information
    system_info = get_system_info()
    tpm_status = get_tpm_status()
    bios_info = get_bios_info()
    cpu_info = get_cpu_info()
    uptime = get_system_uptime()
    install_date = get_system_install_date()
    product_id = get_productid()
    registered_owner = get_registeredowner()
    systemlocale = get_systemlocale()
    inputlocale = get_inputlocale()
    timezone = get_timezone()
    pagefile_location = get_pagefilelocation()
    domain = get_domain()
    boot_device = get_boot_device()
    hotfixes = get_installed_hotfixes()

    # Get CPU usage and memory details
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    memory_info = psutil.virtual_memory()
    swap_info = psutil.swap_memory()

    # Get disk details
    disk_usage = get_disk_usage()

    # Get network details
    network_info = psutil.net_if_addrs()
    network_stats = psutil.net_if_stats()

    network_io = psutil.net_io_counters(pernic=True)

    users = psutil.users()

    processes = psutil.process_iter(['pid', 'name', 'username']) 

    services = psutil.win_service_iter()

    service_info = {
        svc.name(): {  # Use service name as the key
            'display_name': svc.display_name(),
            'status': svc.status(),
            'start_type': svc.start_type(),
            'pid': svc.pid() if svc.pid() else None
        } for svc in services
    }
    
    process_info = {
        proc.info['pid']: {  # Use PID as the key
            'name': proc.info['name'],
            'username': proc.info['username'],
            # 'terminal': proc.info.get('terminal', None)  # Uncomment if you need the terminal info
        } for proc in processes
    }

    net_io = {
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

    cpu_times = psutil.cpu_times()

    cpu_times_info = {
        'user': cpu_times.user,
        'system': cpu_times.system,
        'idle': cpu_times.idle,
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

    # Get system specs
    system_specs = {
        'system': {
            'system': platform.system(),
            'node': platform.node(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'processor': platform.processor()
        }
    }

    # Get detailed CPU information
    cpu_detailed_info = get_cpu_detailed_info()

    return jsonify({
        'system': {
            'host_name': system_info.get('Host Name', 'N/A'),
            'os_name': system_info.get('OS Name', 'N/A'),
            'os_version': system_info.get('OS Version', 'N/A'),
            'system_manufacturer': system_info.get('System Manufacturer', 'N/A'),
            'system_model': system_info.get('System Model', 'N/A'),
            'cpu_num': system_info.get('Processor(s)', 'N/A')
        },
        'system_specs': system_specs,
        'cpu': {
            'usage_percent': cpu_usage,
            'cpu_count': cpu_count,
            'cpu_freq': {
                'current': cpu_freq.current if cpu_freq else None,
                'min': cpu_freq.min if cpu_freq else None,
                'max': cpu_freq.max if cpu_freq else None
            },
            'detailed': cpu_detailed_info
        },
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
        },
        'disk': {
            'partitions': {
                partition.device: {
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype
                } for partition in psutil.disk_partitions()
            },
            'usage': disk_usage
        },
        'disk_io': {
            disk: {
                'read_count': io_counters.read_count,
                'write_count': io_counters.write_count,
                'read_bytes': io_counters.read_bytes,
                'write_bytes': io_counters.write_bytes
            } for disk, io_counters in psutil.disk_io_counters(perdisk=True).items()
        },
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
        },
        'tpm': tpm_status,
        'bios': bios_info,
        'uptime': uptime,
        'cpu_info': cpu_info,
        'install_date': install_date,
        'product_id': product_id,
        'registered_owner': registered_owner,
        'systemlocale': systemlocale,
        'inputlocale': inputlocale,
        'timezone': timezone,
        'pagefile_location': pagefile_location,
        'domain': domain,
        'boot_device': boot_device,
        'hotfixes': hotfixes,
        'users': {
            i: {
                'name': user.name,
                'terminal': user.terminal,
                'host': user.host,
                'started': user.started,
                'pid': user.pid
            } for i, user in enumerate(users)  # Use enumerate to get an index if you need one
        },
        'processes': process_info,
        'services': service_info,
        'cpu_times': cpu_times_info
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
