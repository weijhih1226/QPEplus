---
title: QPEplus系統簡介
categories: [Linux , QPESUMS , QPEplus , FileWatcher]
tags: [Linux , QPESUMS , QPEplus , FileWatcher]
date: 2022/10/13
---

# QPEplus系統架構
## 系統架構圖
![系統架構圖](./img/QPEplus%E6%9E%B6%E6%A7%8B%E5%9C%96.png)

### 作業機 (39、61)
 - 61.56.11.39（資料處理主機）
 - 61.56.11.61（備援資料處理主機）

### 網頁機 (210~212)
 - 61.56.11.210（API主機）
 - 61.56.11.211（API主機）
 - 61.56.11.212（API主機）

### 預部署機（90、91）
 - 61.56.11.90
 - 61.56.11.91

### 測試機 (201)
 - 61.56.11.201

### DMZ（10.140.2.210~212）
 - 10.140.2.210
 - 10.140.2.211
 - 10.140.2.212

### 安內RD版 (156)
 - 172.16.30.156

## PXC叢集 (Percona XtraDB Cluster)
 - 39、61
 - 156

## Docker叢集架構（Docker Swarm）
 - 39、61、210~212
 - DMZ：210~212


# QPEplus服務簡介
## Django
 - webmap (地圖)
 - rainmonitor (監控)
 - gallery (圖輯)
 - case (個案)
 - qadmin (管理)

## Systemd服務
 - qpeplus.dropsonde.service
 - qpeplus.filewatcher@dropsonde.service
 - qpeplus.filewatcher@case.service
 - qpeplus.filewatcher@QPEPLUS.service
 - qpeplus.filewatcher@QPEPLUS_forTHB.service
 - qpeplus.filewatcher@QPEPLUS_for_hdf5.service
 - qpeplus.filewatcher@QPEPLUS_forTHB_special_section.service
 - qpeplus.filewatcher@QPEPLUS_lightningcwb1.service
 - qpeplus.filewatcher@QPEPLUS_lightningcwb2.service
 - qpeplus.filewatcher@QPEPLUS_lightningcwb3.service
 - qpeplus.filewatcher@QPEPLUS_for_two_min_radar.service
 - qpeplus.rainmonitor-tag-time-range.service
 - qpeplus.send_product@QPEPLUS_nfs.timer
 - qpeplus.send_product@QPEAPP.timer
 - qpeplus.send_product@QPEPLUS_TRA.timer
 - qpeplus.send_product.x@QPEPLUS_201.timer
 - qpeplus.send_product.x@QPEPLUS_90.timer
 - qpeplus.send_product@IREADS.timer
 - airforce_match_list_cp@211020.timer
 - TAHOPE_match_list_cp@211026.timer
 - send_product_match_list_cp@210924.timer

## 其它
 - backend (fastapi)
 - send_product
 - filewatcher
 - dropsonde


# QPEplus系統設定
## 主程式目錄（後面以~/代表）
 - /pj/qpesums_web/

## 主資料目錄
 - /mnt2/

## 程式部署
 - ~/deploy.sh
   ```console
   $ git pull     # 於該主機pull到最新版
   $ sh deploy.sh
   ```
   有時候會在build image或recreate container時timeout，只要重跑就好。
 - ~/test_server.sh - 201測試機
 - ~/test_server_90.sh - 90預部署機
 - ~/deploy_south.sh - 南區備援主機

## 定期排程
 - ~/config/backend.crontab
 - ~/config/backend.crontab.1139
 - ~/config/backend.crontab.1161

## 過期資料
 - ~/expire_{數字}hours_setting.txt - {數}小時前過期資料路徑
 - /mnt2/目錄下除了qpesums_web_data外都由上游刪除。
 - 201測試機/90預部署機等以send_product接收上游資料的機器，會同步正式作業機。


# QPEplus系統維護
## 狀況排除
### Docker常用容器、服務
- Docker容器名稱
  - qpesums_web (網頁)
  - qpeplus_nginx.vev4d402uik3jdnhzwotv0u82.nxjskiq3est7o0ibpet90r2zc (nginx，負載平衡)
  - qpeplus_fastapi_backend.1.qc0zw7jzwcwgxepgm4bnwgd9b (框架)

- Docker服務名稱
  - qpeplus_qpesums_web
  - qpeplus_nginx
  - qpeplus_fastapi_backend
  - registry (儲存庫)

### 查看Docker容器輸出logs
```bash
$ docker ps                         # Docker容器列表
$ docker logs [OPTIONS] 容器名稱/ID # 顯示該容器logs
OPTIONS:
 --tail string  # 顯示最後幾行
```

### 查看Docker服務輸出logs
```bash
$ docker service ls                         # Docker服務列表
$ docker service logs [OPTIONS] 服務名稱/ID # 顯示該服務logs
OPTIONS:
 --tail string  # 顯示最後幾行
```

### 查看Systemd服務輸出logs
```console
$ journalctl [OPTIONS...] [MATCHES...]
Flag:
 -u | --unit [Systemd服務名稱]  # 顯示特定服務單位log
 -f                             # 隨著輸出滾動顯示
```

```console
$ systemctl status [Systemd服務名稱]
$ journalctl -u [Systemd服務名稱] -f
```

查看所有filewatcher服務：
```console
$ systemctl status qpeplus.filewatcher@"*".service --lines=0
```

# 補充資料
## 好用的流程畫圖小工具
 - https://app.diagrams.net

---

# 狀況排除
## 查看位置
### 定期排程（API）
/pj/qpesums_web/config/backend.crontab.1139

## 2022/08/29
### 過期資料未被刪除造成queue等候較久

- 61.56.11.39:/pj/qpesums_web/expire_24hours_setting.txt
  - 寫入欲刪除過期資料目錄
    ```txt
    /mnt2/qpesums_web_data/landslide_alert/  # 未加入purge
    ```

- 61.56.11.39:/pj/qpesums_web/config/backend.crontab.1139
  - crontab定期刪除過期資料

## 2022/09/01
### 颱風路徑在13:50後沒顯示

- 61.56.11.39:/pj/qpesums_web/src/support-tools/get_active_typhoon.py
  - 日期處理有bug
    ```python
    # last_position.fix_time = last_position.fix_time.replace(day=last_position.fix_time.day - 1) # 有換月問題
    last_position.fix_time = last_position.fix_time - datetime.timedelta(hours=24)
    ```
  - 輸出log目錄：/mnt2/qpesums_web_data/tmp/active_typhoon/get_weather_advisory.log

## 2022/09/02
### 公路總局監控資料未如期進來

- 掛載之NAS（48、49）容量已滿
  ```console
  $ df -h       # 查看主機掛載磁區使用量
  $ du -xhd 1   # x指跳過不同檔案系統、h指可讀格式、d指層數
  ```

## 2022/09/03
### 颱風預報路徑及小工具消失

- /mnt2/qpesums_web_data/typhoon/position/typhoon_position.YYYYMMDDhhmmss.geojson - 檔案大小變小（因為未含預報路徑）
- /mnt2/qpesums_web_data/tmp/active_typhoon/get_weather_advisory.log - 未顯示輸出預報路徑資料
- 61.56.11.39:/pj/qpesums_web/src/support-tools/get_active_typhoon.py
  - 查詢TAFIS II API
    ```bash
    $ docker exec -it qpesums_web bash
    ```
    ```python
    import requests
    import json
    tafis_api = 'https://tafis2.cwb.gov.tw/tafis/api/'
    token = 'iaU5doZ8-xHOK7sonSHAff-Zc8E'
    param = {"cwb_typhoon_name": "軒嵐諾"}
    response_ca = requests.get(url=tafis_api+'cyclone/active/', params=param, headers={"Authorization": f"Token {token}"})
    response = requests.get(url=tafis_api+'forecast/', params=param, headers={"Authorization": f"Token {token}"})
    json_content_ca = json.loads(response_ca.content)
    json_content = json.loads(response.content)
    print(json_content_ca)
    print(json_content)
    ```
    查詢結果：API資料沒問題。

## 2023/01/05、2023/01/30
### 台鐵版土石流潛勢溪流燈號異常

- /data/qpesums_web_data/tramudslide/latest_file/latest_tramudslide.json - 最新土石流燈號警示ID
- /mnt2/data/QPESUMS/xml/swcb_xml/XXXX_Close.xml - 傳送燈號警示ID(XXXX) XML檔至該目錄下，以關閉該燈號

---