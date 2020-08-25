#!/usr/bin/env python
#  -*- coding: utf-8 -*-

"""
比较 ticks 信息的差别
"""
import multiprocessing
import os
from datetime import datetime

import numpy as np
import pandas
import requests
from tqsdk.utils import _generate_uuid

EXCHANGE_LIST = ["SHFE", "CFFEX", "INE", "DCE", "CZCE", "KQ", "SSWE"]

KLINES_COLS = ["open", "high", "low", "close", "volume", "open_oi", "close_oi"]

TICKS_COLS = ["last_price", "highest", "lowest", "bid_price1", "bid_volume1", "ask_price1", "ask_volume1", "volume",
         "amount", "open_interest"]


# ROOT_DIR = "/Volumes/share/mayanqiong/"
ROOT_DIR = "S:/mayanqiong"


def get_df_diff(df_old, df_new, cols):
    arr_diff = np.array([True for _ in range(df_old.shape[0])])
    for col in cols:
        arr_old = df_old[col].values
        arr_new = df_new[col].values
        if arr_new.dtype == "float64":
            np.round(arr_new, 3, arr_new)
        arr_diff = arr_diff & ((arr_old == arr_new) | (np.isnan(arr_old) & np.isnan(arr_new)))
    if not np.all(arr_diff):
        np.logical_not(arr_diff, arr_diff)
        df_diff_old = df_old.loc[arr_diff]
        df_diff_new = df_new.loc[arr_diff]
        if not df_diff_old.empty:
            return f"{np.count(arr_diff)} lines different\n\n{df_tostring(df_diff_old)}\n\n{df_tostring(df_diff_new)}"
    return None


def df_tostring(df, show_all=True):
    if df.shape[0] == 0:
        return "Empty"
    show_all = True if df.shape[0] < 20 or show_all else False
    if show_all:
        return df.to_string(index=False)
    else:
        return df[:5].to_string(index=False) + "\n........\n" + df[-5:].to_string(index=False)


def handle_err_id(df_old, df_new):
    """
    处理 df_old 将 datetime 为 .9995ddddd 的行，比较数值，一样的数值，删去 下一行
    此时 df_old 减小到 n 行，与 df_new 最后 n 行比较，矩阵是否相同
    """
    pass


def diff_two_csv(file_old, file_new, cols):
    """
    三种不同类型的错误
    timeout 有合约下载超时
    err_size 个数不同
    err_id 两边id值不同
    err_value 两边数值不同
    """
    try:
        df_old = pandas.read_csv(file_old)
        df_new = pandas.read_csv(file_new)
    except Exception as e:
        print("===================")
        print(file_old)
        print(file_new)
        print(e)
        return None
    result = None
    if df_old.shape[0] == 0 and df_new.shape[0] == 0:
        result = {
            "type": "timeout_all",
            "error": f"df_old: {repr(df_old.shape)}\ndf_new: {repr(df_new.shape)}"
        }
    elif df_old.shape[0] == 0 or df_new.shape[0] == 0:
        result = {
            "type": "timeout_" + ("old" if df_old.shape[0] == 0 else "new"),
            "error": f"df_old: {repr(df_old.shape)}\ndf_new: {repr(df_new.shape)}"\
                     f"\n{'*' * 50}\n{df_tostring(df_old, show_all=False)}\n{'*' * 50}\n{df_tostring(df_new, show_all=False)}"
        }
    elif df_old.shape != df_new.shape:
        result = {
            "type": "err_size",
            "error": f"df_old: {repr(df_old.shape)}\ndf_new: {repr(df_new.shape)}"\
                     f"\n{'*' * 50}\n{df_tostring(df_old, show_all=False)}\n{'*' * 50}\n{df_tostring(df_new, show_all=False)}"
        }
    elif df_old.iloc[0]["id"] != df_new.iloc[0]["id"] or df_old.iloc[-1]["id"] != df_new.iloc[-1]["id"]:
        if df_old.iloc[-1]["id"] > df_new.iloc[-1]["id"]:

            result = {
                "type": "err_id_old_greater",
                "error": f"df_old: {df_old.iloc[0]['id']} ~ {df_old.iloc[-1]['id']}\ndf_new: {df_new.iloc[0]['id']} ~ {df_new.iloc[-1]['id']}" \
                         f"\n{'*' * 50}\n{df_tostring(df_old, show_all=False)}\n{'*' * 50}\n{df_tostring(df_new, show_all=False)}"
            }
        else:
            result = {
                "type": "err_id_new_greater",
                "error": f"df_old: {df_old.iloc[0]['id']} ~ {df_old.iloc[-1]['id']}\ndf_new: {df_new.iloc[0]['id']} ~ {df_new.iloc[-1]['id']}" \
                         f"\n{'*' * 50}\n{df_tostring(df_old, show_all=False)}\n{'*' * 50}\n{df_tostring(df_new, show_all=False)}"
            }
    if result:
        return result
    r = get_df_diff(df_old, df_new, cols)
    if r:
        return {
            "type": "err_value",
            "error": r
        }
    return None


def diff_symbol(dir, symbol, same_files, writing_same_queue):
    diff_result = {}
    for dur in [0, 1, 5, 15, 30, 60, 60 * 5, 60 * 15, 60 * 30, 60 * 60, 60 * 60 * 2, 60 * 60 * 4, 60 * 60 * 24,
                60 * 60 * 24 * 7]:
        file_name_old = os.path.join(dir, f"{'ticks' if dur == 0 else 'klines_' + str(dur)}_old.csv")
        file_name_new = os.path.join(dir, f"{'ticks' if dur == 0 else 'klines_' + str(dur)}_new.csv")
        if f"{symbol}-{dur}" in same_files:
            continue
        if os.path.exists(file_name_old) and os.path.exists(file_name_new):
            res = diff_two_csv(file_name_old, file_name_new, TICKS_COLS if dur == 0 else KLINES_COLS)
            if res:
                diff_result[dur] = res
            else:
                writing_same_queue.put(f"{symbol}-{dur}")
        else:
            print(f"no file {file_name_old} or {file_name_new}")
    return diff_result


def record_diff(result_dir, symbol, result):
    for dur in result:
        if result[dur]['type'] == "err_value":
            os.makedirs(os.path.join(result_dir, result[dur]['type']), exist_ok=True)
            file = open(os.path.join(result_dir, f"{result[dur]['type']}/{symbol}-{dur}.log"), mode="w")
            file.write(result[dur]["error"])
            file.close()


def diff_symbols(dir, result_dir, symbols, same_files, writing_same_queue):
    for s in symbols:
        diff_result = diff_symbol(os.path.join(dir, s), s, same_files, writing_same_queue)
        record_diff(result_dir, s, diff_result)


def process_input(args):
    ex, symbols, result_dir, same_files, writing_same_queue = args
    data_dir = os.path.join(ROOT_DIR, "klines_expired")
    diff_symbols(data_dir, os.path.join(result_dir, ex), symbols, same_files, writing_same_queue)


def writing_proc(writing_queue, file_name):
    file_handle = open(file_name, mode="a")
    while True:
        s = writing_queue.get()
        if s == 0:
            file_handle.close()
            break
        file_handle.write(s + '\n')


if __name__ == "__main__":
    print(datetime.now())
    rsp = requests.get(url="https://openmd.shinnytech.com/t/md/symbols/2020-08-21.json", timeout=30)
    all_symbols = rsp.json()
    symbols_group = {ex: [k for k, v in all_symbols.items() if v["exchange_id"] == ex and v["class"] != "FUTURE_COMBINE"] for ex in EXCHANGE_LIST}

    # symbols_group = {"SHFE": ["SHFE.au2012", "SHFE.au1612"], "CFFEX": ["CFFEX.IC1606"]}

    # 已经完全相等的文件
    result_dir = os.path.join(os.path.join(ROOT_DIR, "klines_results"))
    os.makedirs(result_dir, exist_ok=True)

    same_file_name = os.path.join(result_dir, "same_file.log")
    if os.path.exists(same_file_name):
        same_file = open(os.path.join(result_dir, "same_file.log"), mode="r")
        same_files = [s.strip() for s in same_file.readlines()]
        same_file.close()
    else:
        same_files = []

    # 已经处理的文件也 append 到这里
    for ex in EXCHANGE_LIST:
        if not os.path.exists(os.path.join(result_dir, ex)):
            continue
        for err_type in ["timeout_all", "timeout_new", "timeout_old", "err_size", "err_id", "err_value"]:
            if os.path.exists(os.path.join(result_dir, ex, err_type)):
                file_list = os.listdir(os.path.join(result_dir, ex, err_type))
                same_files.extend([f[0:f.index('.log')] for f in file_list])

    print(len(same_files))

    # 一个进程专门记录已经处理过的完全一样的 合约 周期
    m = multiprocessing.Manager()
    writing_same_queue = m.Queue()
    same_file_proc = multiprocessing.Process(target=writing_proc, args=(writing_same_queue, same_file_name))
    same_file_proc.start()

    # 将 symbol 分组，group_size 个一组
    group_size = 50
    inputs = []
    for ex, symbols in symbols_group.items():
        inputs.extend([(ex, symbols[i: i+group_size], result_dir, same_files, writing_same_queue) for i in range(0, len(symbols), group_size)])

    # 分好组的参数
    pool = multiprocessing.Pool(processes=30)
    pool_outputs = pool.map(process_input, inputs)
    pool.close()
    pool.join()

    writing_same_queue.put(0)
    same_file_proc.join()
    print(datetime.now())
