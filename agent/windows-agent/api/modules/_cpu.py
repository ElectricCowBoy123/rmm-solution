import subprocess
import psutil
from flask import Flask, jsonify

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
    

def get_cpu_helper():
    cpu_times = psutil.cpu_times()

    return {
        'cpu_info' : get_cpu_info(),
        'cpu_usage' : psutil.cpu_percent(interval=1),
        'cpu_count' : psutil.cpu_count(),
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
        },
        'cpu_detailed_info' : get_cpu_detailed_info()
    }

def define_response_cpu():
    cpu_data = get_cpu_helper()
    cpu_info = cpu_data['cpu_info']
    cpu_usage = cpu_data['cpu_usage']
    cpu_count = cpu_data['cpu_count']
    cpu_freq = cpu_data['cpu_freq']
    cpu_times_info = cpu_data['cpu_times_info']
    cpu_detailed_info = cpu_data['cpu_detailed_info']

    return jsonify({
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
        'cpu_info': cpu_info,
        'cpu_times': cpu_times_info
    })