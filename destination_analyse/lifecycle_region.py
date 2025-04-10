import pandas as pd
from scapy.all import *
from scapy.layers.inet import IP
import ipaddress
import requests
import csv
from tqdm import tqdm
import shutil

# =================配置区域=================
raw_traffic_dir = r"D:\dingding\iots\dataset\分析实验代码\submit\dataset\lifetime_traffic"
excel_path = r"D:\dingding\iots\dataset\分析实验代码\submit\dataset\device-IP.xlsx"
all_device_bytes_dir = r"D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\region\lifetime\all_device_ip-region-bytes"
all_device_ratio_dir = r"D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\region\lifetime\all_device_region-ratio"
devicetype_ratio_dir = r"D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\region\lifetime\devicetype_region-ratio"
devicetype_lifetime_dir = r"D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\region\lifetime\devicetype_lifetime"
lifetime_region_result__dir = r"D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\region\lifetime\lifetime_ratio"
# ==========================================

# 读取设备-IP映射表
device_ip_df = pd.read_excel(excel_path)
device_ip_map = dict(zip(device_ip_df["device"], device_ip_df["IP"]))

# IP归属地查询缓存（避免重复查询）
ip_region_cache = {}

def is_private_ip(ip):
    """判断是否为私有IP地址"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private or ip_obj.is_multicast or ip_obj.is_loopback
    except ValueError:
        return True

def get_ip_region(ip):
    """查询IP归属地（带缓存和限速）"""
    if ip in ip_region_cache:
        return ip_region_cache[ip]

    try:
        response = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,message,country,query",
            timeout=5
        )
        data = response.json()
        if data["status"] == "success":
            region = data["country"]
            ip_region_cache[ip] = region
            time.sleep(0.5)  # 遵守API速率限制（每分钟150次）
            return region
    except Exception as e:
        print(f"查询IP {ip} 失败: {str(e)}")
    return "Unknown"

def process_pcap(pcap_path, device_ip, output_dir):
    """处理单个pcap文件"""
    # 统计字典 {ip: total_bytes}
    ip_stats = defaultdict(int)

    # 解析pcap文件
    packets = rdpcap(pcap_path)
    for pkt in tqdm(packets, desc="分析数据包", leave=False):
        if IP in pkt:
            src_ip = pkt[IP].src
            dst_ip = pkt[IP].dst
            length = len(pkt)

            # 确定外部IP
            external_ips = []
            if src_ip != device_ip and not is_private_ip(src_ip):
                external_ips.append(src_ip)
            if dst_ip != device_ip and not is_private_ip(dst_ip):
                external_ips.append(dst_ip)

            # 统计字节数
            for ip in external_ips:
                ip_stats[ip] += length

    # 生成CSV文件名
    csv_filename = f"{os.path.splitext(os.path.basename(pcap_path))[0]}_region.csv"
    csv_path = os.path.join(output_dir, csv_filename)

    # 写入CSV文件
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["IP", "region", "bytes"])

        for ip, total_bytes in ip_stats.items():
            region = get_ip_region(ip)
            writer.writerow([ip, region, total_bytes])

def calculate_region_ratio():
    """计算每个CSV文件中国家流量占比"""
    # 遍历设备目录
    device_folders = [d for d in os.listdir(all_device_bytes_dir)
                      if os.path.isdir(os.path.join(all_device_bytes_dir, d))]

    for device in tqdm(device_folders, desc="处理设备"):
        # 准备输入输出路径
        input_dir = os.path.join(all_device_bytes_dir, device)
        output_dir = os.path.join(all_device_ratio_dir, device)
        os.makedirs(output_dir, exist_ok=True)

        # 处理每个CSV文件
        csv_files = [f for f in os.listdir(input_dir) if f.endswith(".csv")]
        for csv_file in tqdm(csv_files, desc=f"处理 {device}", leave=False):
            process_single_file(
                input_path=os.path.join(input_dir, csv_file),
                output_dir=output_dir
            )

def normalize_region_name(df):
    df["region"] = df["region"].str.strip().str.lower()
    hk_variants = {
        "hong kong", "hongkong", "hk", "hksar","Hong Kong",
        "hong kong sar", "hong kong s.a.r."
    }
    tw_variants = {
        "taiwan", "taipei", "roc", "republic of china","Taiwan","TaiWan"
    }
    df["region"] = df["region"].apply(
        lambda x: "china" if x in hk_variants or x in tw_variants else x
    )
    return df

def process_single_file(input_path, output_dir):
    """处理单个CSV文件"""
    try:
        # 读取原始数据
        df = pd.read_csv(input_path)

        # 标准化国家名称
        df = normalize_region_name(df)

        # 按国家聚合（自动合并中国数据）
        region_stats = df.groupby("region", as_index=False).agg({
            "bytes": "sum"
        })

        # 计算总流量
        total_bytes = region_stats["bytes"].sum()
        if total_bytes == 0:
            return

        # 计算占比并格式化
        region_stats["ratio"] = region_stats["bytes"] / total_bytes
        region_stats["ratio"] = region_stats["ratio"].round(6)  # 保留6位小数

        # 恢复标准国家名称（首字母大写）
        region_stats["region"] = region_stats["region"].str.title()

        # 生成输出文件名
        filename = os.path.basename(input_path)
        output_name = f"{os.path.splitext(filename)[0]}_ratio.csv"
        output_path = os.path.join(output_dir, output_name)

        # 保存结果（按占比降序排列）
        region_stats.sort_values("ratio", ascending=False).to_csv(
            output_path, index=False, float_format="%.4f"
        )

    except Exception as e:
        print(f"处理文件 {input_path} 失败: {str(e)}")

def categorize_and_copy():
    # 设备类型分类字典
    type_mapping = {
        "camera": "camera", "doorbell": "doorbell", "light": "light", "hub": "hub",
        "humidifier": "humidifier", "plug": "plug", "sensor": "sensor",
        "speaker": "speaker", "sound": "speaker", "clock": "speaker"
    }

    # 遍历源目录
    for folder in os.listdir(all_device_ratio_dir):
        src_path = os.path.join(all_device_ratio_dir, folder)
        if not os.path.isdir(src_path):
            continue

        # 查找对应的设备类型目录
        for keyword, category in type_mapping.items():
            if keyword in folder:
                dst_folder = os.path.join(devicetype_ratio_dir, category)
                os.makedirs(dst_folder, exist_ok=True)
                dst_path = os.path.join(dst_folder, folder)
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                print(f"Copied {folder} to {dst_path}")
                break

def merge_lifetime_files():
    # 遍历设备类型文件夹
    for device_type in os.listdir(devicetype_ratio_dir):
        device_type_dir = os.path.join(devicetype_ratio_dir, device_type)
        if not os.path.isdir(device_type_dir):
            continue

        # 创建目标文件夹
        dst_device_type_dir = os.path.join(devicetype_lifetime_dir, device_type)
        os.makedirs(dst_device_type_dir, exist_ok=True)

        # 遍历设备名称文件夹
        for device_name in os.listdir(device_type_dir):
            device_name_dir = os.path.join(device_type_dir, device_name)
            if not os.path.isdir(device_name_dir):
                continue

            # 初始化合并数据
            idle_files = []
            delete_files = []
            setup_files = []
            interaction_files = []

            # 遍历该设备名称文件夹中的 CSV 文件
            for csv_file in os.listdir(device_name_dir):
                if not csv_file.endswith('.csv'):
                    continue

                csv_path = os.path.join(device_name_dir, csv_file)
                df = pd.read_csv(csv_path, encoding='GBK')

                # 根据文件名分类
                if 'idle' in csv_file:
                    idle_files.append(df)
                elif 'delete' in csv_file:
                    delete_files.append(df)
                elif 'setup' in csv_file:
                    setup_files.append(df)
                else:
                    interaction_files.append(df)

            # 合并不同类型的文件
            def merge_data(files):
                if not files:
                    return pd.DataFrame(columns=['region', 'bytes', 'ratio'])
                merged_df = pd.concat(files, ignore_index=True)
                merged_df = merged_df.groupby('region', as_index=False).agg({'bytes': 'sum', 'ratio': 'mean'})
                return merged_df

            # 合并后的文件保存到目标目录
            if idle_files:
                idle_df = merge_data(idle_files)
                idle_df.to_csv(os.path.join(dst_device_type_dir, f"{device_name}_idle.csv"), index=False,
                               encoding='GBK')

            if delete_files:
                delete_df = merge_data(delete_files)
                delete_df.to_csv(os.path.join(dst_device_type_dir, f"{device_name}_delete.csv"), index=False,
                                 encoding='GBK')

            if setup_files:
                setup_df = merge_data(setup_files)
                setup_df.to_csv(os.path.join(dst_device_type_dir, f"{device_name}_setup.csv"), index=False,
                                encoding='GBK')

            if interaction_files:
                interaction_df = merge_data(interaction_files)
                interaction_df.to_csv(os.path.join(dst_device_type_dir, f"{device_name}_interaction.csv"), index=False,
                                      encoding='GBK')
    merge_device_files()

def merge_device_files():
    # 遍历设备类型文件夹
    for device_type in os.listdir(devicetype_lifetime_dir):
        device_type_dir = os.path.join(devicetype_lifetime_dir, device_type)
        if not os.path.isdir(device_type_dir):
            continue
        # 初始化分类文件列表
        idle_files = []
        delete_files = []
        setup_files = []
        interaction_files = []

        # 遍历该设备类型文件夹中的 CSV 文件
        for csv_file in os.listdir(device_type_dir):
            if not csv_file.endswith('.csv'):
                continue

            csv_path = os.path.join(device_type_dir, csv_file)
            df = pd.read_csv(csv_path, encoding='GBK')

            # 根据文件名分类
            if 'idle' in csv_file:
                idle_files.append((csv_file, df))
            elif 'delete' in csv_file:
                delete_files.append((csv_file, df))
            elif 'setup' in csv_file:
                setup_files.append((csv_file, df))
            elif 'interaction' in csv_file:
                interaction_files.append((csv_file, df))

        # 合并不同类型的文件
        def merge_data(files):
            if not files:
                return pd.DataFrame(columns=['region', 'bytes', 'ratio'])
            merged_df = pd.concat([df for _, df in files], ignore_index=True)
            merged_df = merged_df.groupby('region', as_index=False).agg({'bytes': 'sum', 'ratio': 'sum'})
            return merged_df

        # 合并并保存文件
        if idle_files:
            idle_df = merge_data(idle_files)
            idle_df.to_csv(os.path.join(device_type_dir, f"{device_type}_idle.csv"), index=False, encoding='GBK')

        if delete_files:
            delete_df = merge_data(delete_files)
            delete_df.to_csv(os.path.join(device_type_dir, f"{device_type}_delete.csv"), index=False,
                             encoding='GBK')

        if setup_files:
            setup_df = merge_data(setup_files)
            setup_df.to_csv(os.path.join(device_type_dir, f"{device_type}_setup.csv"), index=False, encoding='GBK')

        if interaction_files:
            interaction_df = merge_data(interaction_files)
            interaction_df.to_csv(os.path.join(device_type_dir, f"{device_type}_interaction.csv"), index=False,
                                  encoding='GBK')

        # 删除原来的 CSV 文件（只删除已处理的文件）
        files_to_delete = [csv_file for csv_file, _ in idle_files + delete_files + setup_files + interaction_files]
        for csv_file in os.listdir(device_type_dir):
            if csv_file.endswith('.csv') and csv_file  in files_to_delete:
                os.remove(os.path.join(device_type_dir, csv_file))

def generate_lifetime_files():
    os.makedirs(lifetime_region_result__dir, exist_ok=True)

    for device_folder in os.listdir(devicetype_lifetime_dir):
        device_folder_path = os.path.join(devicetype_lifetime_dir, device_folder)

        if os.path.isdir(device_folder_path):
            # Initialize a dictionary to store the data
            merged_data = {}
            stages = []

            for file_name in os.listdir(device_folder_path):
                if file_name.endswith('.csv'):
                    stage_name = file_name.split('_')[1].replace('.csv', '')
                    stages.append(stage_name)

                    # Read the CSV file
                    file_path = os.path.join(device_folder_path, file_name)
                    df = pd.read_csv(file_path)

                    for _, row in df.iterrows():
                        region = row['region']
                        ratio = row['ratio']
                        if region not in merged_data:
                            merged_data[region] = {}
                        merged_data[region][stage_name] = ratio

            # Create a list of regions sorted
            regions = sorted(merged_data.keys())

            # Prepare the final merged DataFrame with the required output format
            result = []
            for stage in stages:
                row = [stage]
                for region in regions:
                    ratio = merged_data[region].get(stage, 0)
                    row.append(ratio)
                result.append(row)

            # Create column names
            columns = [device_folder] + regions
            result_df = pd.DataFrame(result, columns=['region'] + regions)

            # Rename 'region' column to the device name (e.g., camera)
            result_df.rename(columns={'region': device_folder}, inplace=True)

            # Save the final CSV to the output directory
            output_file_path = os.path.join(lifetime_region_result__dir, f"{device_folder}_merged.csv")
            result_df.to_csv(output_file_path, index=False)
def main():
    # 遍历原始流量目录
    for device_folder in tqdm(os.listdir(raw_traffic_dir), desc="处理设备目录"):
        device_path = os.path.join(raw_traffic_dir, device_folder)

        if not os.path.isdir(device_path):
            continue

        # 获取设备IP
        device_ip = device_ip_map.get(device_folder)
        if not device_ip:
            print(f"警告：找不到设备 {device_folder} 的IP")
            continue

        # 创建输出目录
        output_dir = os.path.join(all_device_bytes_dir, device_folder)
        os.makedirs(output_dir, exist_ok=True)

        # 遍历pcap文件
        pcap_files = [f for f in os.listdir(device_path) if f.lower().endswith(".pcap")]
        for pcap_file in tqdm(pcap_files, desc=f"处理 {device_folder} 的文件"):
            pcap_path = os.path.join(device_path, pcap_file)
            process_pcap(pcap_path, device_ip, output_dir)
        calculate_region_ratio()
    categorize_and_copy()
    merge_lifetime_files()
    generate_lifetime_files()


if __name__ == "__main__":
    main()
    print("处理完成！")
