#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
新旧行情服务器 合约信息是否一致 所有未到期的 SHFE,CFFEX,INE,DCE,CZCE,SSWE 的所有合约的所有共有信息
old : "wss://u.shinnytech.com/t/md/front/mobile"
new : "wss://api.shinnytech.com/t/nfmd/front/mobile"
"""

import logging

import requests
from tqsdk import TqApi, TqAccount
from tqsdk.utils import _query_for_quote

AUTH = "myanq@qq.com,MaYanQiong"
EXCHANGE_LIST = ["SHFE", "CFFEX", "INE", "DCE", "CZCE", "SSWE"]


def different(old_quote, new_quote, diff):
    for k, v in old_quote.items():
        # 已知有问题的部分
        if k == "expire_datetime":
            # if old_quote[k] * 1e9 != new_quote.get(k):
            #     diff.append(f"{k} >>> {old_quote[k]} >>> {new_quote.get(k)}")
            continue
        if k in ["margin", "commission"]:
            continue
        # 新版合约服务中已经删去的字段
        if k in ["ins_id", "ins_name", "sort_key", "delivery_year", "delivery_month"]:
            continue
        # 旧版合约服务里行情相关的数据不需要关心
        if k in ["settlement_price", "open_interest", "last_price", "pre_volume"]:
            continue
        if k == "product_id":
            if old_quote["class"] in ["FUTURE", "FUTURE_COMBINE"] and old_quote[k] != new_quote.get(k):
                diff.append(f"{k} >>> {old_quote[k]} >>> {new_quote.get(k)}")
            continue
        if k == "class":
            if not old_quote[k].endswith(new_quote.get(k)):
                diff.append(f"{k} >>> {old_quote[k]} >>> {new_quote.get(k)}")
            continue
        if k == "trading_time":
            for t in ['day', 'night']:
                if old_quote[k].get(t, []) != new_quote.get(k).get(t, []):
                    diff.append(f"trading_time {t} >>> {old_quote[k].get(t, [])} >>> {new_quote.get(k).get(t, [])}")
            continue
        if k == "leg1_symbol" or k == "leg2_symbol":
            continue
        if k == "py":
            if old_quote[k] != new_quote.get("english_name"):
                diff.append(
                    f"trading_time {t} >>> {old_quote[k].get(t, [])} >>> {new_quote.get(k, 'no english_name key')}")
            continue
        if k == "option_class":
            if old_quote[k] != new_quote.get("call_or_put"):
                diff.append(f"{k} >>> {old_quote[k]} >>> {new_quote.get('call_or_put')}")
            continue
        if k == "underlying_symbol":
            new_underlying_symbol = new_quote.get("underlying", {}).get("edges", [{"node": {}}])[0].get("node", {}).get(
                "instrument_id")
            if old_quote[k] != new_underlying_symbol:
                diff.append(f"{k} >>> {old_quote[k]} >>> {new_underlying_symbol}")
            continue
        if k == "underlying_multiple":
            new_underlying_multiple = new_quote.get("underlying", {}).get("edges", [{"node": {}}])[0].get(
                "underlying_multiple", None)
            if old_quote[k] != new_underlying_multiple:
                diff.append(f"{k} >>> {old_quote[k]} >>> {new_underlying_multiple}")
            continue

        if old_quote[k] != new_quote.get(k):
            diff.append(f"{k} >>> {old_quote[k]} >>> {new_quote.get(k, 'no this key')}")

    for k, v in new_quote.items():
        if k not in old_quote:
            if k in ["call_or_put", "english_name"]:
                continue  # 上面和旧版合约服务不同名字的字段比较
            if k in ["trading_day", "quote_multiple", "exercise_type", "last_exercise_day", "underlying"]:
                continue  # 旧版合约服务没有
            diff.append(f"{k} {new_quote.get(k, 'old_quote no this key')}")

if __name__ == '__main__':
    sh = logging.StreamHandler()
    logger = logging.getLogger("Test")
    logger.addHandler(sh)
    logger.setLevel(logging.INFO)

    rsp = requests.get(url="https://openmd.shinnytech.com/t/md/symbols/latest.json", timeout=30)
    old_symbols = {k: v for k,v in rsp.json().items() if v["expired"] is False and v["exchange_id"] in EXCHANGE_LIST}

    api = TqApi(auth=AUTH, _md_url="wss://api.shinnytech.com/t/nfmd/front/mobile")
    new_symbols_list = []
    for ex in EXCHANGE_LIST:
        symbols = api.query_quotes(exchange_id=ex, expired=False)
        new_symbols_list.extend(symbols)

    assert len(new_symbols_list) == len(old_symbols)

    print("已知问题：")
    print("* expire_datetime 为 null")
    print("* margin commission 部分合约不一致, 组合没有 volume_multiple, 指数、主连符合预期，SPOT 没有 expired product_short_name，")
    print("* 新版合约服务中已经删去的字段", ["ins_id", "ins_name", "sort_key", "delivery_year", "delivery_month"])
    print("* 旧版合约服务里行情相关的数据不需要关心", ["settlement_price", "open_interest", "last_price", "pre_volume"])

    symbols_diff = {}
    i = 0
    for symbol, old_quote in old_symbols.items():
        # i += 1
        # if i > 100:
        #     break
        query_pack = _query_for_quote(symbol)
        query_result = api.query_graphql(query=query_pack["query"], variables=query_pack["variables"])
        quotes = query_result.get("result", {}).get("symbol_info", [])
        assert len(quotes) == 1
        new_quote = quotes[0]
        assert new_quote["instrument_id"] == symbol
        diff = symbols_diff.setdefault(symbol, [])
        different(old_quote, new_quote, diff)

    for symbol, diffs in symbols_diff.items():
        if diffs:
            logger.info(f"{'-'*10} {symbol} {old_symbols[symbol]['class']} {'-'*20}")
            for d in diffs:
                logger.info(d)

    api.close()

