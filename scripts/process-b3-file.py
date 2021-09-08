#!/bin/python3

import csv
import sys
import json
from collections import Counter


ALLOWED_YEARS = ['2020', '2019', '2018', '2017', '2016']

returns_by_ticker = {}
with open(sys.argv[1]) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        day_return = float(row['close']) / float(row['open'])
        date, ticker = row['datetime'], row['ticker']

        year = date.split('-')[0]
        if year not in ALLOWED_YEARS:
            continue

        if ticker not in returns_by_ticker:
            returns_by_ticker[ticker] = {year: []}
        elif year not in returns_by_ticker[ticker]:
            returns_by_ticker[ticker][year] = []

        returns_by_ticker[ticker][year].append(round(day_return, 4))

ticker_list = list(returns_by_ticker.keys())
year_list = set(sum([list(data.keys()) for data in list(returns_by_ticker.values())], []))

rv = {
    "dailyReturnsByStock": returns_by_ticker,
    "availableStocks": ticker_list,
    "availableYears": list(year_list)
}

print(json.dumps(rv, separators=(',', ':')))
