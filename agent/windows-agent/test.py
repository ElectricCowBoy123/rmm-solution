import wmi
from flask import Flask, jsonify

def list_partitions_without_drive_letter():
    c = wmi.WMI()
    partitions = c.Win32_DiskPartition()
    logical_disks = c.Win32_LogicalDisk()

    partition_to_fs = {}
    for disk in logical_disks:
        # Map logical disk to its partition and file system
        for partition in disk.associators(wmi_result_class="Win32_DiskPartition"):
            partition_to_fs[partition.DeviceID] = disk.FileSystem

    # Filter out partitions without a drive letter
    partition_info = []
    for partition in partitions:
        file_system = partition_to_fs.get(partition.DeviceID, "Unknown")
        partition_info.append({
            'Partition': partition.DeviceID,
            'DiskIndex': partition.DiskIndex,
            'Type': partition.Type if partition.Type else "Unknown",  
            'Size': partition.Size,  # Ensure size is correctly converted to GB
            'BootPartition': partition.BootPartition,
            'file_system': file_system
        })

    return partition_info

def define_response_disk():
    partition_info = list_partitions_without_drive_letter()
    return jsonify({
        'disks': {
            'partitions': partition_info
        }
    })

if __name__ == "__main__":
    app = Flask(__name__)

    @app.route("/diskinfo", methods=["GET"])
    def diskinfo():
        return define_response_disk()

    app.run(host="0.0.0.0", port=5000)
