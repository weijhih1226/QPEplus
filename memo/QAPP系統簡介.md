---
title: QAPP系統簡介
categories: [Linux , QPESUMS , QPEplus , QAPP , FileWatcher]
tags: [Linux , QPESUMS , QPEplus , QAPP , FileWatcher]
date: 2022/12/09
---

# QAPP系統架構
## 系統架構
### 作業機 (79、88)
- 61.56.11.79
- 61.56.11.88（推播）

### DMZ（由作業機79傳送）
- 10.140.2.79
- 10.140.2.88

## 1. 上游資料
### 圖像產品
- 來源：<b>61.56.11.44</b>
- 目錄：/mnt2/nidsB/images/QPESUMSgoogle
  - cref2d_rad - 雷達回波
  - lightning - 即時閃電
  - mosaicPOS_out - 對流胞即時監測
  - qpe_060min - 未來一小時雨區預報
  - rain01h_gage - 一小時累積雨量
  - rain24h_gage - 二十四小時累積雨量

### 雨量資料
- 來源：<b>61.56.11.39/61</b>
- 目錄：/mnt2/data/gauge/qpesums_web_data/src_station_geojson
- 為了讓QAPP的雨量資料與QPEplus相同。

## 2. 產製產品
- 服務：<b>app_filewatch.service</b>
- 目錄：/mnt2/MetaJson
  - cref2d_rad.json - 雷達回波
  - lightning.json - 即時閃電
  - mosaicPOS_out.json - 對流胞即時監測
  - qpe_060min.json - 未來一小時雨區預報
  - rain01h_gage.json - 一小時累積雨量
  - rain24h_gage.json - 二十四小時累積雨量
  - QPESUMS_GAUGE.10M.json - 自動雨量站資料

## 3. 傳送至DMZ（79、88）
- 服務：
  - Timer：<b>qapp.send_product@qapp_app2dmz.timer</b>
  - Service：<b>qapp.send_product@qapp_app2dmz.service</b>
- 目錄：
  ```conf
  [Unit]
  Description=Send product for %i

  [Service]
  User=app1
  Group=qpedata
  WorkingDirectory=/pj/send_product
  EnvironmentFile=/pj/send_product/env.qpeplus
  ExecStart=/pj/send_product/send_product_qapp.py --config etc/qapp/%i.yaml --log-path log/%i.log --print
  ```

## 服務簡介
### Systemd服務
- app_filewatch.service（圖像產品）
  - 監控目錄變動
  - 若有變動觸發產製json程式
- app_handle_json_eng.service（雨量產品）
- qapp.send_product@qapp_app2dmz.timer
- qapp.send_product@qapp_app2dmz.service

### 產品項目

# 狀況排除
## 常用指令
```bash
$ systemctl start <服務名稱>    # 啟動服務
$ systemctl status <服務名稱>   # 檢查服務狀態
$ systemctl restart <服務名稱>  # 重啟服務
$ systemctl stop <服務名稱>     # 中止服務
```
## 查看位置
### send_product服務log
- /pj/send_product/log/（保留5天）

## 2022/12/08
### send_product服務當掉




