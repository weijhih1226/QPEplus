---
title: QPESUMS產品及傳送機制
categories: [Linux , Perl , Crontab , QPESUMS , QPEplus]
tags: [Linux , Perl , Crontab , QPESUMS , QPEplus]
date: 2022/10/31
---

# QPESUMS產品及傳送機制

- 主機
  - 172.16.30.120（作業主機）
  - 172.16.30.121（備援主機）
- 作業帳號：sudo su -l qpesumsb
- 主目錄：/home/qpesumsB/

## QPESUMS產品

### 程式
- cwbprogram/warning_grid/ - 計算區域內QPE、QPF
  - src - Python程式
    - run_warning_grid.py
    - run_warning_grid_QPE.py
  - workdir/run_warning_grid.sh - 腳本
  - static - 靜態檔案
    - gridinfo/XXX_xxx_gridinfo_441x561.csv - 區域格點資訊
    - secinfo/XXX_xxx_secinfo.csv - 區域詳細資訊
    - shp - Shapefiles
  - outdata - 暫時產品輸出目錄
  - log - 暫時日誌記錄輸出目錄
  - tmp - 暫時目錄

### 例行排程
```console
$ crontab -e
0,10,20,30,40,50 * * * * /home/qpesumsB/.bashrc; /home/qpesumsB/cwbprogram/warning_grid/workdir/run_warning_grid.sh
```

### 產品輸出
- nidsB/txt/warning_grid/XXX/XXX_xxx_warning_grid_YYYYMMDD.hhmm.txt

### 日誌紀錄
- logs/run_warning_grid.log

## QPESUMS傳送機制

### 配置
- config/sending/customization/send2Qplus.config
  ```
  ### txt ###
  /home/qpesumsB/nidsB/txt/warning_grid/KHC    send2Qplus    *.txt
  /home/qpesumsB/nidsB/txt/warning_grid/THB    send2Qplus    *.txt
  ```

### 腳本
- scripts/sending/customization/send2Qplus.pl - 主程式
- scripts/sending/customization/send2Qplus_sub.pl - 副程式
  ```perl
  #txt
  if( ($type3 eq "txt") && ($type2 eq "warning_grid") && ($type1 eq "KHC") ){ &get_fn_latest_sending; }
  if( ($type3 eq "txt") && ($type2 eq "warning_grid") && ($type1 eq "THB") ){ &get_fn_latest_sending; }
  ```