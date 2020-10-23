#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
登录并打印账户信息
"""

import logging
from tqsdk import TqApi, TqAccount

from otg_check_helper import check_orders, check_positions, check_account, check_risk_rule, check_risk_data, check_all
from test_for_etf.base_info import bid, user_id, pwd, td_url, test_logger

if __name__ == '__main__':
    api = TqApi(TqAccount(bid, user_id, pwd), url=td_url, auth="ringo,Shinnytech123")
    check_all(api, bid, user_id, show_risk=True)
    test_logger.info(f"{'='*12} 期权 卖开仓 {'='*12}")
    symbol = "SSE.10002477"  # ETF 期权
    quote = api.get_quote(symbol)  # ETF 期权
    order = api.insert_order(symbol=symbol, direction="SELL", offset="OPEN", limit_price=quote.ask_price1, volume=3)
    api.wait_update()
    api.cancel_order(order)
    while order.status == "ALIVE":
        api.wait_update()
    api.close()
