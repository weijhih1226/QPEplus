---
title: QPEplus資料庫
categories: [Linux , QPESUMS , QPEplus , MySQL , database]
tags: [Linux , QPESUMS , QPEplus , MySQL , database]
date: 2022/12/06
---

# QPEplus資料庫
## 資料庫主機

- 61.56.11.61:3306 - 正式機
- 61.56.11.201:3306 - 測試機
- 61.56.11.90:3306 - 預部署機
- 61.56.11.91:3306 - 測試機的預部署機

## 連線方式
### 方法一
1. 先下載及安裝資料庫軟體（MySQL、DBeaver...）。
2. 新增資料庫連線。
3. 設定使用SSH通道（預設通訊埠為22）連線到資料庫主機，再利用localhost（127.0.0.1）的3306（MySQL預設）通訊埠連線至資料庫。

### 方法二
1. 以SSH連線至資料庫主機。
2. 開啟資料庫軟體。
```console
$ mysql -u <使用者名稱> -p  # 指定以使用者名稱及密碼開啟
Enter password:             # 輸入密碼
```

## 資料關聯
### 資料庫名稱：qpesums_web

各資料庫主機的名稱皆為qpesums_web。

```console
$ use qpesums_web;
```

### 資料表
1. 版本（auth）
   - 客製化版本、使用者：
   1. auth_group：客製化版本
      - name：客製化版本名稱

   2. auth_user：使用者資訊

   3. auth_user_groups：使用者客製化版本權限
      - user_id：所屬使用者資訊ID（auth_user）
      - group_id：所屬客製化版本ID（auth_group）

   - 操作功能權限：
   1. auth_permission：操作功能權限
   2. auth_group_permissions：客製化版本權限
   3. auth_user_user_permissions：使用者權限

2. 地圖（webmap）
   - 底圖：
   1. webmap_metadata：
   2. webmap_geomapdatafile：
   3. webmap_userperm：

3. 監控表格（rainmonitor）
   - 資料表、資料欄相關：
   1. rainmonitor_tagitem：監控表格清單

   2. rainmonitor_tagitemtype：產品種類
      - tag_type：資料種類
      - type_name：種類名稱

   3. rainmonitor_monitorcolumns：監控產品欄位
      - column_name：產品欄位名稱（與json檔有關，儲存於/data/qpesums_web_data/sectiondisplay_file/，39、61有時會互換）
        - section_name
        - section_name2
        - section_name3
        - section_name4
        - institution
        - item_num
        - alarm
        - alarm_reason
        - qpegc_1h
        - qpf_1h
        - qpe_1h_max
        - qpe_3h_ave
        - qpe_6h_ave
        - qpe_12h_ave
        - qpe_24h_ave
        - qpe_72h_ave
      - column_type：欄位屬性
        - info：測站／區域資訊
        - data：產品資料
      - default_name：預設正式名稱
      - tag_type_id：所屬產品種類ID（rainmonitor_tagitemtype）

   4. rainmonitor_tagitemcolumnmap：前端顯示監控表格欄位
      - display_name：欄位顯示名稱
      - column_order：欄位順序
      - tag_name_id：所屬監控表格ID（rainmonitor_tagitem）
      - is_active：欄位顯示與否
      - monitor_column_id：所屬監控產品欄位ID（rainmonitor_monitorcolumns）

   - 資料相關：
   1. rainmonitor_gridareameta：區域資料
      - area_name：區域名稱
      - area_code：區域編碼（e.g. THBbr001）

   2. rainmonitor_monitorsectionmeta：詳細區域資料
      - section_code：區域編碼（e.g. thbqpeqpfbridge_0101）
      - section_name：區域名稱
      - section_name2：區域名稱2
      - institution：機構單位
      - group_id：所屬客製化版本ID（auth_group）
      - item_num：項次


### 補充：匯入門檻值

監控表格門檻值檔案格式：

> item_num,num_code,institution,section_name,section_name2,stid,stname,QPEGC_1H_max,QPEGC_1H_ave,QPEGC_3H_ave,QPEGC_6H_ave,QPEGC_12H_ave,QPEGC_24H_ave,QPEGC_72H_ave,alarm_level

其中產品名稱由insert_THB_condition.py所寫定，並非可以隨意名稱寫入資料庫。

```console
$ docker exec qpesums_web python manage.py runscript \ 
insert_THB_condition --script-args \ 
/mnt2/qpesums_web_data/csv/<監控表格ID>_<日期>_qpeqpf.csv \ 
<監控表格ID> area
```