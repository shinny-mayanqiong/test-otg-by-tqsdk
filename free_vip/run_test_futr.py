#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'yanqiong'

from datetime import datetime

from tqsdk import TqApi
from tqsdk.tools import DataDownloader


def check(stock, auth, md_url=None):
    with TqApi(_stock=stock, auth=auth, _md_url=md_url) as api:
        quote = api.get_quote("SHFE.cu2009")
        print(quote.datetime, quote.last_price)


if __name__ == '__main__':
    check(stock=False, auth="myanq@qq.com,MaYanQiong")
    check(stock=True, auth="myanq@qq.com,MaYanQiong")

    check(stock=False, auth="ma_yanqiong@163.com,MaYanQiong")
    check(stock=True, auth="ma_yanqiong@163.com,MaYanQiong")

    check(stock=False, auth="myanq@qq.com,MaYanQiong", md_url="wss://free-openmd.shinnytech.com/t/md/front/mobile")
    check(stock=True, auth="myanq@qq.com,MaYanQiong", md_url="wss://free-api.shinnytech.com/t/nfmd/front/mobile")
    pass
