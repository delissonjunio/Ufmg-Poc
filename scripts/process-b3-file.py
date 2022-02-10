#!/bin/python3

import csv
import datetime
import sys
from collections import defaultdict
from typing import Dict

ALLOWED_YEARS = [2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012]

output_writer = csv.writer(sys.stdout)
stock_price_by_date: Dict[datetime.datetime, Dict[str, str]] = defaultdict(dict)
tickers = set()
with open(sys.argv[1]) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        ticker = row['ticker'].replace(' ', '')
        date = datetime.datetime.strptime(row['datetime'], '%Y-%m-%d')

        if date.year not in ALLOWED_YEARS:
            continue

        tickers.add(ticker)
        stock_price_by_date[date][ticker] = row['close']

tickers = list(tickers)
output_writer.writerow(['date'] + tickers)
for date, prices in sorted(stock_price_by_date.items(), key=lambda item: item[0]):
    output_writer.writerow([date.strftime("%Y-%m-%d")] + [prices.get(ticker, '') for ticker in tickers])

