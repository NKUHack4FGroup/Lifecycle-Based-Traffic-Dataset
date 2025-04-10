import os
import pandas as pd
from pathlib import Path


def extract_device_name(filename):
    """改进后的设备名提取函数"""
    base_name = os.path.splitext(filename)[0]
    parts = base_name.split('_')

    if len(parts) < 3:
        raise ValueError(f"无效文件名格式: {filename}")

    return '_'.join(parts[:-2])


def process_files():
    # 路径配置
    excel_path = r"D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\server\ip-dns-party-fulltime\all_device_rdns_info.xlsx"
    input_base = r"D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\region\lifetime\all_device_ip-region-bytes"
    output_base = r"D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\server\ip-dns-party-lifetime"

    # 读取Excel数据
    df_rdns = pd.read_excel(excel_path, engine='openpyxl').convert_dtypes()
    df_rdns['IP'] = df_rdns['IP'].astype(str)

    # 创建全局统计变量
    total_files = 0
    processed_files = 0
    skipped_files = 0

    for root, dirs, files in os.walk(input_base):
        for file in files:
            if file.endswith('_region.csv'):
                total_files += 1
                try:
                    device_name = extract_device_name(file)
                    input_path = Path(root) / file

                    # 构造输出路径
                    relative_path = Path(root).relative_to(input_base)
                    output_path = Path(output_base) / relative_path / file
                    output_path.parent.mkdir(parents=True, exist_ok=True)

                    # 处理文件并获取处理结果
                    result = process_single_file(
                        input_path, output_path, device_name, df_rdns
                    )

                    if result == "skipped_empty":
                        skipped_files += 1
                    elif result == "processed":
                        processed_files += 1

                except Exception as e:
                    print(f"处理文件 {file} 时出错: {str(e)}")
                    continue

    # 打印统计信息
    print(f"\n处理完成！")
    print(f"总文件数: {total_files}")
    print(f"成功处理: {processed_files}")
    print(f"跳过空文件: {skipped_files}")
    print(f"失败文件: {total_files - processed_files - skipped_files}")


def process_single_file(input_path, output_path, device_name, df_rdns):
    # 读取CSV文件
    try:
        df_csv = pd.read_csv(input_path, encoding='utf-8')
    except UnicodeDecodeError:
        df_csv = pd.read_csv(input_path, encoding='gbk')

    df_csv['IP'] = df_csv['IP'].astype(str)

    # 筛选设备DNS数据
    device_data = df_rdns[df_rdns['Device Name'] == device_name]

    if device_data.empty:
        print(f"设备 {device_name} 无DNS数据，跳过文件: {input_path}")
        return "skipped_empty"

    # 合并数据
    merged = pd.merge(
        df_csv,
        device_data[['IP', 'final_rdns_info', 'party', 'DNS所属公司']],
        on='IP',
        how='left'
    )

    # 创建存在DNS标记
    merged['has_dns'] = ~(
            merged['final_rdns_info'].isna() &
            merged['party'].isna() &
            merged['DNS所属公司'].isna()
    )

    # 过滤无DNS记录的行
    filtered = merged[merged['has_dns']].drop(columns=['has_dns'])

    # 填充空值为空字符串
    for col in ['final_rdns_info', 'party', 'DNS所属公司']:
        filtered[col] = filtered[col].fillna('')

    if filtered.empty:
        print(f"所有记录无DNS数据，跳过文件: {input_path}")
        return "skipped_empty"

    # 保存结果
    filtered.to_csv(output_path, index=False, encoding='utf-8-sig')
    return "processed"


if __name__ == '__main__':
    process_files()
