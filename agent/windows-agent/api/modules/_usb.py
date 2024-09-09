import pythoncom
from flask import Flask, jsonify
import wmi

def get_usb_devices():
    try:
        # Initialize COM
        pythoncom.CoInitialize()

        # Initialize WMI client
        c = wmi.WMI()
        
        # Query for USB devices
        usb_devices = c.query("SELECT * FROM Win32_PnPSignedDriver WHERE DeviceID LIKE '%USB%'")

        usb_device_info = []
        for device in usb_devices:
            device_info = {
                'DeviceID': getattr(device, 'DeviceID', 'N/A'),
                'DriverName': getattr(device, 'DeviceName', 'N/A'),  # DeviceName is often what you see in Device Manager
                'Manufacturer': getattr(device, 'Manufacturer', 'N/A'),
                'DriverVersion': getattr(device, 'DriverVersion', 'N/A'),
                'Status': getattr(device, 'Status', 'N/A')
            }
            usb_device_info.append(device_info)

        return usb_device_info
    except Exception as e:
        return {'error': f'Failed to retrieve USB device information: {str(e)}'}
    finally:
        # Uninitialize COM
        pythoncom.CoUninitialize()

def define_response_usb():
    usb_device_info = get_usb_devices()
    return jsonify({
        'usb_devices': usb_device_info
    })

