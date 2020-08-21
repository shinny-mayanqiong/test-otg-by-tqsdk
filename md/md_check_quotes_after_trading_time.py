

import csv

import requests

from md.md_test_on_trading import HEADER_ROW
from md.md_test_quotes_list import SYMBOLS_LIST

if __name__ == "__main__":
    symbols = SYMBOLS_LIST
    cols = ["symbol"] + HEADER_ROW

    new_csvfile = open(f'quotes_not_on_trading_time/quotes_from_newmd.csv', newline='')
    old_csvfile = open(f'quotes_not_on_trading_time/quotes_from_oldmd.csv', newline='')
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
            if col in ["last_price"]:
                pass
            if old_quote[col] != new_quote[col]:
                print(f"{s} {col} ==> {old_quote[col]} != {new_quote[col]}")

    old_csvfile.close()
    new_csvfile.close()
