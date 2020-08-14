#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import logging
import time
import math
from tqsdk import TqApi, TqAccount
from datetime import datetime

from otg_check_helper import check_orders, check_positions, check_account, check_risk_rule, check_risk_data

if __name__ == '__main__':
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter('%(asctime)s - OTGTEST - %(levelname)s - %(message)s'))
    logger = logging.getLogger("OTGTest")
    logger.addHandler(sh)

    # bid, user_id, pwd = ("simnow", "103988", "MaYanQiong")
    bid, user_id, pwd = ("五矿经易_ETF", "000199", "Aa9168")

    logger.info(f"{'*' * 20} {bid} {user_id} {pwd} {'*' * 20}")
    api = TqApi(TqAccount(bid, user_id, pwd), auth="myanq@qq.com,MaYanQiong", _td_url="wss://test-t.shinnytech.com:37443/trade")
    # api = TqApi(TqAccount(bid, user_id, pwd), auth="myanq@qq.com,MaYanQiong", _td_url="ws://test_t.shinnytech.com:80/trade")

    is_ctp = False if bid == "快期模拟" else True
    account = api.get_account()
    if bid == "快期模拟":
        assert account.ctp_balance == '-' or math.isnan(account.ctp_balance)
        assert account.ctp_available == '-' or math.isnan(account.ctp_available)
    else:
        logger.info(f"{account.ctp_balance}, {account.ctp_available}")

    logger.info(f"{'=' * 30} 登录成功后，账户初始状态 {'=' * 30}")
    positions = api._data["trade"][user_id]["positions"]
    orders = api._data["trade"][user_id]["orders"]
    check_orders(orders, api, is_ctp)
    check_positions(positions, api, is_ctp)
    check_account(account, positions, is_ctp)
    check_risk_rule(api)
    check_risk_data(api)
    api.close()
