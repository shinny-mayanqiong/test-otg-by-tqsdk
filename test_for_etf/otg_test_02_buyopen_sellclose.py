#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
登录并打印账户信息
"""

import logging
from tqsdk import TqApi, TqAccount

from otg_check_helper import check_orders, check_positions, check_account, check_risk_rule, check_risk_data, check_all
from test_for_etf.base_info import bid, user_id, pwd, td_url, test_logger


symbol = "SSE.10002477"  # ETF 期权

def buy_open():
    api = TqApi(TqAccount(bid, user_id, pwd), url=td_url, auth="ringo,Shinnytech123")
    test_logger.info(f"{'=' * 12} 期权 买开仓 {'=' * 12}")
    quote = api.get_quote(symbol)  # ETF 期权
    order = api.insert_order(symbol=symbol, direction="BUY", offset="OPEN", limit_price=quote.ask_price1, volume=3)
    while order.status == "ALIVE":
        api.wait_update()
    api.wait_update()
    api.close()


def sell_close():
    api = TqApi(TqAccount(bid, user_id, pwd), url=td_url, auth="ringo,Shinnytech123")
    test_logger.info(f"{'='*12} 期权 卖平仓 {'='*12}")
    quote = api.get_quote(symbol)  # ETF 期权
    order = api.insert_order(symbol=symbol, direction="SELL", offset="CLOSE", limit_price=quote.bid_price1, volume=3)
    while order.status == "ALIVE":
        api.wait_update()
    api.wait_update()
    api.close()


if __name__ == '__main__':
    buy_open()
    # sell_close()
