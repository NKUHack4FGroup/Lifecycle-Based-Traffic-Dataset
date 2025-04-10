# Region Traffic Analyzer

该工具用于分析网络流量数据，统计各IP地址的流量并查询其归属地，生成区域流量占比报告。支持设备分类统计与结果合并。

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
- 如需商业用途请遵守其API条款

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

------

## 功能扩展建议

1. **私有云部署**：替换`get_ip_region()`中的IP查询接口
2. **性能优化**：添加多线程处理pcap文件
3. **可视化**：使用matplotlib/pyecharts生成流量地图
4. **错误处理**：增加断点续传功能

------

## 注意事项

1. 首次运行会自动创建输出目录
2. 香港地区流量会自动合并到中国
3. 未知区域标记为"Unknown"
4. 建议在服务器环境处理大型pcap文件