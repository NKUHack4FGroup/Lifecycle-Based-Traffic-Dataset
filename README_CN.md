# 基于设备生命周期的物联网设备流量收集方法

本仓库包含我们向《Science China Information Sciences》期刊投递的论文 **《Security and Privacy Measurement on Chinese Consumer IoT Traffic based on Device Lifecycle》** 中所使用的流量收集方法及实验分析代码。

文章的arxiv链接：[ Security and Privacy Measurement on Chinese Consumer IoT Traffic based on Device Lifecycle](https://arxiv.org/abs/2505.09929)

## 文件结构

每个子文件夹均包含对应分析部分的完整代码与配置文件：

- `destination_analyse/` — **第 4 部分：流量目的地分析**，用于识别和分析设备流量的访问目的地。
- `encryption_analyse/` — **第 5 部分：加密实践分析**，用于评估流量中的加密使用情况。
- `traffic_collection/` — **流量收集方法**，包括实验室网络环境搭建及设备配置文件说明。
- `result_demo/` — **流量收集样例及测试结果样例**，包括了两个设备的生命周期流量及测量结果以供预览。
- `device-list.xlsx/` — **设备列表**。

## 流量数据说明

我们在 2024 年 3 月 1 日至 2025 年 6 月 16 日期间，针对 77 款消费级物联网设备，共收集了约 108 小时的网络流量数据。

如需访问完整数据集及分析结果，请发送邮件至 **nkuhack4fgroup@gmail.com**或**jiay@nankai.edu.cn**，并注明您的组织及使用目的。我们将在一周内给予回复。

## 设备列表

|       device        |
| :-----------------: |
|     360_camera      |
|    aqara_camera     |
|      aqara_hub      |
|     aqara_plug      |
|     aqara_light     |
|     bolian_hub      |
|      bull_plug      |
|   cubetoou_camera   |
|    gosound_plug     |
|  greatwall_camera   |
| honorxiaotun_camera |
|     honyar_plug     |
|    huawei_camera    |
|    huawei_sound     |
|  huaweidalen_light  |
|      JD_camera      |
|     jingxun_hub     |
|    konka_camera     |
|   Lecheng_camera    |
|  lecheng_doorbell   |
|    lenovo_camera    |
|      meian_hub      |
|     midea_light     |
|    midea_speaker    |
|  mijia_humidifier   |
|   mijia_lighthub    |
|     mijia_plug      |
|    mijia_plugtwo    |
|     mingdou_hub     |
|    mingdou_plug     |
|    philips_light    |
|    pisen_camera     |
|    qiaoan_camera    |
|   shuixing_camera   |
| smartmi_humidifier  |
|    Sonoff_camera    |
|     sonoff_hub      |
|    tenda_camera     |
|   tianmao_speaker   |
|    tplink_camera    |
|   tplink_doorbell   |
|      tuya_hub       |
|      tuya_plug      |
|     tuya_sensor     |
|      wiz_light      |
|   xiaobai_camera    |
|  xiaobai_doorbell   |
|  xiaobai_Y2camera   |
|    xiaodu_clock     |
|     xiaodu_plug     |
|    xiaodu_sensor    |
|  xiaojingyu_clock   |
|   xiaomao_camera    |
|   Xiaomi_camera3    |
|    xiaomi_camera    |
|     xiaomi_hub      |
|    xiaomi_sound     |
|   xiaomi_speaker    |
|   xiaopai_camera    |
|   xiaotun_camera    |
|    xiaovv_camera    |
|    yibang_camera    |
|   yingshi_camera    |
|     yingshi_hub     |
|    yingshi_plug     |
|   yingshi_sensor    |
|     zte_camera      |
|    haier_camera     |
| huaweizhengtai_plug |
|   xiangrikui_plug   |
|   deebot_cleaner    |
|   duonisi_feeder    |
|      huawei_tv      |
|    midea_mirror     |
| xiaobaismart_camera |
|   xiaodu_speaker    |
|  xiaomitv_speaker   |
