import logging

bid, user_id, pwd, td_url = ("N南华期货_ETF", "90084321", "888888", "ws://101.230.216.138:37480/trade")

sh = logging.StreamHandler()
sh.setFormatter(logging.Formatter('%(asctime)s - OTGTEST - %(levelname)s - %(message)s'))
test_logger = logging.getLogger("OTGTest")
test_logger.addHandler(sh)
