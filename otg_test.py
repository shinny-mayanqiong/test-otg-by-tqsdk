#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import time
import math
from tqsdk import TqApi, TqAccount
from datetime import datetime


import logging

from otg_check_helper import check_all, check_orders, check_positions, check_account


def run_tianqin_code(bid, user_id, pwd, td_url):
    api = TqApi(TqAccount(bid, user_id, pwd), auth="myanq@qq.com,MaYanQiong", _td_url=td_url)
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

    logger.info(f"{'='*30} 全部撤单 & 全部平仓 {'='*30}")
    for order in orders.values():
        if order.status != "FINISHED":
            api.cancel_order(order)

    for pos in positions.values():
        symbol = f"{pos.exchange_id}.{pos.instrument_id}"
        quote = api.get_quote(symbol)
        if pos.pos_long > 0:
            api.insert_order(symbol=symbol, direction="SELL", offset="CLOSE",
                             limit_price=quote.bid_price1,
                             volume=pos.pos_long)
        if pos.pos_short > 0:
            api.insert_order(symbol=symbol, direction="BUY", offset="CLOSE",
                             limit_price=quote.ask_price1,
                             volume=pos.pos_short)

    while True:
        api.wait_update(deadline=time.time() + 30)
        # 全部持仓清 0
        is_all_clear = True
        for pos in positions.values():
            if pos.pos_long > 0 or pos.pos_short > 0:
                is_all_clear = False
        for order in orders.values():
            if order.status != "FINISHED":
                is_all_clear = False
        if is_all_clear:
            logger.info("全部撤单 & 全部平仓 ok")
            break
        else:
            logger.info("还没完成全部撤单 & 全部平仓")

    logger.info(f"{'='*12} 期货 开仓 {'='*12}")
    quote = api.get_quote("CZCE.RM105")
    api.insert_order(symbol="CZCE.RM105", direction="BUY", offset="OPEN", limit_price=quote.lower_limit + quote.price_tick,
                             volume=2)
    api.insert_order(symbol="CZCE.RM105", direction="BUY", offset="OPEN", limit_price=quote.ask_price1,
                             volume=3)
    quote1 = api.get_quote("CZCE.CF105")
    api.insert_order(symbol="CZCE.CF105", direction="SELL", offset="OPEN", limit_price=quote1.upper_limit - quote1.price_tick,
                     volume=2)
    api.insert_order(symbol="CZCE.CF105", direction="SELL", offset="OPEN", limit_price=quote1.bid_price1,
                     volume=3)
    check_all(api, bid, user_id)


    # logger.info(f"{'='*12} 期权 开仓 {'='*12}")
    # quote = api.get_quote("CZCE.RM009C2300")
    # api.insert_order(symbol="CZCE.RM009C2300", direction="BUY", offset="OPEN",
    #                          limit_price=quote.lower_limit + quote.price_tick,
    #                          volume=2)
    # api.insert_order(symbol="CZCE.RM009C2300", direction="BUY", offset="OPEN", limit_price=quote.ask_price1,
    #                          volume=3)
    # quote1 = api.get_quote("CZCE.CF009C11600")
    # api.insert_order(symbol="CZCE.CF009C11600", direction="SELL", offset="OPEN",
    #                          limit_price=quote1.upper_limit - quote1.price_tick,
    #                          volume=2)
    # api.insert_order(symbol="CZCE.CF009C11600", direction="SELL", offset="OPEN", limit_price=quote1.bid_price1,
    #                          volume=3)
    #
    # quote2 = api.get_quote("CZCE.RM009P2300")
    # api.insert_order(symbol="CZCE.RM009P2300", direction="BUY", offset="OPEN",
    #                  limit_price=quote2.lower_limit + quote2.price_tick,
    #                  volume=2)
    # api.insert_order(symbol="CZCE.RM009P2300", direction="BUY", offset="OPEN", limit_price=quote2.ask_price1,
    #                  volume=3)
    # quote3 = api.get_quote("CZCE.CF009C11600")
    # api.insert_order(symbol="CZCE.CF009P11600", direction="SELL", offset="OPEN",
    #                  limit_price=quote3.upper_limit - quote3.price_tick,
    #                  volume=2)
    # api.insert_order(symbol="CZCE.CF009P11600", direction="SELL", offset="OPEN", limit_price=quote3.bid_price1,
    #                  volume=3)

    # PUT
    # check_all(api, bid, user_id)

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
    # bid, user_id, pwd = ("simnow", "103988", "MaYanQiong")
    bid, user_id, pwd = ("五矿经易_ETF", "000199", "Aa9168")
    logger.info(f"{'*' * 20} {bid} {user_id} {pwd} {'*' * 20}")
    run_tianqin_code(bid, user_id, pwd, "ws://test_t.shinnytech.com:37480/trade")