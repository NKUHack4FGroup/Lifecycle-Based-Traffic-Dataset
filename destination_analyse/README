# Region Traffic Analyzer

This section of the code is used to analyze network traffic data, calculate traffic for each IP address, query its geographic region, and generate a regional traffic proportion report. It supports device category statistics and result merging.

---

## Environment Setup

### Dependencies Installation

```bash
# Python 3.7+
pip install pandas scapy ipaddress requests tqdm openpyxl
```

### API Notes

* Uses the free IP lookup service from [ip-api.com](https://ip-api.com/docs)
* Default rate limit: **45 requests per minute**

---

## Configuration Instructions

### File Path Configuration (Modify the configuration area in `region.py`)

```py
# =================Configuration Area=================
raw_traffic_dir = r"D:\...\raw_traffic"        # Original pcap file directory
excel_path = r"D:\...\device-IP.xlsx"          # Device-IP mapping table
all_device_bytes_dir = r"D:\...\ip-region-bytes"    # IP byte count output directory
all_device_ratio_dir = r"D:\...\region-ratio"       # Regional proportion output directory
devicetype_ratio_dir = r"D:\...\devicetype-ratio"   # Device type statistics directory
fulltime_region_result_path = r"D:\...\final_result.csv"  # Final merged result
# ===================================================
```

### Device Classification Rules (Built into the code)

```python
first_group = ['camera', 'hub', 'doorbell', 'humidifier', 'light', 'plug', 'sensor']
second_group = ['speaker', 'sound', 'clock']
```

---

## Usage Process

### 1. Data Preparation

* Store pcap files by device category in `raw_traffic_dir`

* Example directory structure:

  ```
  raw_traffic/
    ├── device1/
    │   ├── traffic1.pcap
    │   └── traffic2.pcap
    └── device2/
        └── session.pcap
  ```

### 2. Run Analysis

```
python region.py
```

### 3. Output File Descriptions

| Directory/File               | Content                                     |
| :--------------------------- | :------------------------------------------ |
| `all_device_ip-region-bytes` | Raw IP-region-byte count statistics         |
| `all_device_region-ratio`    | Regional traffic proportion by device (CSV) |
| `devicetype_region-ratio`    | Aggregated statistics by device type        |
| `fulltime_region_result.csv` | Final formatted data (source-target-value)  |
