import pandas as pd
from scapy.all import *
from scapy.layers.inet import IP
import ipaddress
import requests
import csv
from tqdm import tqdm
from io import StringIO

# =================配置区域=================
raw_traffic_dir = r"D:\dingding\iots\dataset\分析实验代码\submit\dataset\raw_traffic"
excel_path = r"D:\dingding\iots\dataset\分析实验代码\submit\dataset\device-IP.xlsx"
all_device_bytes_dir = r"D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\region\fulltime\all_device_ip-region-bytes"
all_device_ratio_dir = r"D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\region\fulltime\all_device_region-ratio"
devicetype_ratio_dir = r"D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\region\fulltime\devicetype_region-ratio"
fulltime_region_result_path = r"D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\region\fulltime\fulltime_region_result.csv"
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
    """标准化国家名称（合并香港到中国）"""
    # 统一转换为小写处理
    df["region"] = df["region"].str.strip().str.lower()

    # 合并逻辑（包含常见香港拼写变体）
    hk_variants = {
        "hong kong", "hongkong", "hk", "hksar",
        "hong kong sar", "hong kong s.a.r."
    }

    df["region"] = df["region"].apply(
        lambda x: "china" if x in hk_variants else x
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


def merge_device_region_ratios():
    # 定义设备分类规则
    first_group = ['camera', 'hub', 'doorbell', 'humidifier', 'light', 'plug', 'sensor']
    second_group = ['speaker', 'sound', 'clock']

    # 确保目标目录存在
    os.makedirs(devicetype_ratio_dir, exist_ok=True)

    # 初始化数据存储结构：device_type -> {region: sum_ratio}
    device_data = defaultdict(lambda: defaultdict(float))

    # 遍历源目录
    for folder_name in os.listdir(all_device_ratio_dir):
        folder_path = os.path.join(all_device_ratio_dir, folder_name)

        # 跳过非目录文件
        if not os.path.isdir(folder_path):
            continue

        # 确定设备类型
        folder_lower = folder_name.lower()
        device_type = None

        # 先检查第一类设备
        for kw in first_group:
            if kw in folder_lower:
                device_type = kw
                break

        # 再检查第二类设备
        if not device_type:
            for kw in second_group:
                if kw in folder_lower:
                    device_type = "speaker"
                    break

        # 跳过未分类设备
        if not device_type:
            continue

        # 处理目录下的CSV文件
        for file_name in os.listdir(folder_path):
            if not file_name.endswith(".csv"):
                continue

            file_path = os.path.join(folder_path, file_name)

            try:
                # 读取CSV文件
                df = pd.read_csv(
                    file_path,
                    usecols=["region", "ratio"],
                    dtype={"region": str, "ratio": float}
                )

                # 累加到设备数据
                for _, row in df.iterrows():
                    region = str(row["region"]).strip()
                    device_data[device_type][region] += row["ratio"]

            except Exception as e:
                print(f"处理文件失败：{file_path}，错误：{str(e)}")
                continue

    # 保存结果
    for device_type, regions in device_data.items():
        # 转换为DataFrame并排序
        df = pd.DataFrame(
            [(region, ratio) for region, ratio in regions.items()],
            columns=["region", "ratio"]
        ).sort_values("region")

        # 保存文件
        output_path = os.path.join(devicetype_ratio_dir, f"{device_type}_region_ratio.csv")
        df.to_csv(output_path, index=False)
        print(f"已生成文件：{output_path}")


def merge_device_region_ratio(encoding='utf-8'):
    all_data = []

    # 遍历处理每个CSV文件
    for filename in os.listdir(devicetype_ratio_dir):
        if filename.lower().endswith('.csv'):
            try:
                # 提取设备名称（第一个下划线前的部分）
                device = filename.split('_')[0]
                filepath = os.path.join(devicetype_ratio_dir, filename)

                with open(filepath, 'r', encoding=encoding) as f:
                    lines = f.readlines()

                    # 检测标题行（查找包含region和ratio的标题）
                    header = lines[0].strip().lower()
                    start_line = 1 if ('region' in header and 'ratio' in header) else 0

                    for line in lines[start_line:]:
                        line = line.strip()
                        if not line:
                            continue

                        # 智能分割：最后一个空格前是region，最后一个是ratio
                        parts = line.split(',')
                        if len(parts) != 2:
                            continue  # 跳过格式错误行

                        region, ratio = parts
                        all_data.append((device, region, ratio))

            except Exception as e:
                print(f"处理文件 {filename} 时出错: {str(e)}")
                continue

    # 写入合并文件
    try:
        with open(fulltime_region_result_path, 'w', newline='', encoding=encoding) as f:
            writer = csv.writer(f)
            writer.writerow(['source', 'target', 'value'])
            writer.writerows(all_data)
        print(f"成功合并 {len(all_data)} 条记录到 {fulltime_region_result_path}")
    except Exception as e:
        print(f"写入输出文件失败: {str(e)}")
        raise


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
    merge_device_region_ratios()
    merge_device_region_ratio()


if __name__ == "__main__":
    main()
    print("处理完成！")
