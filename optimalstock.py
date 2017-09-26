start_sum = 1000
start_date = '2017-01-01'
end_date = '2017-01-31'

stocks = [
    #    "ABB.ST",
    "SAND.ST", "AXFO.ST"]

if True:

    import locale
    locale.setlocale( locale.LC_ALL, 'Swedish' ) 

    import csv
    hist_data = {}
    import os
    data_files = os.listdir(".")
#    print(data_files)
    cvs_data_files = [x for x in data_files if x.endswith(".csv")]

    stocks = set(["SAND", "ATCO_B"])
    for data_file in cvs_data_files:
        stock = data_file.partition("-")[0]
        if stock not in stocks:
            print("Ignoring %s" % stock)
#         for stock, data_file in (
#            ("ATCO B", "ATCO_B-2016-09-26-2017-09-26.csv"),
#            ("SAND", "SAND-1990-08-25-2017-09-25.csv")
#            ):
        with open(data_file) as csvfile:
            data = {} # Date -> (open, close)
            first_line = csvfile.readline()
            assert first_line.rstrip() == "sep=;"
            reader = csv.reader(csvfile, delimiter=';')
            headers = None
            for row in reader:
                if headers is None:
                    headers = row
                    assert headers[0] == "Date"
                    assert headers[3] == "Opening price", headers[2]
                    assert headers[6] == "Closing price", headers[5]
                    continue
                try:
                    if row[3] == "" or row[6] == "":
                        assert headers[10] == "Trades"
#                        assert row[10] == "0", row
                        continue
                    date = row[0]
                    opening_price = locale.atof(row[3])
                    closing_price = locale.atof(row[6])
                except ValueError:
                    print(row)
                    raise
                data[date] = (opening_price, closing_price)

        hist_data[stock] = data

if False:
    import pandas_datareader
    from pandas import Panel, Index, DatetimeIndex

    data_source = "yahoo" # or 'google' # or "yahoo"

    data = pandas_datareader.DataReader(stocks, data_source,
                                        start_date, end_date)
    print(data)
    print(data.ix("Open"))
    print(data.axes)

    print(data.get_value(Index("Open"), DatetimeIndex("2017-01-04"),
                         Index("SAND.ST")))


if False:
    import yahoo_finance
    import math
    hist_data = {}
    for stock in stocks:
        print("Fetch " + stock)
        share = yahoo_finance.Share(stock)
        hist_data[stock] = share.get_historical(start_date, end_date)

money = start_sum
total_courtage = 0
plan = []
import math
import datetime
start_datetime = datetime.date(2017, 1, 1)
if True:
    courtage_level = 0.0025 # 0.25%
    min_courtage = 1
else:
    courtage_level = 0
    min_courtage = 0
for day in (start_datetime + datetime.timedelta(n) for n in range(0, 380)):
    date = day.isoformat()
#    date = "2017-01-%02d" % day
    best_gain_for_day = 0 # money
    best_stock_data = None # Don't buy anything at all
    for stock, stock_data in hist_data.iteritems():
        if not date in stock_data:
            # Sunday or something
            continue
        open_price = stock_data[date][0] # float(stock_data["Open"])
        close_price = stock_data[date][1] # float(stock_data["Adj_Close"])
        if open_price <= close_price and open_price <= money:
            shares = math.floor(money / open_price)
            courtage = max(min_courtage,
                           math.ceil(shares * (open_price + close_price) * courtage_level))
#            print("yay: %d" % shares)
            gain = shares * (close_price - open_price) - courtage
            if gain > best_gain_for_day:
                best_gain_for_day = gain
                best_stock_data = (date, shares, stock, courtage, stock_data[date])
    if best_stock_data is not None:
        money += best_gain_for_day
        total_courtage += best_stock_data[3]
        print("%s -> +%g -> %g (total courtage: %g)" % (best_stock_data, best_gain_for_day, money, total_courtage))

if money == start_sum:
    print("Sorry, nothing to do")
    
            
        
