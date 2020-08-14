#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'yanqiong'

from tqsdk import TqApi

def api_freeuser():
    api = TqApi(auth="ma_yanqiong@163.com,MaYanQiong")
    print(api._md_url)
    assert api._md_url == "wss://free-api.shinnytech.com/t/nfmd/front/mobile"
    api.close()

def api_vipuser():
    api = TqApi(auth="myanq@qq.com,MaYanQiong")
    print(api._md_url)
    assert api._md_url == "wss://api.shinnytech.com/t/nfmd/front/mobile"
    api.close()

def openmd_freeuser():
    api = TqApi(_stock=False, auth="ma_yanqiong@163.com,MaYanQiong")
    print(api._md_url)
    assert api._md_url == "wss://free-openmd.shinnytech.com/t/md/front/mobile"
    api.close()

def openmd_vipuser():
    api = TqApi(_stock=False, auth="myanq@qq.com,MaYanQiong")
    print(api._md_url)
    assert api._md_url == "wss://u.shinnytech.com/t/md/front/mobile"
    api.close()


if __name__ == '__main__':
    api_freeuser()
    api_vipuser()
    openmd_freeuser()
    openmd_vipuser()