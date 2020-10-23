#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
买开
"""

from tqsdk import TqApi, TqAccount

from otg_check_helper import check_orders, check_positions, check_account, check_risk_rule, check_risk_data
from test_for_etf.base_info import bid, user_id, pwd, td_url, test_logger

if __name__ == '__main__':
    api = TqApi(TqAccount(bid, user_id, pwd), url=td_url, auth="ringo,Shinnytech123")

    account = api.get_account()
    positions = api._data["trade"][api._account._account_id]["positions"]
    orders = api._data["trade"][api._account._account_id]["orders"]

    # 显示各种信息
    test_logger.info(f"{'=' * 30} 登录成功后，账户初始状态 {'=' * 30}")
    is_ctp = False if api._account._broker_id == "快期模拟" else True
    check_orders(orders, api, is_ctp)
    check_positions(positions, api, is_ctp)
    check_account(account, positions, is_ctp)
    check_risk_rule(api)
    check_risk_data(api)
    api.close()
