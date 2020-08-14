#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'yanqiong'

from datetime import datetime

from tqsdk import TqApi
from tqsdk.tools import DataDownloader


def check(stock, auth, md_url=None):
    with TqApi(_stock=stock, auth=auth, _md_url=md_url) as api:
        kd = DataDownloader(api, symbol_list="SHFE.cu2012", dur_sec=60,
                        start_dt=datetime(2020, 6, 1, 6, 0, 0), end_dt=datetime(2020, 6, 1, 16, 0, 0),
                        csv_file_name="kline.csv")
        while not kd.is_finished():
            api.wait_update()
            print(f"progress: kline: {kd.get_progress():8.2f} ")


if __name__ == '__main__':
    # check(stock=False, auth="myanq@qq.com,MaYanQiong")
    # check(stock=True, auth="myanq@qq.com,MaYanQiong")

    # exceptions
    # check(stock=False, auth="ma_yanqiong@163.com,MaYanQiong")
    # check(stock=True, auth="ma_yanqiong@163.com,MaYanQiong")

    # timeout
    # check(stock=False, auth="myanq@qq.com,MaYanQiong", md_url="wss://free-openmd.shinnytech.com/t/md/front/mobile")
    # check(stock=True, auth="myanq@qq.com,MaYanQiong", md_url="wss://free-api.shinnytech.com/t/nfmd/front/mobile")
    pass
