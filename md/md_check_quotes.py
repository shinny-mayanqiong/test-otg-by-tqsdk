

import csv

import requests


if __name__ == "__main__":
    # rsp = requests.get(url="https://openmd.shinnytech.com/t/md/symbols/latest.json", timeout=30)
    # symbols = [v["underlying_symbol"] for v in rsp.json().values() if v["class"] == "FUTURE_CONT"]
    # symbols.extend([k for k, v in rsp.json().items() if v["class"] == "FUTURE_CONT"])

    symbols = ['CFFEX.IF2009', 'CFFEX.IH2009', 'CFFEX.IC2009', 'CFFEX.TF2012', 'CFFEX.T2012', 'SHFE.cu2010', 'SHFE.au2012',
     'SHFE.ag2012', 'SHFE.zn2009', 'SHFE.al2009', 'SHFE.ru2101', 'SHFE.rb2010', 'SHFE.fu2101', 'SHFE.hc2010',
     'SHFE.bu2012', 'SHFE.pb2010', 'SHFE.ni2010', 'SHFE.sn2010', 'SHFE.wr2010', 'INE.sc2010', 'DCE.a2101', 'DCE.b2010',
     'DCE.bb2009', 'DCE.c2101', 'DCE.cs2009', 'DCE.fb2009', 'DCE.i2101', 'DCE.j2101', 'DCE.jd2010', 'DCE.jm2009',
     'DCE.l2101', 'DCE.m2101', 'DCE.p2101', 'DCE.pp2101', 'DCE.v2101', 'DCE.y2101', 'CZCE.WH009', 'CZCE.PM105',
     'CZCE.CF101', 'CZCE.CY101', 'CZCE.SR101', 'CZCE.TA101', 'CZCE.OI101', 'CZCE.RI009', 'CZCE.MA101', 'CZCE.FG101',
     'CZCE.RS009', 'CZCE.RM101', 'CZCE.ZC011', 'CZCE.JR009', 'CZCE.LR011', 'CZCE.SF010', 'CZCE.SM009', 'CZCE.AP010',
     'CFFEX.TS2012', 'SHFE.sp2012', 'DCE.eg2101', 'CZCE.CJ101', 'INE.nr2010', 'DCE.rr2010', 'CZCE.UR101', 'SHFE.ss2010',
     'DCE.eb2009', 'CZCE.SA101', 'DCE.pg2011', 'INE.lu2101', 'KQ.m@CFFEX.IF', 'KQ.m@CFFEX.IH', 'KQ.m@CFFEX.IC',
     'KQ.m@CFFEX.TF', 'KQ.m@CFFEX.T', 'KQ.m@SHFE.cu', 'KQ.m@SHFE.au', 'KQ.m@SHFE.ag', 'KQ.m@SHFE.zn', 'KQ.m@SHFE.al',
     'KQ.m@SHFE.ru', 'KQ.m@SHFE.rb', 'KQ.m@SHFE.fu', 'KQ.m@SHFE.hc', 'KQ.m@SHFE.bu', 'KQ.m@SHFE.pb', 'KQ.m@SHFE.ni',
     'KQ.m@SHFE.sn', 'KQ.m@SHFE.wr', 'KQ.m@INE.sc', 'KQ.m@DCE.a', 'KQ.m@DCE.b', 'KQ.m@DCE.bb', 'KQ.m@DCE.c',
     'KQ.m@DCE.cs', 'KQ.m@DCE.fb', 'KQ.m@DCE.i', 'KQ.m@DCE.j', 'KQ.m@DCE.jd', 'KQ.m@DCE.jm', 'KQ.m@DCE.l', 'KQ.m@DCE.m',
     'KQ.m@DCE.p', 'KQ.m@DCE.pp', 'KQ.m@DCE.v', 'KQ.m@DCE.y', 'KQ.m@CZCE.WH', 'KQ.m@CZCE.PM', 'KQ.m@CZCE.CF',
     'KQ.m@CZCE.CY', 'KQ.m@CZCE.SR', 'KQ.m@CZCE.TA', 'KQ.m@CZCE.OI', 'KQ.m@CZCE.RI', 'KQ.m@CZCE.MA', 'KQ.m@CZCE.FG',
     'KQ.m@CZCE.RS', 'KQ.m@CZCE.RM', 'KQ.m@CZCE.ZC', 'KQ.m@CZCE.JR', 'KQ.m@CZCE.LR', 'KQ.m@CZCE.SF', 'KQ.m@CZCE.SM',
     'KQ.m@CZCE.AP', 'KQ.m@CFFEX.TS', 'KQ.m@SHFE.sp', 'KQ.m@DCE.eg', 'KQ.m@CZCE.CJ', 'KQ.m@INE.nr', 'KQ.m@DCE.rr',
     'KQ.m@CZCE.UR', 'KQ.m@SHFE.ss', 'KQ.m@DCE.eb', 'KQ.m@CZCE.SA', 'KQ.m@DCE.pg', 'KQ.m@INE.lu']
    symbols = [s for s in symbols if s.startswith("KQ.m@")]
    delta_list = []
    for s in symbols:
        print(f"start {s} {'='*20}")
        old_csvfile = open(f'quotes2/trading_quote_{s}_old.csv', newline='')
        old_csv_reader = csv.DictReader(old_csvfile)
        new_csvfile = open(f'quotes2/trading_quote_{s}_new.csv', newline='')
        new_csv_reader = csv.DictReader(new_csvfile)
        try:
            old_quote = next(old_csv_reader)
            new_quote = next(new_csv_reader)
        except:
            print(f"{s} 没有收到数据")
            continue
        if old_quote['datetime'] == new_quote['datetime']:
            pass
        elif old_quote['datetime'] > new_quote['datetime']:
            while True:
                new_quote = next(new_csv_reader)
                print(new_quote['datetime'])
                if old_quote['datetime'] == new_quote['datetime']:
                    break
        else:
            while True:
                old_quote = next(old_csv_reader)
                if old_quote['datetime'] == new_quote['datetime']:
                    break
        # 得到了开始的地方
        from_dt = old_quote['datetime']
        quotes_count = 0
        try:
            while True:
                old_quote = next(old_csv_reader)
                new_quote = next(new_csv_reader)
                if old_quote['datetime'] != new_quote['datetime']:
                    print(f"{s} ***** 遇到对不齐时间的行情", old_quote['datetime'], new_quote['datetime'])
                    while True:
                        if old_quote['datetime'] > new_quote['datetime']:
                            print(f"{s} 旧合约服务器跳过行情时间 {new_quote['datetime']}")
                            new_quote = next(new_csv_reader)
                        else:
                            print(f"{s} 新合约服务器跳过行情时间 {old_quote['datetime']}")
                            old_quote = next(old_csv_reader)
                        if old_quote['datetime'] == new_quote['datetime']:
                            print(f"{s} ***** 时间重新对齐", old_quote['datetime'], new_quote['datetime'])
                            break

                quotes_count += 1
                # local_nano_time, quote_nano_time, datetime, last_price, highest, lowest, open, close, average, volume, amount, open_interest, ask_price1, ask_volume1, bid_price1, bid_volume1, ask_price2, ask_volume2, bid_price2, bid_volume2, ask_price3, ask_volume3, bid_price3, bid_volume3, ask_price4, ask_volume4, bid_price4, bid_volume4, ask_price5, ask_volume5, bid_price5, bid_volume5
                delta_t = (int(old_quote['local_nano_time']) - int(new_quote['local_nano_time'])) / 1e6
                delta_list.append(abs(delta_t))
                if delta_t == 0:
                    print(f" {s} {old_quote['datetime']} delta_t == 0")
                if abs(delta_t) > 300:
                    print(f" {s} {old_quote['datetime']} delta_t > 300")
                for k in old_quote:
                    if k == 'local_nano_time':
                        continue
                    if old_quote[k] != new_quote[k]:
                        if k in ["average"]:
                            continue
                        print(f"{s} -> {k} 数据不同", old_quote[k], new_quote[k])
        except:
            pass
        to_dt = old_quote['datetime']
        print(f"{s} from: {from_dt} to: {to_dt} quotes_count: {quotes_count}")

    import numpy as np
    arr = np.array(delta_list)
    print(f"均值 - {np.mean(arr):.4} \n"
          f"中位数 - {np.median(arr):.4} \n"
          f"1/4 - {np.percentile(arr, 25):.4} \n"
          f"3/4 - {np.percentile(arr, 75):.4} \n"
          f"9/10 - {np.percentile(arr, 90):.4} \n"
          f"95/100 - {np.percentile(arr, 95):.4} \n"
          f"99/100 - {np.percentile(arr, 99):.4} \n"
          f"最小值 {arr.min():.4} \n"
          f"最大值 {arr.max():.4} \n"
          f"差值大于300占比 {sum(arr > 300)}/{arr.size} = {sum(arr > 300) / arr.size * 100 :.4}%")
