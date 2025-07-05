# Region Traffic Analyzer

此部分代码用于分析网络流量数据，统计各IP地址的流量并查询其归属地，生成区域流量占比报告。支持设备分类统计与结果合并。

---

## 环境配置

### 依赖安装
```bash
# Python 3.7+
pip install pandas scapy ipaddress requests tqdm openpyxl
```

### API注意事项

- 使用 [ip-api.com](https://ip-api.com/docs) 免费IP查询服务
- 默认速率限制：**45次/分钟**

------

## 配置说明

### 文件路径配置（修改`region.py`中的配置区域）

```py
# =================配置区域=================
raw_traffic_dir = r"D:\...\raw_traffic"        # 原始pcap文件目录
excel_path = r"D:\...\device-IP.xlsx"          # 设备-IP映射表
all_device_bytes_dir = r"D:\...\ip-region-bytes"    # IP字节数输出目录
all_device_ratio_dir = r"D:\...\region-ratio"       # 区域占比输出目录
devicetype_ratio_dir = r"D:\...\devicetype-ratio"   # 设备类型统计目录
fulltime_region_result_path = r"D:\...\final_result.csv"  # 最终合并结果
# ==========================================
```

### 设备分类规则（代码内置）

```python
first_group = ['camera', 'hub', 'doorbell', 'humidifier', 'light', 'plug', 'sensor']
second_group = ['speaker', 'sound', 'clock']
```

------

## 使用流程

### 1. 数据准备

- 按设备分类存放pcap文件到`raw_traffic_dir`

- 示例目录结构：

  ```
  raw_traffic/
    ├── device1/
    │   ├── traffic1.pcap
    │   └── traffic2.pcap
    └── device2/
        └── session.pcap
  ```

### 2. 运行分析

```
python region.py
```

### 3. 输出文件说明

| 目录/文件                    | 内容                                  |
| :--------------------------- | :------------------------------------ |
| `all_device_ip-region-bytes` | 原始IP-区域-字节数统计                |
| `all_device_region-ratio`    | 各设备区域流量占比（CSV）             |
| `devicetype_region-ratio`    | 设备类型聚合统计结果                  |
| `fulltime_region_result.csv` | 最终格式化数据（source-target-value） |
