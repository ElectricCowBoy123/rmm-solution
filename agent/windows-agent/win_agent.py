import sys
import os
import ctypes
import importlib

sys.path.append(os.path.join(os.path.dirname(__file__), 'api/modules'))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import _general

try:
    _general.install_and_import_module('pywin32', 'pywin32')
    _general.install_and_import_module('wmi', 'wmi')
    _general.install_and_import_module('pythoncom', 'pythoncom')
    _general.install_and_import_module('flask', 'flask')
    _general.install_and_import_module('pywintypes', 'pywin32')
    _general.install_and_import_module('pycaw', 'pycaw')
    _general.install_and_import_module('psutil', 'psutil')
    _general.install_and_import_module('flask_cors', 'flask_cors')
except Exception:
    exit(1)
finally:
    from flask import Flask, jsonify
    from flask_cors import CORS
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    import time

import _cpu
import _memory
import _bios
import _network
import _disk
import _usb
import _system
import _display
import _audio
import _perf

project_dir = os.path.dirname(os.path.abspath(__file__))

loaded_modules = list(sys.modules.items())
    
# Iterate over the list of loaded modules
for module_name, module in loaded_modules:
    # Check if the module has a __file__ attribute and if its path is within project_dir
    if hasattr(module, '__file__') and module.__file__ and project_dir in module.__file__:
        try:
            # Reload the module
            importlib.reload(module)
            print(f"Reloaded: {module_name}")
        except Exception as e:
            print(f"Failed to reload {module_name}: {e}")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False
    
if not is_admin():
    print("Please run as admin!")
    exit(0)


app = Flask(__name__)
app.add_url_rule('/cpu', 'define_response_cpu', _cpu.define_response_cpu, methods=['GET'])
app.add_url_rule('/bios', 'define_response_bios', _bios.define_response_bios, methods=['GET'])
app.add_url_rule('/memory', 'define_response_memory', _memory.define_response_memory, methods=['GET'])
app.add_url_rule('/network', 'define_response_network', _network.define_response_network, methods=['GET'])
app.add_url_rule('/system', 'define_response_system', _system.define_response_system, methods=['GET'])
app.add_url_rule('/usb', 'define_response_usb', _usb.define_response_usb, methods=['GET'])
app.add_url_rule('/disk', 'define_response_disk', _disk.define_response_disk, methods=['GET'])
app.add_url_rule('/display', 'define_response_display', _display.define_response_display, methods=['GET'])
app.add_url_rule('/audio', 'define_response_audio', _audio.define_response_audio, methods=['GET'])
app.add_url_rule('/performance', 'define_response_performance', _perf.define_response_performance, methods=['GET'])
CORS(app)

class PythonFlaskService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PythonFlaskService"
    _svc_display_name_ = "Python Flask API Service"
    _svc_description_ = "A Python service running a Flask API for system information."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(PythonFlaskService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(PythonFlaskService)

# TO-DO: find a better way of reimporting the modules etc having to define it the way ive done it here seems clumbersome
# TO-DO: review directory structure dont think i need a modules folder inside of api actually
# TO-DO: implement regions and review code structure and refactor accordingly
# TO-DO: go back through everything and make sure all information is included, i want it to be as verbose as possible
# TO-DO: complete the usb api

# TO-DO: start fleshing out the web interface in html css
# TO-DO: implement javascript to call this api
# TO-DO: at this point we want to add client/server functionality such that agents check in with the server and a record is kept as such, we should be able to query a clients api for info

# TO-DO: at this point functionality should start being added to run commands locally and execute basic administrative tasks, of which i should obtain a comprehensive list

# TO-DO: at this point i should also start looking at implementing or structuring the ui around at-least automation ability so you can tick multiple clients performing actions enmass

# IDEA: automations via powershell would be a good idea to include so every time a user logs in etc execute some powershell code