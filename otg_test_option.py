#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import time
import math
from tqsdk import TqApi, TqAccount
from datetime import datetime


import logging

from otg_check_helper import check_all, check_orders, check_positions, check_account


def run_tianqin_code(bid, user_id, pwd, td_url):
    api = TqApi(TqAccount(bid, user_id, pwd), auth="myanq@qq.com,MaYanQiong", _stock=True,
                _md_url="wss://nfmd.shinnytech.com/t/nfmd/front/mobile", _td_url=td_url)
    print(api._md_url)
    is_ctp = False if bid == "快期模拟" else True
    account = api.get_account()
    if bid == "快期模拟":
        assert account.ctp_balance == '-' or math.isnan(account.ctp_balance)
        assert account.ctp_available == '-' or math.isnan(account.ctp_available)
    else:
        logger.info(f"{account.ctp_balance}, {account.ctp_available}")

    logger.info(f"{'='*30} 登录成功后，账户初始状态 {'='*30}")
    positions = api._data["trade"][user_id]["positions"]
    orders = api._data["trade"][user_id]["orders"]
    check_orders(orders, api, is_ctp)
    check_positions(positions, api, is_ctp)
    check_account(account, positions, is_ctp)

    logger.info(f"{'='*12} 期权 开仓 {'='*12}")
    quote = api.get_quote("CZCE.RM105")  # ETF 期权
    print(quote)
    # 挂单
    # order = api.insert_order(symbol="SSE.10002513", direction="BUY", offset="OPEN", limit_price=quote.lower_limit + quote.price_tick, volume=2)
    # 可成交
    order = api.insert_order(symbol="CZCE.RM105", direction="BUY", offset="OPEN", limit_price=quote.ask_price1, volume=1)
    # order = api.insert_order(symbol="SSE.10002513", direction="BUY", offset="OPEN", limit_price=quote.ask_price1, volume=3)
    # 可成交 FAK 下单失败,CTP:交易所不支持的价格类型
    # order = api.insert_order(symbol="SSE.10002513", direction="BUY", offset="OPEN", limit_price=quote.ask_price1, volume=2, advanced="FAK")
    # 可成交 FOK
    # order = api.insert_order(symbol="SSE.10002513", direction="BUY", offset="OPEN", limit_price=quote.ask_price1, volume=2, advanced="FOK")

    # BEST
    # order = api.insert_order(symbol="SSE.10002513", direction="SELL", offset="CLOSE", limit_price="BEST", volume=10)
    # BEST FOK 下单失败,已撤单报单被拒绝12038，合约代码:SSE.10002513，下单方向:买，开平标志:开仓，委托价格:最优价，委托手数:3
    # order = api.insert_order(symbol="SSE.10002513", direction="SELL", offset="CLOSE", limit_price="BEST", volume=3, advanced="FOK")

    # any_price 通知: 下单失败,CTP:交易所不支持的价格类型
    # order = api.insert_order(symbol="SSE.10002513", direction="BUY", offset="OPEN", volume=3)
    # FIVELEVEL 通知: 下单失败,CTP:交易所不支持的价格类型
    # order = api.insert_order(symbol="SSE.10002513", direction="BUY", offset="OPEN", limit_price="FIVELEVEL", volume=3)

    while order.status == "ALIVE":
        api.wait_update()
    api.wait_update()
    api.wait_update()
    check_all(api, bid, user_id)

    # logger.info(f"{'='*30} 发平仓挂单 {'='*30}")
    # positions = api._data["trade"][user_id]["positions"]
    # for pos in positions.values():
    #     symbol = f"{pos.exchange_id}.{pos.instrument_id}"
    #     quote = api.get_quote(symbol)
    #     if pos.pos_long > 0:
    #         api.insert_order(symbol=symbol, direction="SELL", offset="CLOSE",
    #                          limit_price=quote.upper_limit - quote.price_tick,
    #                          volume=pos.pos_long)
    #     if pos.pos_short > 0:
    #         api.insert_order(symbol=symbol, direction="BUY", offset="CLOSE",
    #                          limit_price=quote.lower_limit + quote.price_tick,
    #                          volume=pos.pos_short)
    # check_all(api, bid, user_id)
    api.close()


if __name__ == '__main__':
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter('%(asctime)s - OTGTEST - %(levelname)s - %(message)s'))
    logger = logging.getLogger("OTGTest")
    logger.addHandler(sh)

    bid, user_id, pwd = ("simnow", "103988", "MaYanQiong")
    # bid, user_id, pwd = ("五矿经易_ETF", "000199", "Aa9168")

    logger.info(f"{'*' * 20} {bid} {user_id} {pwd} {'*' * 20}")
    run_tianqin_code(bid, user_id, pwd, "wss://test-t.shinnytech.com:443/trade")
