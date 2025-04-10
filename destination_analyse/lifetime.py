import pandas as pd


def update_excel_data():
    # 定义文件路径（使用原始字符串处理Windows路径）
    src_path = r'D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\server\ip-dns-party-fulltime\all_device_rdns_info.xlsx'
    dst_path = r'D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\server\ip-dns-party-lifetime\device_ip-life_output_backend.xlsx'
    output_path = r'D:\dingding\iots\dataset\分析实验代码\submit\destination_analyse\result\server\ip-dns-party-lifetime\updated_device_ip-life_output_backend.xlsx'

    try:
        # 读取源数据（使用openpyxl引擎确保兼容性）
        df_source = pd.read_excel(src_path, engine='openpyxl')

        # 读取目标数据
        df_target = pd.read_excel(dst_path, engine='openpyxl')

        # 创建复合键映射字典
        mapping = {}
        for _, row in df_source.iterrows():
            key = (row['Device Name'], row['IP'])
            mapping[key] = {
                'final_rdns_info': row['final_rdns_info'],
                'party': row['party'],
                'DNS所属公司': row['DNS所属公司']
            }

        # 确保目标列存在
        for col in ['party', 'DNS所属公司']:
            if col not in df_target.columns:
                df_target[col] = None

        # 更新目标数据
        for idx, row in df_target.iterrows():
            key = (row['Device Name'], row['IP'])
            if key in mapping:
                values = mapping[key]
                df_target.at[idx, 'final_rdns_info'] = values['final_rdns_info']
                df_target.at[idx, 'party'] = values['party']
                df_target.at[idx, 'DNS所属公司'] = values['DNS所属公司']

        # 保存更新后的数据（保留原始格式）
        df_target.to_excel(output_path, index=False, engine='openpyxl')
        print(f"数据更新完成，已保存至：{output_path}")

    except Exception as e:
        print(f"处理过程中发生错误：{str(e)}")


if __name__ == "__main__":
    update_excel_data()
