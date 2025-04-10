import os
import csv
from collections import defaultdict
from scapy.all import rdpcap
from scapy.layers.dns import DNS
from datetime import datetime

# ========================
# 配置参数
# ========================
INPUT_BASE = r'D:\dingding\iots\dataset\分析实验代码\submit\dataset\raw_traffic'
OUTPUT_DIR = r'D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\server\ip-dns'


def extract_dns_info(pcap_path):
    """使用您提供的逻辑提取DNS信息"""
    try:
        packets = rdpcap(pcap_path)
    except Exception as e:
        print(f"无法读取文件 {os.path.basename(pcap_path)}: {str(e)}")
        return defaultdict(set)

    dns_info = defaultdict(set)  # ip -> domains

    for packet in packets:
        if packet.haslayer(DNS):
            dns_layer = packet.getlayer(DNS)

            # 确保是DNS响应包且包含回答记录
            if dns_layer.qr == 1 and dns_layer.ancount > 0:
                try:
                    # 获取查询域名
                    qname = dns_layer.qd.qname.decode().strip('.') if dns_layer.qd else 'unknown'

                    # 遍历所有回答记录
                    for i in range(dns_layer.ancount):
                        answer = dns_layer.an[i]
                        if answer.type == 1:  # A记录
                            ip = answer.rdata
                            if isinstance(ip, str) and ip.count('.') == 3:
                                dns_info[ip].add(qname)
                except Exception as e:
                    print(f"处理数据包异常 {pcap_path}: {str(e)}")

    return dns_info


def process_device(device_path, device_name):
    """处理单个设备目录"""
    all_records = set()  # 用于全局去重 (ip, domain)

    print(f"\n▶ 开始处理设备 [{device_name}]")

    # 遍历所有pcap文件
    for filename in os.listdir(device_path):
        if not filename.lower().endswith('.pcap'):
            continue

        pcap_file = os.path.join(device_path, filename)
        print(f"  正在分析: {filename}")

        # 提取DNS信息
        ip_domains = extract_dns_info(pcap_file)

        # 转换数据结构并去重
        for ip, domains in ip_domains.items():
            for domain in domains:
                record = (ip, domain)
                if record not in all_records:
                    all_records.add(record)

    # 保存结果
    if all_records:
        save_results(device_name, sorted(all_records))
        print(f"✔ 完成处理，共发现 {len(all_records)} 条唯一记录")
    else:
        print(f"⚠ 未发现有效DNS记录")


def save_results(device_name, records):
    """保存为CSV文件"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{device_name}_DNS_{timestamp}.csv"
    output_path = os.path.join(OUTPUT_DIR, filename)

    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["IP地址", "DNS域名"])
        writer.writerows(records)

    print(f"  结果已保存至: {filename}")


if __name__ == "__main__":
    start_time = datetime.now()
    print("=" * 50)
    print("DNS分析开始")
    print(f"输入目录: {INPUT_BASE}")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 50)

    total_devices = 0
    total_records = 0

    # 遍历所有设备目录
    for device_dir in os.listdir(INPUT_BASE):
        device_path = os.path.join(INPUT_BASE, device_dir)
        if not os.path.isdir(device_path):
            continue

        # 处理设备数据
        records = process_device(device_path, device_dir)

        # 统计结果
        record_count = len(records) if records else 0
        if record_count > 0:
            total_devices += 1
            total_records += record_count

    # 输出汇总报告
    print("\n" + "=" * 50)
    print(f"分析完成！共处理 {total_devices} 个设备")
    print(f"总计发现 {total_records} 条唯一DNS记录")
    print(f"总耗时: {datetime.now() - start_time}")
    print("=" * 50)
