

import csv

import requests

from md.md_test_on_trading import HEADER_ROW
from md.md_test_quotes_list import SYMBOLS_LIST

if __name__ == "__main__":
    symbols = SYMBOLS_LIST
    cols = ["symbol"] + HEADER_ROW
    print(len(symbols))

    new_csvfile = open(f'quotes_not_on_trading_time/quotes_from_new_md', newline='')
    old_csvfile = open(f'quotes_not_on_trading_time/quotes_from_old_md', newline='')
    old_csv_reader = csv.DictReader(old_csvfile)
    new_csv_reader = csv.DictReader(new_csvfile)

    for s in symbols:
        old_quote = next(old_csv_reader)
        new_quote = next(new_csv_reader)
        for col in cols:
            if col in ["average"]:
                continue
            if col in ["datetime"]:
                # KQ 可能我们计算的问题； SHFE CZCE INE CFFEX 时间超过交易时间段
                continue
            if col in ["last_price", "close"]:
                # if old_quote[col] != new_quote[col] and new_quote[col] == 'nan':
                #     print(f"{s} {col} ==> {old_quote[col]} != {new_quote[col]}")
                # if old_quote[col] != new_quote[col]:
                #     print(f"{s} {col} ==> {old_quote[col]} != {new_quote[col]}")
                continue
            if old_quote[col] != new_quote[col]:
                # volume amount open_interest 有些字段需要乘2 KQ 还有 2001 合约
                print(f"{s} {col} ==> {old_quote[col]} != {new_quote[col]}")
                continue

    old_csvfile.close()
    new_csvfile.close()
