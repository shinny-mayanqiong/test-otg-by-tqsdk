#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
新旧行情服务器 合约信息是否一致 所有未到期的 SHFE,CFFEX,INE,DCE,CZCE,SSWE 的所有合约的所有共有信息
old : "wss://u.shinnytech.com/t/md/front/mobile"
new : "wss://api.shinnytech.com/t/nfmd/front/mobile"

在非交易时段针对每个合约(包括到期合约)，获取新老行情系统的 quote
"""

import csv
import multiprocessing as mp
import os

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


def record_quotes(symbols, _stock, _md_url):
    api = TqApi(auth=AUTH, _stock=_stock, _md_url=_md_url)
    os.makedirs(f"quotes_not_on_trading_time", exist_ok=True)
    csv_file = open(f"quotes_not_on_trading_time/quotes_{'new' if _stock else 'old'}1.csv", 'w', newline='')
    csv_writer = csv.writer(csv_file, dialect='excel')
    csv_writer.writerow(["symbol"] + QUOTE_KEYS)
    for symbol in symbols:
        api._send_chan.send_nowait({
            "aid": "subscribe_quote",
            "ins_list": symbol
        })
        while True:
            api.wait_update()
            quote = api._data.get("quotes", {}).get(symbol, {})
            if quote and quote["datetime"] != "":
                break
        row = [symbol]
        for k in QUOTE_KEYS:
            row.append(quote.get(k))
        csv_writer.writerow(row)
    csv_file.close()
    api.close()

if __name__ == '__main__':
    # rsp = requests.get(url="https://openmd.shinnytech.com/t/md/symbols/latest.json", timeout=30)
    # symbols = [k for k,v in rsp.json().items() if v["exchange_id"] in EXCHANGE_LIST]  # 全部合约
    symbols = SYMBOLS_LIST[SYMBOLS_LIST.index("CZCE.RM005C2850"):]
    # old_symbols = SYMBOLS_LIST[SYMBOLS_LIST.index("CZCE.RM005C2850"):]
    # new_symbols = SYMBOLS_LIST[SYMBOLS_LIST.index("CZCE.RM005C2850"):]
    old_md = mp.Process(target=record_quotes, args=(symbols, False, "wss://u.shinnytech.com/t/md/front/mobile"))
    new_md = mp.Process(target=record_quotes, args=(symbols, True, "wss://api.shinnytech.com/t/nfmd/front/mobile"))
    old_md.start()
    new_md.start()
    old_md.join()
    new_md.join()
