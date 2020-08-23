#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
新旧行情服务器 合约信息是否一致 所有未到期的 SHFE,CFFEX,INE,DCE,CZCE,SSWE 的所有合约的所有共有信息
old : "wss://u.shinnytech.com/t/md/front/mobile"
new : "wss://api.shinnytech.com/t/nfmd/front/mobile"

在非交易时段针对每个合约(包括到期合约)，获取新老行情系统的 quote
"""

import csv
import multiprocessing
import os
from datetime import datetime

import requests
from tqsdk import TqApi

from md.md_test_quotes_list import SYMBOLS_LIST

AUTH = "myanq@qq.com,MaYanQiong"
EXCHANGE_LIST = ["SHFE", "CFFEX", "INE", "DCE", "CZCE", "KQ", "SSWE"]

QUOTE_KEYS = ["datetime", "last_price", "highest", "lowest", "open", "close", "average", "volume", "amount",
"open_interest",
"settlement",
"upper_limit",
"lower_limit",
"pre_open_interest",
"pre_settlement",
"pre_close"]

for i in range(5):
    for t in ["ask_price", "ask_volume", "bid_price", "bid_volume"]:
        QUOTE_KEYS.append(t + str(i+1))


def record_quotes(args):
    symbols, file_name, _stock, _md_url = args
    api = TqApi(auth=AUTH, _stock=_stock, _md_url=_md_url)
    os.makedirs(f"S:/mayanqiong/quotes_not_on_trading_time", exist_ok=True)
    csv_file = open(f"S:/mayanqiong/quotes_not_on_trading_time/{file_name}", 'w', newline='')
    csv_writer = csv.writer(csv_file, dialect='excel')
    csv_writer.writerow(["symbol"] + QUOTE_KEYS)
    group_size = 20
    symbols_group = [symbols[i: i+group_size] for i in range(0, len(symbols), group_size)]
    for one_symbols in symbols_group:
        api._send_chan.send_nowait({
            "aid": "subscribe_quote",
            "ins_list": ",".join(one_symbols)
        })
        while True:
            api.wait_update()
            all_quotes_ready = True
            quotes = api._data.get("quotes", {})
            for s in one_symbols:
                if quotes.get(s, {}).get("datetime", "") == "":
                    all_quotes_ready = False
                    break
            if all_quotes_ready:
                break
        quotes = api._data.get("quotes", {})
        for s in one_symbols:
            quote = quotes.get(s)
            row = [s]
            for k in QUOTE_KEYS:
                row.append(quote.get(k))
            csv_writer.writerow(row)
    csv_file.close()
    api.close()

if __name__ == '__main__':
    rsp = requests.get(url="https://openmd.shinnytech.com/t/md/symbols/latest.json", timeout=30)
    symbols = rsp.json()
    symbols_group = {ex: [k for k, v in symbols.items() if v["exchange_id"] == ex] for ex in EXCHANGE_LIST}  # 按交易所分组合约
    inputs = []
    dt = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    for ex, symbols in symbols_group.items():
        inputs.append((symbols, f"quotes_{dt}_{ex}_old.csv", False, "wss://u.shinnytech.com/t/md/front/mobile"))
        inputs.append((symbols, f"quotes_{dt}_{ex}_new.csv", True, "wss://api.shinnytech.com/t/nfmd/front/mobile"))
    pool = multiprocessing.Pool(processes=14)
    pool_outputs = pool.map(record_quotes, inputs)
    pool.close()
    pool.join()
