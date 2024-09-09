import pythoncom
import wmi
from flask import Flask, jsonify
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from pycaw.utils import AudioUtilities as AU
from comtypes import CLSCTX_ALL

app = Flask(__name__)

def get_audio_devices():
    try:
        # Initialize COM
        pythoncom.CoInitialize()

        # Initialize WMI client
        c = wmi.WMI()

        # Query for audio devices using WMI
        sound_devices = c.query("SELECT * FROM Win32_SoundDevice")

        # Get audio endpoint information using pycaw
        audio_info = []
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)

        # Gather audio devices information
        for device in sound_devices:
            device_info = {
                'device_id': getattr(device, 'DeviceID', None),
                'name': getattr(device, 'Name', None),
                'status': getattr(device, 'Status', None),
                'description': getattr(device, 'Description', None),
                'manufacturer': getattr(device, 'Manufacturer', None),
                'caption': getattr(device, 'Caption', None)
            }
            audio_info.append(device_info)

        # Get volume information
        volume_info = {
            'volume_level': int(float(volume.GetMasterVolumeLevelScalar()) * 100),
            'muted': True if volume.GetMute() == 1 else False
        }

        return {
            'sound_devices': audio_info,
            'volume_info': volume_info
        }
    except Exception as e:
        return {'error': f'Failed to retrieve audio device information: {str(e)}'}
    finally:
        # Uninitialize COM
        pythoncom.CoUninitialize()

def define_response_audio():
    audio_device_info = get_audio_devices()
    if 'error' in audio_device_info:
        return jsonify({'error': audio_device_info['error']}), 500
    return jsonify({
        'audio_devices': audio_device_info.get('sound_devices', []),
        'volume_info': audio_device_info.get('volume_info', {})
    })

@app.route('/audio_devices', methods=['GET'])
def audio_devices():
    return define_response_audio()

if __name__ == "__main__":
    app.run(debug=True)
