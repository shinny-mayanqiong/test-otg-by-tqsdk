#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
比较 ticks 信息的差别
"""
import multiprocessing
import os

import numpy as np
import pandas
import requests

EXCHANGE_LIST = ["SHFE", "CFFEX", "INE", "DCE", "CZCE", "KQ", "SSWE"]

KLINES_COLS = ["open", "high", "low", "close", "volume", "open_oi", "close_oi"]

TICKS_COLS = ["last_price", "highest", "lowest", "bid_price1", "bid_volume1", "ask_price1", "ask_volume1", "volume",
         "amount", "open_interest"]


def get_df_diff(df_old, df_new, cols):
    arr_diff = np.array([True for _ in range(df_old.shape[0])])
    for col in cols:
        arr_old = df_old[col].values
        arr_new = df_new[col].values
        np.logical_and(arr_diff, np.equal(arr_old, arr_new), arr_diff)
    if not np.all(arr_diff):
        np.logical_not(arr_diff, arr_diff)
        df_diff_old = df_old.loc[arr_diff]
        df_diff_new = df_new.loc[arr_diff]
        if not df_diff_old.empty:
            return f"{df_diff_old.to_string(index=False)}\n\n{df_diff_new.to_string(index=False)}"
    return None


def diff_two_csv(file_old, file_new, cols):
    """
    三种不同类型的错误
    timeout 有合约下载超时
    err_size 个数不同
    err_id 两边id值不同
    err_value 两边数值不同
    """
    df_old = pandas.read_csv(file_old)
    df_new = pandas.read_csv(file_new)
    if df_old.shape[0] == 0 or df_new.shape[0] == 0:
        return {
            "type": "timeout",
            "error": f"df_old: {repr(df_old.shape)}\ndf_new: {repr(df_new.shape)}"
        }
    elif df_old.shape != df_new.shape:
        return {
            "type": "err_size",
            "error": f"df_old: {repr(df_old.shape)}\ndf_new: {repr(df_new.shape)}"
        }
    elif df_old.iloc[0]["id"] != df_new.iloc[0]["id"] or df_old.iloc[-1]["id"] != df_new.iloc[-1]["id"]:
        return {
            "type": "err_id",
            "error": f"df_old: {df_old.iloc[0]['id']} ~ {df_old.iloc[-1]['id']}\ndf_new: {df_new.iloc[0]['id']} ~ {df_new.iloc[-1]['id']}"
        }
    r = get_df_diff(df_old, df_new, cols)
    if r:
        return {
            "type": "err_value",
            "error": r
        }
    return None


def diff_symbol(dir):
    diff_result = {}
    for dur in [0, 1, 5, 15, 30, 60, 60 * 5, 60 * 15, 60 * 30, 60 * 60, 60 * 60 * 2, 60 * 60 * 4, 60 * 60 * 24,
                60 * 60 * 24 * 7]:
        file_name_old = os.path.join(dir, f"{'ticks' if dur == 0 else 'klines_' + str(dur)}_old.csv")
        file_name_new = os.path.join(dir, f"{'ticks' if dur == 0 else 'klines_' + str(dur)}_new.csv")
        res = diff_two_csv(file_name_old, file_name_new, TICKS_COLS if dur == 0 else KLINES_COLS)
        if res:
            diff_result[dur] = res
    return diff_result


def record_diff(result_dir, symbol, result):
    for dur in result:
        file = open(os.path.join(result_dir, f"{result[dur]['type']}/{symbol}-{dur}.log"), mode="w")
        file.write(result[dur]["error"])
        file.close()


def diff_symbols(dir, result_dir, symbols):
    for s in symbols:
        diff_result = diff_symbol(os.path.join(dir, s))
        record_diff(result_dir, s, diff_result)


def process_input(args):
    ex, symbols = args
    dir = "/Volumes/share/mayanqiong/klines_expired/"
    result_dir = f"/Volumes/share/mayanqiong/klines_diff_results/{ex}"
    os.makedirs(result_dir, exist_ok=True)
    os.makedirs(os.path.join(result_dir, "timeout"), exist_ok=True)
    os.makedirs(os.path.join(result_dir, "err_size"), exist_ok=True)
    os.makedirs(os.path.join(result_dir, "err_id"), exist_ok=True)
    os.makedirs(os.path.join(result_dir, "err_value"), exist_ok=True)
    diff_symbols(dir, result_dir, symbols)


if __name__ == "__main__":
    rsp = requests.get(url="https://openmd.shinnytech.com/t/md/symbols/latest.json", timeout=30)
    symbols_group = {ex: [k for k, v in rsp.json().items() if v["exchange_id"] == ex and v["class"] != "FUTURE_COMBINE"] for ex in EXCHANGE_LIST}

    # 将 symbol 分组，group_size 个一组
    group_size = 50
    inputs = []
    for ex, symbols in symbols_group.items():
        inputs.extend([(ex, symbols[i: i+group_size]) for i in range(0, len(symbols), group_size)])

    # 分好组的参数
    pool = multiprocessing.Pool(processes=32)
    pool_outputs = pool.map(process_input, inputs)
    pool.close()
    pool.join()
