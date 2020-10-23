#!/usr/bin/env python
#  -*- coding: utf-8 -*-


from tqsdk import TqApi, TqAccount

from otg_check_helper import check_orders, check_positions, check_account, check_risk_rule, check_risk_data, check_all
from test_for_etf.base_info import bid, user_id, pwd, td_url, test_logger


if __name__ == '__main__':
    api = TqApi(TqAccount(bid, user_id, pwd), auth="ringo,Shinnytech123", _stock=True, _td_url=td_url)

    # 频繁报撤单风控规则
    rule = api.set_risk_management_rule("SSE", True, insert_order_count_limit=6, cancel_order_count_limit=4, cancel_order_percent_limit=50)
    api.wait_update()

    test_logger.info(f"{'='*12} 期权 开仓 {'='*12}")
    symbol = "SSE.10002477"
    quote = api.get_quote(symbol)  # ETF 期权
    # 挂单
    order = api.insert_order(symbol=symbol, direction="SELL", offset="OPEN", limit_price=quote.ask_price1, volume=3)
    api.wait_update()
    api.cancel_order(order)
    while order.status == "ALIVE":
        api.wait_update()
    # check_all(api, bid, user_id, show_risk=True)
    # check_risk_rule(api, None)
    # check_risk_data(api, symbol)
    api.close()
