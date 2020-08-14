#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'yanqiong'

from datetime import datetime

from tqsdk import TqApi, TqBacktest, BacktestFinished


def check(stock, auth, md_url=None):
    try:
        bt = TqBacktest(start_dt=datetime(2020, 6, 1), end_dt=datetime(2020, 6, 2))
        api = TqApi(backtest=bt, _stock=stock, auth=auth, _md_url=md_url)
        quote = api.get_quote("DCE.m2009")
        while True:
            print(quote.datetime, quote.last_price)
            api.wait_update()
    except BacktestFinished:
        api.close()


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
