#!/usr/bin/env python
#  -*- coding: utf-8 -*-


from tqsdk import TqApi, TqAccount

from otg_check_helper import check_orders, check_positions, check_account, check_risk_rule, check_risk_data, check_all
from test_for_etf.base_info import bid, user_id, pwd, td_url, test_logger


if __name__ == '__main__':
    api = TqApi(TqAccount(bid, user_id, pwd), auth="ringo,Shinnytech123", _stock=True, _td_url=td_url)

    # 触发自成交风控限制
    rule = api.set_risk_management_rule("SSE", True, count_limit=0)

    test_logger.info(f"{'='*12} 期权 开仓 {'='*12}")
    symbol = "SSE.10002477"
    quote = api.get_quote(symbol)  # ETF 期权
    # 挂单
    sell_order = api.insert_order(symbol=symbol, direction="SELL", offset="OPEN", limit_price=quote.upper_limit - quote.price_tick, volume=2)
    api.wait_update()
    buy_order = api.insert_order(symbol=symbol, direction="BUY", offset="OPEN", limit_price=quote.upper_limit, volume=2)
    while buy_order.status == "ALIVE":
        api.wait_update()
    api.wait_update()
    check_all(api, bid, user_id)
    check_risk_rule(api, None)
    check_risk_data(api, symbol)
    api.close()
