#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
分期货公司比较盘后的行情
"""

import csv

from md.md_test_on_trading import HEADER_ROW

EXCHANGE_LIST = ["SHFE", "CFFEX", "INE", "DCE", "CZCE", "KQ", "SSWE"]

if __name__ == "__main__":
    dt = "2020-08-23-14-38-15"
    cols = ["symbol"] + HEADER_ROW
    for ex in EXCHANGE_LIST:
        print(f"=== {ex} {dt} ===")
        old_csvfile = open(f'/Volumes/share/mayanqiong/quotes_not_on_trading_time/quotes_{dt}_{ex}_old.csv', newline='')
        new_csvfile = open(f'/Volumes/share/mayanqiong/quotes_not_on_trading_time/quotes_{dt}_{ex}_new.csv', newline='')
        old_csv_reader = csv.DictReader(old_csvfile)
        new_csv_reader = csv.DictReader(new_csvfile)

        try:
            while True:
                old_quote = next(old_csv_reader)
                new_quote = next(new_csv_reader)
                assert old_quote["symbol"] == new_quote["symbol"]
                s = old_quote["symbol"]
                for k in old_quote:
                    if k in ["average", "datetime"]:
                        # average 保留小数位数不一样
                        # datetime KQ 可能我们计算的问题； SHFE CZCE INE CFFEX 时间超过交易时间段
                        continue
                    if k.find("bid") > -1 or k.find("ask") > -1:
                        # 买卖价格不一样
                        continue
                    if k in ["last_price", "close"]:
                        # if old_quote[col] != new_quote[col] and new_quote[col] == 'nan':
                        #     print(f"{s} {col} ==> {old_quote[col]} != {new_quote[col]}")
                        # if old_quote[col] != new_quote[col]:
                        #     print(f"{s} {col} ==> {old_quote[col]} != {new_quote[col]}")
                        continue
                    if old_quote[k] != new_quote[k]:
                        # volume amount open_interest 有些字段需要乘2 KQ 还有 2001 合约
                        if float(old_quote[k]) == float(new_quote[k]) * 2:  # 跳过刚好两倍的值
                            continue
                        print(f"{s} {k} ==> {old_quote[k]} != {new_quote[k]}")
        except:
            print(f"=== {ex} {dt} 比较的合约个数 {old_csv_reader.line_num-1} ===")
        old_csvfile.close()
        new_csvfile.close()
