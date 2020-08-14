#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import time
import math
from tqsdk import TqApi, TqAccount
from datetime import datetime


import logging

from otg_check_helper import check_all, check_orders, check_positions, check_account, check_risk_rule, check_risk_data


def run_tianqin_code(bid, user_id, pwd, td_url):
    api = TqApi(TqAccount(bid, user_id, pwd), auth="myanq@qq.com,MaYanQiong", _stock=True, _td_url=td_url)
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
    check_risk_rule(api,None)
    check_risk_data(api,"SSE.10002513")

    api.set_risk_management_rule("SSE", True)




    logger.info(f"{'='*12} 期权 开仓 {'='*12}")
    quote = api.get_quote("SSE.10002513")  # ETF 期权
    # 挂单
    # order = api.insert_order(symbol="SSE.10002513", direction="BUY", offset="OPEN", limit_price=quote.lower_limit + quote.price_tick, volume=2)
    order = api.insert_order(symbol="SSE.10002513", direction="SELL", offset="OPEN", limit_price=quote.upper_limit - quote.price_tick, volume=2)
    # 可成交
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
    api.cancel_order(order)
    api.cancel_order(order)
    api.cancel_order(order)
    while order.status == "ALIVE":
        api.wait_update()
    check_all(api, bid, user_id)
    check_risk_rule(api,None)
    check_risk_data(api,"SSE.10002513")
    api.close()


if __name__ == '__main__':
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter('%(asctime)s - OTGTEST - %(levelname)s - %(message)s'))
    logger = logging.getLogger("OTGTest")
    logger.addHandler(sh)

    # bid, user_id, pwd = ("simnow", "103988", "MaYanQiong")
    bid, user_id, pwd = ("五矿经易_ETF", "000199", "Aa9168")

    logger.info(f"{'*' * 20} {bid} {user_id} {pwd} {'*' * 20}")
    run_tianqin_code(bid, user_id, pwd, "wss://test-t.shinnytech.com:37443/trade")


"""
2020-08-12 14:45:53,509 -  DEBUG - websocket message sent to ws://test_t.shinnytech.com:37480/trade: {"aid": "insert_order", "user_id": "000199", "order_id": "PYSDK_insert_5be75dedb6555919cc4dfc1119d4225a", "exchange_id": "SSE", "instrument_id": "10002513", "direction": "BUY", "offset": "OPEN", "volume": 3, "price_type": "BEST", "time_condition": "IOC", "volume_condition": "ALL"}
2020-08-12 14:45:53,622 -  DEBUG - websocket message received from ws://test_t.shinnytech.com:37480/trade: {"aid":"rtn_data","data":[{"trade":{"000199":{"user_id":"000199","trading_day":"","trade_more_data":false,"accounts":{},"positions":{},"orders":{"PYSDK_insert_5be75dedb6555919cc4dfc1119d4225a":{"seqno":16,"user_id":"000199","order_id":"PYSDK_insert_5be75dedb6555919cc4dfc1119d4225a","exchange_id":"SSE","instrument_id":"10002513","direction":"BUY","offset":"OPEN","volume_orign":3,"price_type":"BEST","limit_price":0.0,"time_condition":"IOC","volume_condition":"ALL","insert_date_time":1597214110000000000,"exchange_order_id":"","status":"FINISHED","volume_left":3,"last_msg":"已撤单报单被拒绝12038","frozen_margin":0.0,"frozen_premium":0.0,"frozen_commm
ission":0.0}},"trades":{},"banks":{},"transfers":{},"pre_insert_orders":{},"risk_management_rule":{},"risk_management_data":{}}}}]}


2020-08-12 14:46:34,727 -  DEBUG - websocket message sent to ws://test_t.shinnytech.com:37480/trade: {"aid": "insert_order", "user_id": "000199", "order_id": "PYSDK_insert_988ec85dc4389fb8987a469c2fc4d727", "exchange_id": "SSE", "instrument_id": "10002513", "direction": "BUY", "offset": "OPEN", "volume": 3, "price_type": "BEST", "time_condition": "IOC", "volume_condition": "ALL"}
2020-08-12 14:46:35,069 -  DEBUG - websocket message received from ws://test_t.shinnytech.com:37480/trade: {"aid":"rtn_data","data":[{"trade":{"000199":{"user_id":"000199","trading_day":"","trade_more_data":false,"accounts":{},"positions":{},"orders":{"PYSDK_insert_988ec85dc4389fb8987a469c2fc4d727":{"seqno":18,"user_id":"000199","order_id":"PYSDK_insert_988ec85dc4389fb8987a469c2fc4d727","exchange_id":"SSE","instrument_id":"10002513","direction":"BUY","offset":"OPEN","volume_orign":3,"price_type":"BEST","limit_price":0.0,"time_condition":"IOC","volume_condition":"ALL","insert_date_time":1597214151000000000,"exchange_order_id":"1025059","status":"FINISHED","volume_left":0,"last_msg":"全部成交报单已提交","frozen_margin":0.0,"frozen_premium":0.0,"frozen__
commission":0.0}},"trades":{},"banks":{},"transfers":{},"pre_insert_orders":{},"risk_management_rule":{},"risk_management_data":{}}}}]}

"""