## Traffic Collection Framework Introduction

This guide aims to help users utilize a Python script for data packet collection and segmentation. The script connects to a router via SSH, captures packets using `tcpdump`, and splits the packets into multiple files based on timestamps defined in a configuration file.

## Environment Setup

### 1. Python Environment

Ensure that Python 3.x is installed on your system. You can check the Python version using the following command:

```
python3 --version
```

### 2. Install Dependencies

The script relies on the following Python libraries:

- `paramiko`: For SSH connections.
- `scapy`: For handling PCAP files.
- `shutil`: For file operations.

You can install these libraries using the following command:

```
pip install paramiko scapy
```

### 3. Router Configuration

Ensure you have a router accessible via SSH and that `tcpdump` is installed on the router. You need to know the router's IP address, SSH port, username, and password.

## Parameter Configuration

### 1. Configuration File

The script uses the `Config.txt` file to define configurations for different device types. You can generate the configuration file by running the script and selecting the device type.

### 2. Global Variables

At the beginning of the script, you need to set the following global variables:

- `router_ip`: The router's IP address.
- `router_port`: The router's SSH port (default is 22).
- `router_username`: The router's SSH username.
- `router_password`: The router's SSH password.
- `pcap_file`: The path and filename for saving the PCAP file.
- `lifetime_path`: The path for saving the segmented PCAP files.

### 3. Device Type Selection

When running the script, you will be prompted to select a device type. Enter the corresponding number based on your device:

```
1 Camera
2 plug
3 speaker
4 hub
5 light
6 doorbell
7 sensor
```

## Usage Steps

### 1. Initialize Configuration

After running the script, you will first be prompted to select a device type. Once selected, the script will generate the corresponding `Config.txt` file.

### 2. Load Configuration

The script will automatically load the configuration information from the `Config.txt` file.

### 3. Start Capturing Packets

When prompted, enter `B` or `b` to start capturing packets. The script will connect to the router via SSH and start `tcpdump`.

### 4. Event Control

The script will process each phase in the configuration file sequentially. For each phase:

- Press `S` to start capturing packets for that phase.
- If the phase requires manual stopping, press `E` to stop capturing.
- If the phase has a predefined duration, the script will automatically wait for the specified time.

### 5. Stop Capturing

Once all phases are completed, the script will automatically stop the `tcpdump` process.

### 6. Record Configuration

The script will write the updated configuration information to the `Config.txt` file and copy it to the directory where the PCAP file is stored.

### 7. Segment Packets

Based on the timestamps in the `Config.txt` file, the script will split the captured PCAP file into multiple files, with each file corresponding to a phase.