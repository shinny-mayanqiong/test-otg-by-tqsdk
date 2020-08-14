#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import time
import math
from tqsdk import TqApi, TqAccount
from datetime import datetime


import logging
logger = logging.getLogger("OTGTest")
logger.setLevel(logging.INFO)


def show_order(order, quote, is_ctp):
    logger.info(f"{order.exchange_id:>5}.{order.instrument_id:15} {order.direction:>6} {order.offset:>6} {order.limit_price:>6} "
                f"{order.volume_left:>8}/{order.volume_orign:<3} {order.frozen_margin:10} {order.frozen_premium:10}")
    if is_ctp:  # ctp frozen_margin frozen_premium 全为 0
        return
    if quote.ins_class == "FUTURE":
        assert order.frozen_premium == 0.0
        if order.offset == "OPEN":
            assert order.frozen_margin > 0.0
        else:
            assert order.frozen_margin == 0.0
    else:
        if order.offset == "CLOSE":
            assert order.frozen_margin == 0.0
            assert order.frozen_premium == 0.0
        elif order.direction == "BUY" and order.offset == "OPEN":
            assert order.frozen_margin == 0.0
            assert order.frozen_premium > 0.0
        elif order.direction == "SELL" and order.offset == "OPEN":
            assert order.frozen_margin > 0.0
            assert order.frozen_premium == 0.0


def show_future_position(pos, quote, is_ctp):
    logger.info(f"{'手数':>8} {'开仓价':>8} {'浮动盈亏':>8} {'持仓价':>8} {'持仓盈亏':>10} {'占用保证金':>10}")
    logger.info(f"多仓: {pos.pos_long:5} {pos.open_price_long:10.1f} {pos.float_profit_long:10.1f} {pos.position_price_long:10.1f} {pos.position_profit_long:10.1f} {pos.margin_long:10.1f}")
    logger.info(f"空仓: {pos.pos_short:5} {pos.open_price_short:10.1f} {pos.float_profit_short:10.1f} {pos.position_price_short:10.1f} {pos.position_profit_short:10.1f} {pos.margin_short:10.1f}")


def show_option_position(pos, quote, is_ctp):
    logger.info(f"{'手数':>8} {'开仓价':>8} {'浮动盈亏':>8} {'市值':>8} {'占用保证金':>10}")
    logger.info(
        f"多仓: {pos.pos_long:5} {pos.open_price_long:10.1f} {pos.float_profit_long:10.1f} {pos.market_value_long:10.1f} {pos.margin_long:10.1f}")
    logger.info(
        f"空仓: {pos.pos_short:5} {pos.open_price_short:10.1f} {pos.float_profit_short:10.1f} {pos.market_value_short:10.1f} {pos.margin_short:10.1f}")
    if pos.pos_long > 0:
        assert pos.market_value_long > 0.0  # 多仓市值 >0
        assert pos.margin_long == 0.0  # 多仓占用保证金 =0
    if pos.pos_short > 0:
        assert pos.market_value_short < 0.0  # 空仓市值 <0
        assert pos.margin_short > 0.0 if not is_ctp else True  # 空仓占用保证金 >0


def check_account(acc, positions, is_ctp):
    logger.info(f"===================== 检查账户字段 =====================")
    logger.info(f"静态权益 static_balance: {acc.static_balance}")
    #: 账户权益 （账户权益 = 动态权益 = 静态权益 + 平仓盈亏 + 持仓盈亏 - 手续费）
    logger.info(f"浮动盈亏 float_profit: {acc.float_profit}")
    logger.info(f"期权市值 market_value: {acc.market_value}")
    local_mv = sum(0 if math.isnan(pos.market_value) else pos.market_value for pos in positions.values())
    logger.info(f"本地计算持仓总市值: {local_mv} vs {acc.market_value}")
    # assert local_mv == acc.market_value

    local_balance = acc.static_balance + acc.close_profit + acc.premium - acc.commission + acc.position_profit + acc.market_value
    logger.info(f"账户权益 = 静态权益 + 日内(平仓盈亏 + 权利金 - 手续费) + 持仓盈亏 + 期权市值")
    logger.info(f"{local_balance} = {acc.static_balance} + {acc.close_profit} + {acc.premium} - {acc.commission} + {acc.position_profit} + {acc.market_value}")
    logger.info(f"账户权益 balance: {acc.balance}")
    logger.info(f"账户权益 ctp_balance: {acc.ctp_balance}")
    assert local_balance == acc.balance

    local_available = local_balance - acc.margin - acc.frozen_margin - acc.frozen_commission - acc.frozen_premium - acc.market_value
    logger.info(f"可用资金(包含持仓盈亏) = 账户权益 - 冻结保证金 - 保证金占用 - 冻结手续费 - 冻结权利金 - 期权市值", )
    logger.info(
        f"{local_available} = {local_balance} - {acc.frozen_margin} - {acc.margin} - {acc.frozen_commission} - {acc.frozen_premium} - {acc.market_value}", )

    local_available_without_position_profit = local_balance - acc.margin - acc.frozen_margin - acc.frozen_commission - acc.frozen_premium - acc.position_profit - acc.market_value
    logger.info(f"可用资金(去除持仓盈亏) = 账户权益 - 冻结保证金 - 保证金占用 - 冻结手续费 - 冻结权利金 - 持仓盈亏 - 期权市值", )
    logger.info(
        f"{local_available_without_position_profit} = {local_balance} - {acc.frozen_margin} - {acc.margin} - {acc.frozen_commission} - {acc.frozen_premium} - {acc.position_profit} - {acc.market_value}", )
    logger.info(f"可用资金 available: {acc.available}")
    logger.info(f"可用资金 ctp_available: {acc.ctp_available}")
    # assert local_available == acc.available or local_available_without_position_profit == acc.available

    local_risk_ratio = acc.margin / local_balance
    logger.info(f"风险度: {acc.risk_ratio} 本地计算: {local_risk_ratio}")
    # assert local_risk_ratio == acc.risk_ratio


def check_orders(orders, api, is_ctp):
    logger.info(f"===================== 检查所有挂单 =====================")
    logger.info(f"{'合约':>8} {'方向':>8} {'开平':>8} {'价格':>8} {'剩余/原始手数':>8} {'冻结保证金':>10} {'冻结权利金':>10}")
    for order in orders.values():
        if order.status == "FINISHED":
            continue
        quote = api.get_quote(f"{order.exchange_id}.{order.instrument_id}")
        show_order(order, quote, is_ctp)


def check_positions(positions, api, is_ctp):
    logger.info(f"===================== 检查所有持仓 =====================")
    for pos in positions.values():
        if pos.pos_long == 0 and pos.pos_short == 0:
            continue
        quote = api.get_quote(f"{pos.exchange_id}.{pos.instrument_id}")
        logger.info(f"{'-' * 10} {pos.exchange_id}.{pos.instrument_id} 最新价:{pos.last_price} {'-' * 10}")
        if quote.ins_class == "FUTURE":
            show_future_position(pos, quote, is_ctp)
        else:
            show_option_position(pos, quote, is_ctp)
        logger.info(f"{'-' * 60}")


def check_all(api, bid, user_id):
    is_ctp = False if bid == "快期模拟" else True
    while True:
        api.wait_update(deadline=time.time() + 30)
        orders = api._data["trade"][user_id]["orders"]
        is_all_orders_from_server = True
        for order in orders.values():
            if order.status == 'ALIVE' and order.insert_date_time == 0 and order.instrument_id != "IO2005-P-3750":
                is_all_orders_from_server = False
        # 等到所有 order 都是交易所回单
        if is_all_orders_from_server:
            positions = api._data["trade"][user_id]["positions"]
            orders = api._data["trade"][user_id]["orders"]
            account = api.get_account()
            check_orders(orders, api, is_ctp)
            check_positions(positions, api, is_ctp)
            check_account(account, positions, is_ctp)
            check_risk_rule(api)
            check_risk_data(api)
            break


def show_risk_rule(api, exchange_id):
    rule = api.get_risk_management_rule(exchange_id=exchange_id)
    logger.info(f"{'-' * 20} {exchange_id} {rule['enable']} {'-' * 20}")
    logger.info(f"{'-' * 2} {rule.self_trade}")
    logger.info(f"{'-' * 2} {rule.frequent_cancellation}")
    logger.info(f"{'-' * 2} {rule.trade_position_ratio}")


def check_risk_rule(api):
    logger.info(f"===================== 风控规则 =====================")
    show_risk_rule(api, exchange_id="SSE")
    show_risk_rule(api, exchange_id="SZSE")


def show_risk_data(risk_data):
    logger.info(f"{'-' * 20} {risk_data.instrument_id} {'-' * 20}")
    logger.info(f"{'-' * 2} {risk_data.self_trade}")
    logger.info(f"{'-' * 2} {risk_data.frequent_cancellation}")
    logger.info(f"{'-' * 2} {risk_data.trade_position_ratio}")

def check_risk_data(api, symbols=[]):
    logger.info(f"===================== 风控数据 =====================")
    symbols = symbols if isinstance(symbols, list) else [symbols]
    if symbols:
        for s in symbols:
            risk_data = api.get_risk_management_data(s)
            show_risk_data(risk_data)
    else:
        datas = api.get_risk_management_data()
        for risk_data in datas.items():
            show_risk_data(risk_data)

