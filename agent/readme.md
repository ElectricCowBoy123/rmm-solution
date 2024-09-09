- Seems to be better to use C++ for this instead of Python, just running into issues with it:
  https://github.com/lfreist/hwinfo

- Make both the Linux agent and Windows agents a service and daemon respectively:

Yes, you can write a Windows service in Python using the pywin32 library. A Windows service is similar to a Linux daemon, running in the background and starting automatically when the system boots.
Steps to Create a Windows Service in Python:

    Install pywin32: First, you need to install the pywin32 package. You can do this using pip:

    bash

pip install pywin32

Write the Windows Service Script: Below is an example Python script that implements a simple Windows service. This service will run in the background and, for example, write a timestamp to a log file every 10 seconds.

python

    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    import time

    class MyPythonService(win32serviceutil.ServiceFramework):
        _svc_name_ = "MyPythonService"
        _svc_display_name_ = "My Python Service"
        _svc_description_ = "This is a simple Python service that writes timestamps to a log file."

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
            with open("C:\\path\\to\\your\\log_file.txt", "a") as f:
                while self.running:
                    f.write(f"Service is running at {time.ctime()}\n")
                    f.flush()
                    time.sleep(10)

    if __name__ == '__main__':
        win32serviceutil.HandleCommandLine(MyPythonService)

    Explanation:
        MyPythonService class: Inherits from win32serviceutil.ServiceFramework and implements the service's main functionality.
        SvcDoRun(): The main loop of the service. This method is where the service runs continuously.
        SvcStop(): Handles stopping the service. It sets the running flag to False to break the loop in SvcDoRun() and terminate the service.
        Log file: The service writes a timestamp to log_file.txt every 10 seconds. Make sure to update the path to where you want to save the log file.

3. Install the Service:

To install the service, run the Python script with the install argument:

bash

python your_service_script.py install

This command installs the service on the system. You can start, stop, and manage it using the Windows Service Manager. 4. Start the Service:

After installation, you can start the service using the start command:

bash

python your_service_script.py start

You can also start and stop the service using the Windows Service Manager (services.msc). 5. Stop and Uninstall the Service:

To stop the service, use the stop command:

bash

python your_service_script.py stop

To uninstall the service, use the remove command:

bash

python your_service_script.py remove

6. Debugging the Service:

If you need to debug your service, you can run it in debug mode:

bash

python your_service_script.py debug

Conclusion:

This setup allows you to create a Windows service in Python using the pywin32 library. You can customize the service's behavior by modifying the main() function in the MyPythonService class. This approach is useful for running long-running background tasks on a Windows system, such as monitoring files, handling scheduled tasks, or maintaining persistent connections.
