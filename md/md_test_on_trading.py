#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
新旧行情服务器 合约信息是否一致 所有未到期的 SHFE,CFFEX,INE,DCE,CZCE,SSWE 的所有合约的所有共有信息
old : "wss://u.shinnytech.com/t/md/front/mobile"
new : "wss://api.shinnytech.com/t/nfmd/front/mobile"


在交易时段新老系统同时订阅所有主连合约:
确认新老行情系统都没有跳过某笔更新，即从两个系统收到的 quote 数及除了时间的其他内容是一样的,且时间差不超过 300ms
计算从新行情系统收到同一笔行情的本地时间-从老行情系统收到数据的本地时间，计算出均值，中位数，1/4分位，3/4分位及最大及最小值

在交易时段新老系统同时订阅所有主力合约:
确认新老行情系统都没有跳过某笔更新，即从两个系统收到的 quote 数及内容是一样的
计算从新行情系统收到同一笔行情的本地时间-从老行情系统收到数据的本地时间，计算出均值，中位数，1/4分位，3/4分位及最大及最小值
"""
import csv
import multiprocessing as mp

import logging
import math
from datetime import datetime
from time import time

import requests
from tqsdk import TqApi, TqAccount
from tqsdk.utils import _query_for_quote

AUTH = "myanq@qq.com,MaYanQiong"
EXCHANGE_LIST = ["SHFE", "CFFEX", "INE", "DCE", "CZCE", "KQ", "SSWE"]
# EXCHANGE_LIST = ["SHFE"]

PRICE_KEYS = []
for i in range(5):
    for t in ["ask_price", "ask_volume", "bid_price", "bid_volume"]:
        PRICE_KEYS.append(t + str(i + 1))


HEADER_ROW = ["datetime", "last_price", "highest", "lowest", "open", "close", "average", "volume", "amount", "open_interest"] + PRICE_KEYS


def _str_to_nano(str):
    dt = datetime.strptime(str, "%Y-%m-%d %H:%M:%S.%f").timestamp()
    return dt*1e9


def record_quotes(symbols, _stock, _md_url):
    api = TqApi(auth=AUTH, _stock=_stock, _md_url=_md_url)
    api._requests["quotes"] = set(symbols)
    api._send_chan.send_nowait({
        "aid": "subscribe_quote",
        "ins_list": ",".join(symbols)
    })
    api.wait_update()
    api.wait_update()
    quotes = {}
    csv_files = {}
    for s in symbols:
        quotes[s] = api.get_quote(s)
        csv_files[s] = (create_csvfile(s, "new" if _stock else "old"))
        csv_files[s][1].writerow(["local_nano_time", "quote_nano_time"] + HEADER_ROW)
    end = time() + 60 * 60  # 记录 30 min 分钟的数据分析
    while True:
        if end < time():
            break
        api.wait_update()
        for s, q in quotes.items():
            if api.is_changing(q):
                csv_files[s][1].writerow([f"{time()*1e9:.0f}", f"{_str_to_nano(q['datetime']):.0f}"] + [q[k] for k in HEADER_ROW])
    close_csvfiles(csv_files)
    api.close()


def create_csvfile(symbol, prefix):
    csv_file = open(f"quotes2/trading_quote_{symbol}_{prefix}.csv", 'w', newline='')
    csv_writer = csv.writer(csv_file, dialect='excel')
    return csv_file, csv_writer


def close_csvfiles(csv_files):
    for csv_file, _ in csv_files.values():
        csv_file.close()


if __name__ == '__main__':
    rsp = requests.get(url="https://openmd.shinnytech.com/t/md/symbols/latest.json", timeout=30)
    symbols = [v["underlying_symbol"] for v in rsp.json().values() if v["class"] == "FUTURE_CONT"]
    symbols.extend([k for k, v in rsp.json().items() if v["class"] == "FUTURE_CONT"])

    old_md = mp.Process(target=record_quotes, args=(symbols, False, "wss://u.shinnytech.com/t/md/front/mobile"))
    new_md = mp.Process(target=record_quotes, args=(symbols, True, "wss://api.shinnytech.com/t/nfmd/front/mobile"))

    # 開始加速執行
    old_md.start()
    new_md.start()

    # 結束多進程
    old_md.join()
    new_md.join()
