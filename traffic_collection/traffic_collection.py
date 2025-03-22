import sys
import shutil
import threading
import paramiko
import time
from datetime import datetime
import os
from scapy.utils import rdpcap, wrpcap

# global variables
config_file = './Config.txt'
phase_info = {}
# router IP, SSH port, userid&password
router_ip = "192.168.1.1"
router_port = 22
router_username = "root"
router_password = "password"
pcap_file = r"your pcap file path/device name/device name"
lifetime_path = r"your life time file path/device name/"
tcpdump_command = None
tcpdump_process = None

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Generate config based on device
def config_init():
    file_content_camera = """# Camera Configurations
# phase start_time end_time duration
setup 0 0 0
idle_local 0 0 1800
idle_remote 0 0 1800
watch_local 0 0 300
speak_local 0 0 0
watch_remote 0 0 300
speak_remote 0 0 0
update 0 0 0
delete 0 0 0
"""

    file_content_plug = """# plug Configurations
# phase start_time end_time duration
setup 0 0 0
idle_on_local 0 0 900
idle_off_local 0 0 900
idle_off_remote 0 0 900
idle_on_remote 0 0 900
off_remote 0 0 0
on_remote 0 0 0
off_local 0 0 0
on_local 0 0 0
off_voice 0 0 0
on_voice 0 0 0
off_physical 0 0 0
on_physical 0 0 0
update 0 0 0
delete 0 0 0
"""
    file_content_speaker = """# speaker Configurations
# phase start_time end_time duration
setup 0 0 0
idle_local 0 0 1800
idle_remote 0 0 1800
wake_remote 0 0 0
playmusic_remote 0 0 0
app_control_remote 0 0 0
wake_local 0 0 0
playmusic_local 0 0 0
app_control_local 0 0 0
update 0 0 0
delete 0 0 0
"""
    file_content_hub = """# hub Configurations
# phase start_time end_time duration
setup 0 0 0
idle_local 0 0 1800
idle_remote 0 0 1800
update 0 0 0
delete 0 0 0
"""
    file_content_light = """# light Configurations
# phase start_time end_time duration
setup 0 0 0
idle_on_local 0 0 900
idle_off_local 0 0 900
idle_off_remote 0 0 900
idle_on_remote 0 0 900
off_remote 0 0 0
on_remote 0 0 0
control_remote 0 0 0
off_local 0 0 0
on_local 0 0 0
control_local 0 0 0
off_physical 0 0 0
on_physical 0 0 0
control_physical 0 0 0
update 0 0 0
delete 0 0 0
"""
    file_content_doorbell = """# doorbell Configurations
# phase start_time end_time duration
setup 0 0 0
idle_local 0 0 1800
idle_remote 0 0 1800
call 0 0 0
watch_local 0 0 300
speak_local 0 0 0
watch_remote 0 0 300
speak_remote 0 0 0
update 0 0 0
delete 0 0 0
"""
    file_content_sensor = """# sensor Configurations
# phase start_time end_time duration
setup_sensor 0 0 0
idle_local 0 0 1800
alarm_local 0 0 0
idle_remote 0 0 1800
alarm_remote 0 0 0
update 0 0 0
delete 0 0 0
"""

    device_type = input("1 Camera\n2 plug\n3 speaker\n4 hub\n5 light\n6 doorbell\n7 sensor\n"
                        "Please choose the device type: ")

    # 根据用户选择写入配置
    if device_type == '1':
        file_content = file_content_camera
    elif device_type == '2':
        file_content = file_content_plug
    elif device_type == '3':
        file_content = file_content_speaker
    elif device_type == '4':
        file_content = file_content_hub
    elif device_type == '5':
        file_content = file_content_light
    elif device_type == '6':
        file_content =file_content_doorbell
    elif device_type == '7':
        file_content =file_content_sensor
    else:
        print("Invalid input.")
        return

    file_path = './Config.txt'
    with open(file_path, 'w') as file:
        file.write(file_content)
    print(f"Configuration for device type {device_type} has been initialized.")

# read from config.txt
def load_config():
    with open(config_file, 'r', encoding='utf-8') as file:
        for line in file:
            if not line.startswith('#') and line.strip():
                parts = line.split()
                phase_info[parts[0]] = [
                    parts[1],
                    parts[2],
                    int(parts[3])
                ]
    print('Loaded config file')

# update config.txt
def update_config(phase, start_time, end_time, duration):
    # 获取当前的系统时间并格式化为字符串
    current_time_str = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    if start_time == 1:
        # 更新字典中对应阶段的开始时间
        phase_info[phase][0] = current_time_str
    if end_time == 1:
        phase_info[phase][1] = current_time_str
    if duration == 1:
        start_time = datetime.strptime(phase_info[phase][0], '%Y-%m-%d_%H:%M:%S')
        end_time = datetime.strptime(phase_info[phase][1], '%Y-%m-%d_%H:%M:%S')
        duration = end_time - start_time
        phase_info[phase][2] = int(duration.total_seconds())

def execute_ssh_command(ssh_client, command):
    global tcpdump_command, tcpdump_process
    try:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        pid = stdout.readline().strip()
        tcpdump_process = pid
        print(pid)
        output = stdout.read().decode('utf-8')
        print("The command was executed successfully")
        print(output)

        error = stderr.read().decode('utf-8')
        if "packets captured" in error or "packets received by filter" in error or "tcpdump" in error:
            print("command prompt:")
            print(error)

    except Exception as e:
        print(f"执行命令时出现错误：{e}")


def capture():
    global tcpdump_command, tcpdump_process
    try:
        ssh_client.connect(router_ip, router_port, router_username, router_password)
        command = 'tcpdump -s 0 -i br-lan host 192.168.1.236 -w ' + pcap_file + '.pcap' + ' 2>&1'
        command_thread = threading.Thread(target=execute_ssh_command, args=(ssh_client, command))
        command_thread.start()
        print("The SSH command is running in the background...")
    except paramiko.AuthenticationException:
        print("认证失败，请检查用户名和密码。")
    except paramiko.SSHException as e:
        print(f"创建SSH连接时出现问题：{e}")
    except Exception as e:
        print(f"连接或执行命令时出现错误：{e}")
    finally:
        print("Main thread is not waiting for the command to complete.")


def stop_capture():
    global tcpdump_command, tcpdump_process
    try:
        if tcpdump_process:
            stop_command = f'kill -2 {tcpdump_process}'
            ssh_client.exec_command(stop_command)
            time.sleep(5)
            print(f"tcpdump process {tcpdump_process} has been stopped.")
            tcpdump_process = None
    except Exception as e:
        print(f"停止tcpdump进程时出现错误：{e}")


def event_control():
    for phase in phase_info:

        while input(f"Press 'S' to begin capturing {phase} packets: ").strip().upper() != 'S':
            print("You did not press 'S'. Please try again.")
        update_config(phase, 1, 0, 0)
        if phase_info[phase][2] == 0:
            while input(
                    "This stage needs to be stopped manually, please press 'E' or 'e' to stop:").strip().upper() != 'E':
                print("You did not press 'E'. Please try again.")
            update_config(phase, 0, 1, 1)
        else:
            wait_time = phase_info[phase][2]
            print("Waiting")
            for i in range(wait_time, 0, -1):
                sys.stdout.write(f"\r剩余时间： {i} 秒...")
                sys.stdout.flush()
                time.sleep(1)
            sys.stdout.flush()
            update_config(phase, 0, 1, 0)


def write_record():
    with open('Config.txt', 'w') as file:
        file.write("# Config informations\n")
        file.write("# phase start_time end_time duration\n")

        for phase, times in phase_info.items():
            line = f"{phase} {times[0]} {times[1]} {times[2]}\n"
            file.write(line)
    shutil.copy('Config.txt', pcap_file + '.txt')

def divide_pcap_file(pcap_file, lifetime_path):
    pcap_path = f"{pcap_file}.pcap"
    try:
        packets = rdpcap(pcap_path)
    except FileNotFoundError:
        print(f"PCAP file {pcap_path} is not exist")
        return
    if not packets:
        print("no packets in PCAP file")
        return
    output_dir = lifetime_path
    os.makedirs(output_dir, exist_ok=True)


    txt_path = f"{pcap_file}.txt"
    try:
        with open(txt_path, "r") as f:
            lines = f.readlines()[2:]  # 跳过前两行注释
    except FileNotFoundError:
        print(f"TXT file {txt_path} is not exist")
        return

    for line in lines:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        if len(parts) < 4:
            continue

        try:
            phase = parts[0]
            start_ts = datetime.strptime(parts[1], "%Y-%m-%d_%H:%M:%S").timestamp()
            end_ts = datetime.strptime(parts[2], "%Y-%m-%d_%H:%M:%S").timestamp()
        except ValueError as e:
            print(f"The time format is incorrect: {line} ({str(e)})")
            continue

        filtered = []
        for pkt in packets:
            if start_ts <= pkt.time <= end_ts:
                filtered.append(pkt)

        file_basename = os.path.basename(pcap_file)
        output_filename = f"{file_basename}_{phase}.pcap"
        output_path = os.path.join(output_dir, output_filename)
        wrpcap(output_path, filtered)


    print(f"The split is complete and the file is saved {output_dir}")

# 主程序
def main():
    config_init()
    load_config()
    while input("Press 'B' or 'b' to begin capturing: ").strip().upper() != 'B':
        print("You did not press 'B'. Please try again.")
    capture()
    event_control()
    stop_capture()
    write_record()
    divide_pcap_file(pcap_file, lifetime_path)


if __name__ == "__main__":
    main()

