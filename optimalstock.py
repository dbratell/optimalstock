import csv
import locale
import os
import re

def parse_data():
    # To get locale.atof to do the right thing
    locale.setlocale( locale.LC_ALL, 'Swedish' ) 

    hist_data = {}
    data_files = os.listdir(".")
    csv_data_files = [x for x in data_files if x.endswith(".csv")]

    for data_file in csv_data_files:
        match = re.match(r"((?:[A-Z][A-Z0-9]*[-_]?)+)-[1-2]", data_file)
        assert match, data_file
        stock = match.group(1)
        if False and stock not in stocks:
            print("Ignoring %s" % stock)
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
                    assert headers[3] == "Opening price", headers[3]
                    assert headers[6] == "Closing price", headers[6]
                    assert headers[8] == "Total volume", headers[8]
                    assert headers[10] == "Trades", headers[10]
                    continue
                try:
                    if row[3] == "" or row[6] == "" or row[8] == "":
#                        assert row[10] == "0", row
                        continue
                    date = row[0]
                    opening_price = locale.atof(row[3])
                    closing_price = locale.atof(row[6])
                    volume = locale.atof(row[8]) # Can be non-integer because of splits
                except ValueError:
                    print(data_file)
                    print(row)
                    raise
                data[date] = (opening_price, closing_price, volume)

        hist_data[stock] = data
    return hist_data

def run_simulation(start_sum, courtage, min_courtage, hist_data, max_volume_share=0.001, reverse=False,
                   verbose=False):
    money = start_sum
    total_courtage = 0
    plan = []
    import math
    import datetime
    start_datetime = datetime.date(2017, 1, 1)
    for day in (start_datetime + datetime.timedelta(n) for n in range(0, 380)):
        date = day.isoformat()
        best_gain_for_day = 0 # money
        best_stock_data = None # Don't buy anything at all
        had_options = False
        for stock, stock_data in hist_data.iteritems():
            if not date in stock_data:
                # Sunday or something
                continue
            had_options = True
            open_price = stock_data[date][0] # float(stock_data["Open"])
            close_price = stock_data[date][1] # float(stock_data["Adj_Close"])
            if (not reverse and open_price <= close_price or
                reverse and open_price >= close_price):
                shares = int(math.floor(max(money, 0) / open_price))
                volume = stock_data[date][2]
                if shares > volume * max_volume_share:
                    # Never do more than 1% of the trade in the stock.
                    shares = int(math.floor(volume * max_volume_share))
                if shares == 0:
                    continue
                courtage = (max(min_courtage, math.ceil(shares * open_price * courtage_level)) +
                            max(min_courtage, math.ceil(shares * close_price * courtage_level)))
                gain = shares * (close_price - open_price) - courtage
                if reverse:
                    if gain < best_gain_for_day:
                        best_gain_for_day = gain
                        best_stock_data = (date, shares, stock, courtage, stock_data[date])
                else:
                    if gain > best_gain_for_day:
                        best_gain_for_day = gain
                        best_stock_data = (date, shares, stock, courtage, stock_data[date])
        if best_stock_data is not None:
            money += best_gain_for_day
            total_courtage += best_stock_data[3]
            if verbose:
                sign_str = "+"
                if reverse:
                    sign_str = "" # Minus already in the number
                print("%s: Buy and sell %d %s -> %s%.2f -> %.2f (total courtage: %d)" % (
                    date,
                    best_stock_data[1],
                    best_stock_data[2],
                    sign_str,
                    best_gain_for_day,
                    money,
                    total_courtage))
        elif had_options:
            if verbose:
                print("%s: No stocks worth trading. Still %.2f (total courtage: %d)" % (
                    date,
                    money,
                    total_courtage))

    if money == start_sum:
        if verbose:
            print("Sorry, nothing to do")

    return money

if False:
    # Fast
    courtage_level = 0.0 # 0.15%
    min_courtage = 99
elif False:
    # Medium
    courtage_level = 0.0015 # 0.15%
    min_courtage = 39
elif True:
    # Small
    courtage_level = 0.0025 # 0.25%
    min_courtage = 1
else:
    # Start
    courtage_level = 0
    min_courtage = 0

start_money = 100000

hist_data = parse_data()
courtage_options = ((0, 99),
                    (0.0015, 39),
                    (0.0025, 1))

best_money = 0
best_courtage_level = 1
best_min_courtage = 99999
reverse = True
if reverse:
    best_money = start_money
else:
    best_money = 0

for courtage_level, min_courtage in courtage_options:
    end_money = run_simulation(start_money, courtage_level, min_courtage, hist_data,
                               reverse=reverse, verbose=False)
    if (not reverse and end_money > best_money or
        reverse and end_money < best_money):
        best_money = end_money
        best_courtage_level = courtage_level
        best_min_courtage = min_courtage

end_money = run_simulation(start_money, best_courtage_level, best_min_courtage, hist_data,
                           reverse=reverse, verbose=True)
print("With courtage level=%.2f%% and min courtage=%d we end up with %.0f" % (
    best_courtage_level * 100.0, best_min_courtage, end_money))
    
            
        
