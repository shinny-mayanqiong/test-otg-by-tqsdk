

import csv

import requests

from md.md_test_on_trading import HEADER_ROW
from md.md_test_quotes_list import SYMBOLS_LIST

if __name__ == "__main__":
    for t in ["new", "old"]:
        csv_file = open(f"quotes_not_on_trading_time/quotes_from_{t}_md", 'w', newline='')
        csv_writer = csv.writer(csv_file, dialect='excel')

        for p in ["", "1"]:
            r_csvfile = open(f'quotes_not_on_trading_time/quotes_{t}{p}.csv', newline='')
            reader = csv.reader(r_csvfile)
            for r in reader:
                csv_writer.writerow(r)
            r_csvfile.close()

        csv_file.close()
