import subprocess
import psutil
import platform
import os
from flask import Flask, jsonify
import _general

def run_command(command):
    try:
        result = subprocess.check_output(command, shell=True).decode()
        return result
    except subprocess.CalledProcessError:
        return None

def parse_systeminfo(output):
    lines = output.splitlines()
    system_info = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            system_info[key.strip()] = value.strip()
    return system_info

def get_system_info():
    result = run_command('systeminfo')
    if result:
        return parse_systeminfo(result)
    return {'error': 'Failed to retrieve system information'}

def get_tpm_status():
    result = run_command('powershell -Command "Get-WmiObject -Namespace \\"Root\\CIMv2\\Security\\MicrosoftTpm\\" -Class Win32_Tpm"')
    if result:
        return parse_systeminfo(result)
    return {'error': 'Failed to retrieve TPM status'}

def get_system_uptime():
    result = run_command('systeminfo')
    if result:
        for line in result.splitlines():
            if line.startswith('System Boot Time:'):
                return line.split(':', 1)[1].strip()
    return {'error': 'System Boot Time not found in systeminfo output'}

def get_system_install_date():
    result = run_command('systeminfo')
    if result:
        for line in result.splitlines():
            if line.startswith('Original Install Date:'):
                return line.split(':', 1)[1].strip()
    return {'error': 'Original Install Date not found in systeminfo output'}

def get_productid():
    result = run_command('systeminfo')
    if result:
        for line in result.splitlines():
            if line.startswith('Product ID:'):
                return line.split(':', 1)[1].strip()
    return {'error': 'Product ID not found in systeminfo output'}

def get_registeredowner():
    result = run_command('systeminfo')
    if result:
        for line in result.splitlines():
            if line.startswith('Registered Owner:'):
                return line.split(':', 1)[1].strip()
    return {'error': 'Registered Owner not found in systeminfo output'}

def get_timezone():
    result = run_command('systeminfo')
    if result:
        for line in result.splitlines():
            if line.startswith('Time Zone:'):
                return line.split(':', 1)[1].strip()
    return {'error': 'Time Zone not found in systeminfo output'}

def get_inputlocale():
    result = run_command('systeminfo')
    if result:
        for line in result.splitlines():
            if line.startswith('Input Locale:'):
                return line.split(':', 1)[1].strip()
    return {'error': 'Input Locale not found in systeminfo output'}

def get_systemlocale():
    result = run_command('systeminfo')
    if result:
        for line in result.splitlines():
            if line.startswith('System Locale:'):
                return line.split(':', 1)[1].strip()
    return {'error': 'System Locale not found in systeminfo output'}

def get_logonserver():
    result = run_command('systeminfo')
    if result:
        for line in result.splitlines():
            if line.startswith('Logon Server:'):
                return line.split(':', 1)[1].strip()
    return {'error': 'Logon Server not found in systeminfo output'}

def get_pagefilelocation():
    result = run_command('systeminfo')
    if result:
        for line in result.splitlines():
            if line.startswith('Page File Location(s):'):
                return line.split(':', 1)[1].strip()
    return {'error': 'Page File Location(s) not found in systeminfo output'}

def get_domain():
    result = run_command('systeminfo')
    if result:
        for line in result.splitlines():
            if line.startswith('Domain:'):
                return line.split(':', 1)[1].strip()
    return {'error': 'Domain not found in systeminfo output'}

def get_boot_device():
    result = run_command('systeminfo')
    if result:
        for line in result.splitlines():
            if line.startswith('Boot Device:'):
                return line.split(':', 1)[1].strip()
    return {'error': 'Boot Device not found in systeminfo output'}

def get_installed_hotfixes():
    output = run_command('wmic qfe list brief /format:list')
    if output:
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
        grouped_hotfixes = [hotfixes[i:i + 3] for i in range(0, len(hotfixes), 3)]
        return grouped_hotfixes
    return {'error': 'Failed to retrieve installed hotfixes'}

def get_environment_variables():
    return dict(os.environ)  # Get all environment variables as a dictionary

def get_system_helper():  
    services = psutil.win_service_iter()
    processes = psutil.process_iter(['pid', 'name', 'username'])

    return {
        'system_info': get_system_info(),
        'tpm_status': get_tpm_status(),
        'uptime': get_system_uptime(),
        'install_date': get_system_install_date(),
        'product_id': get_productid(),
        'registered_owner': get_registeredowner(),
        'systemlocale': get_systemlocale(),
        'inputlocale': get_inputlocale(),
        'timezone': get_timezone(),
        'pagefile_location': get_pagefilelocation(),
        'domain': get_domain(),
        'boot_device': get_boot_device(),
        'hotfixes': get_installed_hotfixes(),
        'users': psutil.users(),
        'service_info': {
            svc.name(): {
                'display_name': svc.display_name(),
                'status': svc.status(),
                'start_type': svc.start_type(),
                'pid': svc.pid() if svc.pid() else None
            } for svc in services
        },
        'process_info': {
            proc.info['pid']: {
                'name': proc.info['name'],
                'username': proc.info['username']
            } for proc in processes
        },
        'system_specs': {
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
        },
        'environment_variables': get_environment_variables()  # Add environment variables
    }

def define_response_system():
    system_data = get_system_helper()
    return jsonify({
        'system': {
            'host_name': system_data['system_info'].get('Host Name', 'N/A'),
            'os_name': system_data['system_info'].get('OS Name', 'N/A'),
            'os_version': system_data['system_info'].get('OS Version', 'N/A'),
            'system_manufacturer': system_data['system_info'].get('System Manufacturer', 'N/A'),
            'system_model': system_data['system_info'].get('System Model', 'N/A'),
            'cpu_num': system_data['system_info'].get('Processor(s)', 'N/A')
        },
        'system_specs': system_data['system_specs'],
        'tpm': system_data['tpm_status'],
        'uptime': system_data['uptime'],
        'install_date': system_data['install_date'],
        'product_id': system_data['product_id'],
        'registered_owner': system_data['registered_owner'],
        'systemlocale': system_data['systemlocale'],
        'inputlocale': system_data['inputlocale'],
        'timezone': system_data['timezone'],
        'pagefile_location': system_data['pagefile_location'],
        'domain': system_data['domain'],
        'boot_device': system_data['boot_device'],
        'hotfixes': system_data['hotfixes'],
        'users': {
            i: {
                'name': user.name
            } for i, user in enumerate(system_data['users'])
        },
        'processes': system_data['process_info'],
        'services': system_data['service_info'],
        'environment_variables': system_data['environment_variables']  # Include environment variables
    })