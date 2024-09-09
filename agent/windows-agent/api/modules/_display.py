import pythoncom
import wmi
from flask import Flask, jsonify
import ctypes

app = Flask(__name__)

def define_response_display():
    display_device_info = get_display_devices()
    
    if 'error' in display_device_info:
        return jsonify({'error': display_device_info['error']}), 500
    
    response_data = {
        'display_devices': display_device_info['display_devices'],
        'gpu_info': display_device_info['gpu_info']
    }

    return jsonify(response_data)

def get_display_devices():
    try:
        # Initialize COM
        pythoncom.CoInitialize()

        # Initialize WMI client
        c = wmi.WMI()

        # Query for display devices
        monitors = c.query("SELECT * FROM Win32_DesktopMonitor")
        # Query for GPU information
        gpus = c.query("SELECT * FROM Win32_VideoController")

        display_info = []

        # Define the function and constants for retrieving display resolution
        user32 = ctypes.WinDLL('user32')
        user32.GetSystemMetrics.restype = ctypes.c_int

        def get_display_resolution(monitor_index):
            width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
            height = user32.GetSystemMetrics(1) # SM_CYSCREEN
            return width, height

        # Gather monitor information
        for i, monitor in enumerate(monitors):
            monitor_info = {
                'DeviceID': getattr(monitor, 'DeviceID', 'N/A'),
                'Name': getattr(monitor, 'Name', 'N/A'),
                'ScreenWidth': getattr(monitor, 'ScreenWidth', 'N/A'),
                'ScreenHeight': getattr(monitor, 'ScreenHeight', 'N/A'),
                'Status': getattr(monitor, 'Status', 'N/A'),
                'MonitorType': getattr(monitor, 'MonitorType', 'N/A'),
                'Manufacturer': getattr(monitor, 'Manufacturer', 'N/A'),
                'Availability': getattr(monitor, 'Availability', 'N/A'),
                'Bandwidth': getattr(monitor, 'Bandwidth', 'N/A'),
                'Caption': getattr(monitor, 'Caption', 'N/A'),
                'ConfigManagerErrorCode': getattr(monitor, 'ConfigManagerErrorCode', 'N/A'),
                'ConfigManagerUserConfig': getattr(monitor, 'ConfigManagerUserConfig', 'N/A'),
                'CreationClassName': getattr(monitor, 'CreationClassName', 'N/A'),
                'Description': getattr(monitor, 'Description', 'N/A'),
                'DisplayType': getattr(monitor, 'DisplayType', 'N/A'),
                'ErrorCleared': getattr(monitor, 'ErrorCleared', 'N/A'),
                'ErrorDescription': getattr(monitor, 'ErrorDescription', 'N/A'),
                'InstallDate': getattr(monitor, 'InstallDate', 'N/A'),
                'IsLocked': getattr(monitor, 'IsLocked', 'N/A'),
                'LastErrorCode': getattr(monitor, 'LastErrorCode', 'N/A'),
                'MonitorManufacturer': getattr(monitor, 'MonitorManufacturer', 'N/A'),
                'PixelsPerXLogicalInch': getattr(monitor, 'PixelsPerXLogicalInch', 'N/A'),
                'PixelsPerYLogicalInch': getattr(monitor, 'PixelsPerYLogicalInch', 'N/A'),
                'PNPDeviceID': getattr(monitor, 'PNPDeviceID', 'N/A'),
                'PowerManagementCapabilities': getattr(monitor, 'PowerManagementCapabilities', 'N/A'),
                'PowerManagementSupported': getattr(monitor, 'PowerManagementSupported', 'N/A'),
                'StatusInfo': getattr(monitor, 'StatusInfo', 'N/A'),
                'SystemCreationClassName': getattr(monitor, 'SystemCreationClassName', 'N/A'),
                'SystemName': getattr(monitor, 'SystemName', 'N/A'),
                'HorizontalResolution': 'N/A',
                'VerticalResolution': 'N/A'
            }

            # Try to get resolution from GetSystemMetrics (this is for primary display)
            width, height = get_display_resolution(i)
            monitor_info['HorizontalResolution'] = width
            monitor_info['VerticalResolution'] = height

            display_info.append(monitor_info)

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
            'display_devices': display_info,
            'gpu_info': gpu_info
        }
    except Exception as e:
        return {'error': f'Failed to retrieve display and GPU information: {str(e)}'}
    finally:
        # Uninitialize COM
        pythoncom.CoUninitialize()

@app.route('/display_devices', methods=['GET'])
def display_devices():
    display_device_info = get_display_devices()
    
    if 'error' in display_device_info:
        return jsonify({'error': display_device_info['error']}), 500
    
    response_data = {
        'display_devices': display_device_info['display_devices'],
        'gpu_info': display_device_info['gpu_info']
    }

    return jsonify(response_data)
