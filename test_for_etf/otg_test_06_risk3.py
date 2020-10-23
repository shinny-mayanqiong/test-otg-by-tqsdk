#!/usr/bin/env python
#  -*- coding: utf-8 -*-


from tqsdk import TqApi, TqAccount

from otg_check_helper import check_orders, check_positions, check_account, check_risk_rule, check_risk_data, check_all
from test_for_etf.base_info import bid, user_id, pwd, td_url, test_logger


if __name__ == '__main__':
    api = TqApi(TqAccount(bid, user_id, pwd), auth="ringo,Shinnytech123", _stock=True, _td_url=td_url)

    # 成交持仓比风控规则
    rule = api.set_risk_management_rule("SSE", True, trade_units_limit=6, trade_position_ratio_limit=150)

    test_logger.info(f"{'='*12} 期权 开仓 {'='*12}")
    symbol = "SSE.10002477"
    quote = api.get_quote(symbol)  # ETF 期权
    # 挂单
    buy_order = api.insert_order(symbol=symbol, direction="BUY", offset="OPEN", limit_price=quote.ask_price1, volume=10)
    while buy_order.status == "ALIVE":
        api.wait_update()
    check_all(api, bid, user_id)
    check_risk_rule(api, None)
    check_risk_data(api, symbol)
    api.close()
