import os
import re
import pandas as pd


def update_rdns_info():
    # 定义路径
    csv_dir = r'D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\server\ip-dns-party-fulltime'
    excel_path = r'D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\server\rdns_info.xlsx'

    # 读取所有CSV文件并构建映射关系
    mapping_data = []
    for filename in os.listdir(csv_dir):
        if filename.endswith('.csv'):
            # 使用正则表达式提取设备名
            match = re.match(r'^(.*?)_DNS_.*\.csv$', filename)
            if not match:
                print(f"跳过不符合格式的文件: {filename}")
                continue

            device_name = match.group(1)
            csv_path = os.path.join(csv_dir, filename)

            try:
                # 读取CSV文件并检测列数（使用UTF-8编码）
                with open(csv_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    num_columns = len(first_line.split(','))

                # 根据列数动态处理（统一使用UTF-8编码读取）
                if num_columns == 3:
                    df_csv = pd.read_csv(
                        csv_path,
                        header=None,
                        names=['IP', 'DNS', 'party'],
                        encoding='utf-8'
                    )
                elif num_columns == 2:
                    df_csv = pd.read_csv(
                        csv_path,
                        header=None,
                        names=['IP', 'DNS'],
                        encoding='utf-8'
                    )
                    df_csv['party'] = ''
                else:
                    print(f"文件 {filename} 列数不符合要求（{num_columns}列），已跳过")
                    continue

                df_csv['Device Name'] = device_name
                mapping_data.append(df_csv)
            except UnicodeDecodeError:
                # 如果UTF-8解码失败，尝试使用latin-1编码
                try:
                    with open(csv_path, 'r', encoding='latin-1') as f:
                        first_line = f.readline().strip()
                        num_columns = len(first_line.split(','))

                    if num_columns == 3:
                        df_csv = pd.read_csv(
                            csv_path,
                            header=None,
                            names=['IP', 'DNS', 'party'],
                            encoding='latin-1'
                        )
                    elif num_columns == 2:
                        df_csv = pd.read_csv(
                            csv_path,
                            header=None,
                            names=['IP', 'DNS'],
                            encoding='latin-1'
                        )
                        df_csv['party'] = ''
                    else:
                        print(f"文件 {filename} 列数不符合要求（{num_columns}列），已跳过")
                        continue

                    df_csv['Device Name'] = device_name
                    mapping_data.append(df_csv)
                except Exception as e:
                    print(f"读取文件 {filename} 时发生错误: {e}")
                    continue
            except pd.errors.EmptyDataError:
                print(f"文件 {filename} 内容为空，已跳过")
                continue
            except Exception as e:
                print(f"读取文件 {filename} 时发生错误: {e}")
                continue

    if not mapping_data:
        print("未找到有效的CSV文件")
        return

    # 合并所有CSV数据
    df_mapping = pd.concat(mapping_data)[['Device Name', 'IP', 'DNS', 'party']]

    # 读取Excel文件
    df_excel = pd.read_excel(excel_path)

    # 合并数据（左连接）
    merged_df = pd.merge(
        df_excel,
        df_mapping,
        on=['Device Name', 'IP'],
        how='left'
    )

    # 更新final_rdns_info列
    merged_df['final_rdns_info'] = merged_df['DNS'].fillna(merged_df['final_rdns_info'])

    # 添加party列
    merged_df['party'] = merged_df['party'].fillna('')

    # 清理临时列
    merged_df.drop(columns=['DNS'], inplace=True)

    # 保存回原文件
    merged_df.to_excel(excel_path, index=False)
    print("更新完成！")


if __name__ == "__main__":
    update_rdns_info()
