#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
新旧行情服务器 合约信息是否一致 所有未到期的 SHFE,CFFEX,INE,DCE,CZCE,SSWE 的所有合约的所有共有信息
old : "wss://u.shinnytech.com/t/md/front/mobile"
new : "wss://api.shinnytech.com/t/nfmd/front/mobile"

在非交易时段针对每个合约(包括到期合约)，最大长度的 tick, kline 1s/5s/15s/30s/1m/5m/15m/30m/1h/2h/4h/1d/7d 数据并进行对比
组合合约没有k线数据因此会获取数据超时，这里需要测试的是新老系统都会超时
"""

import os

import csv
import multiprocessing as mp
from datetime import datetime

import requests
from tqsdk import TqApi
from tqsdk.diff import _get_obj
from tqsdk.utils import _generate_uuid

from md.md_test_quotes_list import SYMBOLS_LIST

AUTH = "myanq@qq.com,MaYanQiong"
EXCHANGE_LIST = ["SHFE", "CFFEX", "INE", "DCE", "CZCE", "KQ", "SSWE"]
DATA_LENGTH = 8964

KLINES_COLS = ["open", "high", "low", "close", "volume", "open_oi", "close_oi"]

TICKS_COLS = ["last_price", "highest", "lowest", "bid_price1", "bid_volume1", "ask_price1", "ask_volume1", "volume",
         "amount", "open_interest"]

def download_symbol_dur(s, dur, api, file_name):
    csv_file = open(file_name, 'w', newline='')
    csv_writer = csv.writer(csv_file, dialect='excel')
    data_cols = KLINES_COLS if dur > 0 else TICKS_COLS
    csv_writer.writerow(["id", "datetime_nano", "datetime"] + data_cols)
    chart_info = {
        "aid": "set_chart",
        "chart_id": _generate_uuid("PYSDK_downloader"),
        "ins_list": s,
        "duration": int(dur*1e9),
        "view_width": DATA_LENGTH
    }
    api._send_chan.send_nowait(chart_info)
    chart = _get_obj(api._data, ["charts", chart_info["chart_id"]])
    path = ["klines", s, str(int(dur*1e9))] if dur > 0 else ["ticks", s]
    serial = _get_obj(api._data, path)
    while True:
        api.wait_update()
        left_id = chart.get("left_id", -1)
        right_id = chart.get("right_id", -1)
        last_id = serial.get("last_id", -1)
        if (right_id > -1 and last_id > -1) and api._data.get("mdhis_more_data", True) is False:
            break
    for current_id in range(max(left_id, 0), right_id+1):
        item = serial["data"].get(str(current_id), {})
        row = [str(current_id), item["datetime"], _nano_to_str(item["datetime"])]
        for col in data_cols:
            row.append(item.get(col, "#N/A"))
        csv_writer.writerow(row)
    api._send_chan.send_nowait({
        "aid": "set_chart",
        "chart_id": chart_info["chart_id"],
        "ins_list": "",
        "duration": int(dur*1e9),
        "view_width": DATA_LENGTH,
    })
    api.wait_update()
    csv_file.close()


def _nano_to_str(nano):
    dt = datetime.fromtimestamp(nano // 1000000000)
    s = dt.strftime('%Y-%m-%d %H:%M:%S')
    s += '.' + str(int(nano % 1000000000)).zfill(9)
    return s


def record_ticks(symbols, _stock, _md_url):
    api = TqApi(auth=AUTH, _stock=_stock, _md_url=_md_url)
    for i in range(len(symbols)):
        s = symbols[i]
        os.makedirs(f"klines/{s}", exist_ok=True)
        for dur in [0, 1, 5, 15, 30, 60, 60*5, 60*15, 60*30, 60*60, 60*60*2, 60*60*4, 60*60*24, 60*60*24*7]:
            file_name = f"klines/{s}/{'ticks' if dur == 0 else 'klines_' + str(dur)}_{'new' if _stock else 'old'}.csv"
            download_symbol_dur(s, dur, api, file_name)
        print(f"{'new' if _stock else 'old'} 完成 {s} 进度 {i / len(symbols):6.2}%")
    api.close()


if __name__ == '__main__':
    # rsp = requests.get(url="https://openmd.shinnytech.com/t/md/symbols/latest.json", timeout=30)
    # symbols = [k for k,v in rsp.json().items() if v["exchange_id"] in EXCHANGE_LIST]  # 全部合约
    # symbols = [k for k,v in rsp.json().items() if v["class"] != "FUTURE_COMBINE"]  # 非组合数据
    # combine_symbols = [k for k,v in rsp.json().items() if v["class"] == "FUTURE_COMBINE"]  # 组合数据
    old_symbols = SYMBOLS_LIST[SYMBOLS_LIST.index("CZCE.MA009P1825"):]
    new_symbols = SYMBOLS_LIST[SYMBOLS_LIST.index("CZCE.RM005C2850"):]
    # "CZCE.MA009P1825"  #old
    # "CZCE.RM005C2850"  #new
    old_md = mp.Process(target=record_ticks, args=(old_symbols, False, "wss://u.shinnytech.com/t/md/front/mobile"))
    new_md = mp.Process(target=record_ticks, args=(new_symbols, True, "wss://api.shinnytech.com/t/nfmd/front/mobile"))
    old_md.start()
    new_md.start()
    old_md.join()
    new_md.join()
