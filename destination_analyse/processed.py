import pandas as pd
import os
from pathlib import Path

# 路径配置
excel_path = r"D:\dingding\iots\dataset\分析实验代码\submit\dataset\device-IP.xlsx"
input_root = r"D:\dingding\iots\encryption\temp"
output_root = r"D:\dingding\iots\encryption\processed"

# 读取设备-IP映射表（增加大小写转换）
device_ip_df = pd.read_excel(excel_path)
device_ip_map = {k.strip().lower(): v.strip() for k, v in zip(device_ip_df["device"], device_ip_df["IP"])}

# 创建输出目录
Path(output_root).mkdir(parents=True, exist_ok=True)


def normalize_columns(df):
    """规范化列名：去除前后空格，转换为小写"""
    df.columns = df.columns.str.strip().str.lower()
    return df


# 遍历所有CSV文件
for root, dirs, files in os.walk(input_root):
    for file in files:
        if file.lower().endswith(".csv"):
            csv_path = os.path.join(root, file)

            # 获取设备名称（处理可能的空格问题）
            device_name = os.path.basename(root).strip().lower()

            # 验证设备是否在映射表中
            if device_name not in device_ip_map:
                print(f"警告：设备目录 {device_name} 不存在于IP映射表中，跳过处理")
                continue

            target_ip = device_ip_map[device_name]

            try:
                # 自动检测分隔符和编码读取CSV
                with open(csv_path, 'r', encoding='utf-8-sig') as f:
                    first_line = f.readline()

                # 判断分隔符
                sep = '\t' if '\t' in first_line else ','

                # 读取CSV（增加错误处理）
                df = pd.read_csv(
                    csv_path,
                    sep=sep,
                    engine='python',
                    on_bad_lines='warn',
                    encoding='utf-8-sig'
                )
                df = normalize_columns(df)

                # 验证必要列是否存在
                required_columns = {'ip_src', 'ip_dst'}
                if not required_columns.issubset(df.columns):
                    missing = required_columns - set(df.columns)
                    raise ValueError(f"缺少必要列：{missing}")

                # 过滤数据（增加IP格式规范化）
                filtered_df = df[
                    (df['ip_src'].str.strip() == target_ip) |
                    (df['ip_dst'].str.strip() == target_ip)
                    ]

                # 构建输出路径（保持原目录结构）
                relative_path = os.path.relpath(root, input_root)
                output_dir = os.path.join(output_root, relative_path)
                os.makedirs(output_dir, exist_ok=True)

                # 保存结果（使用检测到的分隔符）
                output_path = os.path.join(output_dir, file)
                filtered_df.to_csv(output_path, sep=sep, index=False, encoding='utf-8-sig')
                print(f"成功处理：{csv_path} -> {output_path}（{len(filtered_df)} 行）")

            except Exception as e:
                print(f"处理失败：{csv_path}")
                print(f"错误详情：{str(e)}")
                print("=" * 60)
                continue

print("处理完成！")
