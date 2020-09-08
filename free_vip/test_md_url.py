#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'yanqiong'

import unittest
from datetime import datetime

from tqsdk import TqApi, TqBacktest, BacktestFinished
from tqsdk.tools import DataDownloader


def download(api):
    kd = DataDownloader(api, symbol_list="SHFE.cu2012", dur_sec=60,
                        start_dt=datetime(2020, 6, 1, 6, 0, 0), end_dt=datetime(2020, 6, 1, 16, 0, 0),
                        csv_file_name="kline.csv")
    while not kd.is_finished():
        api.wait_update()
        print(f"progress: kline: {kd.get_progress():8.2f} ")


class TestLmtIdx(unittest.TestCase):

    def test_api_freeuser(self):
        api = TqApi(auth="ma_yanqiong@163.com,MaYanQiong")
        self.assertEqual(api._md_url, "wss://free-api.shinnytech.com/t/nfmd/front/mobile")
        self.assertRaises(Exception, api.get_quote, "SSE.10002513")
        api.close()

    def test_api_vipuser(self):
        api = TqApi(auth="myanq@qq.com,MaYanQiong")
        self.assertEqual(api._md_url, "wss://api.shinnytech.com/t/nfmd/front/mobile")
        quote = api.get_quote("SSE.10002513")
        print(quote.datetime, quote.last_price)
        api.close()

    def test_openmd_freeuser(self):
        api = TqApi(_stock=False, auth="ma_yanqiong@163.com,MaYanQiong")
        self.assertEqual(api._md_url, "wss://free-openmd.shinnytech.com/t/md/front/mobile")
        self.assertRaises(Exception, api.get_quote, "SSE.000300")
        self.assertRaises(Exception, api.get_quote, "SSE.10002513")
        api.close()

    def test_openmd_vipuser(self):
        api = TqApi(_stock=False, auth="myanq@qq.com,MaYanQiong")
        self.assertEqual(api._md_url, "wss://u.shinnytech.com/t/md/front/mobile")
        self.assertRaises(Exception, api.get_quote, "SSE.000300")
        self.assertRaises(Exception, api.get_quote, "SSE.10002513")
        api.close()

    # -----------------------------------------------
    # backtest
    # -----------------------------------------------
    def test_api_freeuser_bt(self):
        bt = TqBacktest(start_dt=datetime(2020, 6, 1), end_dt=datetime(2020, 6, 2))
        self.assertRaises(Exception, TqApi, backtest=bt, auth="ma_yanqiong@163.com,MaYanQiong")

    def test_api_vipuser_bt(self):
        bt = TqBacktest(start_dt=datetime(2020, 6, 1), end_dt=datetime(2020, 6, 2))
        api = TqApi(backtest=bt, auth="myanq@qq.com,MaYanQiong")
        quote = api.get_quote("DCE.m2009")
        print(quote.datetime, quote.last_price)
        self.assertEqual("2020-05-29 22:59:59.999999", quote.datetime)
        self.assertEqual(2826.0, quote.last_price)
        api.close()

    def test_openmd_freeuser_bt(self):
        bt = TqBacktest(start_dt=datetime(2020, 6, 1), end_dt=datetime(2020, 6, 2))
        self.assertRaises(Exception, TqApi, _stock=False, backtest=bt, auth="ma_yanqiong@163.com,MaYanQiong")

    def test_openmd_vipuser_bt(self):
        bt = TqBacktest(start_dt=datetime(2020, 6, 1), end_dt=datetime(2020, 6, 2))
        api = TqApi(backtest=bt, _stock=False, auth="myanq@qq.com,MaYanQiong")
        quote = api.get_quote("DCE.m2009")
        print(quote.datetime, quote.last_price)
        self.assertEqual("2020-05-29 22:59:59.999999", quote.datetime)
        self.assertEqual(2826.0, quote.last_price)
        api.close()
        

    # -----------------------------------------------
    # download
    # -----------------------------------------------
    def test_api_freeuser_dl(self):
        api = TqApi(auth="ma_yanqiong@163.com,MaYanQiong")
        self.assertEqual(api._md_url, "wss://free-api.shinnytech.com/t/nfmd/front/mobile")
        self.assertRaises(Exception, download, api)
        api.close()

    def test_api_vipuser_dl(self):
        api = TqApi(auth="myanq@qq.com,MaYanQiong")
        self.assertEqual(api._md_url, "wss://api.shinnytech.com/t/nfmd/front/mobile")
        download(api)
        api.close()

    def test_openmd_freeuser_dl(self):
        api = TqApi(_stock=False, auth="ma_yanqiong@163.com,MaYanQiong")
        self.assertEqual(api._md_url, "wss://free-openmd.shinnytech.com/t/md/front/mobile")
        self.assertRaises(Exception, download, api)
        api.close()

    def test_openmd_vipuser_dl(self):
        api = TqApi(_stock=False, auth="myanq@qq.com,MaYanQiong")
        self.assertEqual(api._md_url, "wss://u.shinnytech.com/t/md/front/mobile")
        download(api)
        api.close()
