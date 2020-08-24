#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
新旧行情服务器 合约信息是否一致 所有未到期的 SHFE,CFFEX,INE,DCE,CZCE,SSWE 的所有合约的所有共有信息
old : "wss://u.shinnytech.com/t/md/front/mobile"
new : "wss://api.shinnytech.com/t/nfmd/front/mobile"

在非交易时段针对每个合约(包括到期合约)，最大长度的 tick, kline 1s/5s/15s/30s/1m/5m/15m/30m/1h/2h/4h/1d/7d 数据并进行对比
组合合约没有k线数据因此会获取数据超时，这里需要测试的是新老系统都会超时

只记录 klines 下载超时与否，第一个和最后一个 id 信息
"""

import os

import csv
import multiprocessing as mp
from datetime import datetime
from time import time

import requests
from tqsdk import TqApi
from tqsdk.diff import _get_obj
from tqsdk.utils import _generate_uuid

import multiprocessing

AUTH = "myanq@qq.com,MaYanQiong"
EXCHANGE_LIST = ["SHFE", "CFFEX", "INE", "DCE", "CZCE", "KQ", "SSWE"]
DATA_LENGTH = 8964

KLINES_COLS = ["open", "high", "low", "close", "volume", "open_oi", "close_oi"]

TICKS_COLS = ["last_price", "highest", "lowest", "bid_price1", "bid_volume1", "ask_price1", "ask_volume1", "volume",
         "amount", "open_interest"]


async def download_symbol_dur(s, dur, api, server_type, chart_ids):
    chart_info = {
        "aid": "set_chart",
        "chart_id": chart_ids[dur]["chart_id"],
        "ins_list": s,
        "duration": int(dur*1e9),
        "view_width": DATA_LENGTH
    }
    await api._send_chan.send(chart_info)
    chart = _get_obj(api._data, ["charts", chart_info["chart_id"]])
    path = ["klines", s, str(int(dur*1e9))] if dur > 0 else ["ticks", s]
    serial = _get_obj(api._data, path)
    end_time = time() + 10
    async with api.register_update_notify() as chan:
        async for _ in chan:
            left_id = chart.get("left_id", -1)
            right_id = chart.get("right_id", -1)
            last_id = serial.get("last_id", -1)
            if (right_id > -1 and last_id > -1) and api._data.get("mdhis_more_data", True) is False:
                chart_ids[dur]["is_timeout"] = 0
                chart_ids[dur]["left_id"] = left_id
                chart_ids[dur]["right_id"] = right_id
                chart_ids[dur]["last_id"] = last_id
                break
    await api._send_chan.send({
        "aid": "set_chart",
        "chart_id": chart_ids[dur]["chart_id"],
        "ins_list": "",
        "duration": int(dur*1e9),
        "view_width": DATA_LENGTH,
    })


def _nano_to_str(nano):
    dt = datetime.fromtimestamp(nano // 1000000000)
    s = dt.strftime('%Y-%m-%d %H:%M:%S')
    s += '.' + str(int(nano % 1000000000)).zfill(9)
    return s


def download_symbol(symbol, _stock, api):
    chart_ids = {}
    server_type = 'new' if _stock else 'old'
    for dur in [0, 1, 5, 15, 30, 60, 60 * 5, 60 * 15, 60 * 30, 60 * 60, 60 * 60 * 2, 60 * 60 * 4, 60 * 60 * 24,
                60 * 60 * 24 * 7]:
        chart_id = _generate_uuid("PYSDK_downloader")
        chart_ids[dur] = {"chart_id": chart_id, "is_timeout": None, "left_id": None, "right_id": None, "last_id": None}
        chart_ids[dur]["task"] = api.create_task(download_symbol_dur(symbol, dur, api, server_type, chart_ids))
    end_time = time() + 20
    while True:
        api.wait_update(end_time)
        all_finished = True
        for dur, val in chart_ids.items():
            if val["is_timeout"] is None:
                all_finished = False
                break
        if all_finished or end_time < time():
            file_name = f"S:/mayanqiong/klines_combine/{symbol}_timeouts_{'new' if _stock else 'old'}.csv"
            csv_file = open(file_name, 'w', newline='')
            csv_writer = csv.writer(csv_file, dialect='excel')
            csv_writer.writerow(["symbol", "duration", "is_timeout", "server_type", "left_id", "right_id", "last_id"])
            for dur, val in chart_ids.items():
                if val["is_timeout"] is None:
                    print([symbol, dur, val["is_timeout"], server_type, val["left_id"], val["right_id"], val["last_id"]])
                csv_writer.writerow([symbol, dur, val["is_timeout"], server_type, val["left_id"], val["right_id"], val["last_id"]])
            csv_file.close()
            break

def record_ticks(args):
    symbols, _stock, _md_url = args
    api = TqApi(auth=AUTH, _stock=_stock, _md_url=_md_url)
    for symbol in symbols:
        os.makedirs(f"S:/mayanqiong/klines_combine", exist_ok=True)
        for dur in [0, 1, 5, 15, 30, 60, 60 * 5, 60 * 15, 60 * 30, 60 * 60, 60 * 60 * 2, 60 * 60 * 4, 60 * 60 * 24, 60 * 60 * 24 * 7]:
            download_symbol(symbol, dur, api)
    api.close()
    print(args)


def get_dir_size(dir):
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    return size


def clear_dirs():
    "删除文件数小于 14 的 new 、old 文件 "
    dir_list = os.listdir(f"S:/mayanqiong/klines_combine/")
    for d in dir_list:
        dir_file_list = os.listdir(f"S:/mayanqiong/klines_combine/{d}")
        file_list = {
            "old": [f for f in dir_file_list if f.find("old") > -1],
            "new": [f for f in dir_file_list if f.find("new") > -1]
        }
        for t in ["new", "old"]:
            if 0 < len(file_list[t]) < 14:
                for f in file_list[t]:
                    os.remove(f"S:/mayanqiong/klines_combine/{d}/{f}")
            else:
                for f in file_list[t]:
                    if os.path.getsize(f"S:/mayanqiong/klines_combine/{d}/{f}") < 128:
                        os.remove(f"S:/mayanqiong/klines_combine/{d}/{f}")


def has_downloaded(symbol, _stock):
    return os.path.exists(f"S:/mayanqiong/klines_combine/{symbol}_timeouts_{'new' if _stock else 'old'}.csv")


if __name__ == '__main__':
    # clear_dirs()
    rsp = requests.get(url="https://openmd.shinnytech.com/t/md/symbols/latest.json", timeout=30)
    symbols = [k for k,v in rsp.json().items() if v["exchange_id"] in EXCHANGE_LIST if v["class"] == "FUTURE_COMBINE"]
    inputs = []
    symbols_group = {'new': [], 'old': []}
    symbols_group_size = 5
    for s in symbols:
        if not has_downloaded(s, False):
            symbols_group['old'].append(s)
        if not has_downloaded(s, True):
            symbols_group['new'].append(s)
        if len(symbols_group['old']) >= symbols_group_size:
            inputs.append((symbols_group['old'], False, "wss://u.shinnytech.com/t/md/front/mobile"))
            symbols_group['old'] = []
        if len(symbols_group['new']) >= symbols_group_size:
            inputs.append((symbols_group['new'], True, "wss://api.shinnytech.com/t/nfmd/front/mobile"))
            symbols_group['new'] = []
    if symbols_group['old']:
        inputs.append((symbols_group['old'], False, "wss://u.shinnytech.com/t/md/front/mobile"))
    if symbols_group['new']:
        inputs.append((symbols_group['new'], True, "wss://api.shinnytech.com/t/nfmd/front/mobile"))
    print(len(inputs))
    pool = multiprocessing.Pool(processes=32)
    pool_outputs = pool.map(record_ticks, inputs)
    pool.close()
    pool.join()
