### Stocks
### Sean Welleck | 2014
#
# A module for retrieving stock information using the
# yahoo finance API (https://code.google.com/p/yahoo-finance-managed/wiki/CSVAPI)

import csv
import urllib.request, urllib.error, urllib.parse
from collections import defaultdict
import numpy
from statsmodels.stats.correlation_tools import cov_nearest

# Retrieves the stock quote for the given symbol
# from Yahoo Finance as a float.
# Input:  symbol - stock symbol as a string
# Output: price  - latest trade price from yahoo finance
def get_stock_quote(symbol):
	BASE_URL = 'http://download.finance.yahoo.com/d/quotes.csv?s='
	ID = symbol
	close_prop = '&f=l1'
	SUFFIX = '&e=.csv'
	url = "%s%s%s%s" % (BASE_URL, ID, close_prop, SUFFIX)
	price = float(urllib.request.urlopen(url).read().strip())
	return price

# Downloads the stock history for the given symbol,
# for the given date range, as a csv file.
# Input: symbol   - stock symbol as a string
#        start    - start date in the form 'mm/dd/yyyy'
#        end      - end date in the form 'mm/dd/yyyy'
#        outfile  - output filename, e.g. 'out.csv'
#        interval - trading interval; either d, w, m (daily, weekly, monthl7)
def csv_quote_history(symbol, start, end, outfile, interval='d'):
	response = _quote_history(symbol, start, end, interval)
	with open(outfile, 'wb') as f:
		csv_reader = csv.reader(response)
		csv_writer = csv.writer(f)
		for row in csv_reader:
			csv_writer.writerow(row)

# Gives the stock history for the given symbol,
# for the given date range, as a dictionary.
# Output: keys: ['High', 'Adj Close', 'Volume', 'Low', 'Date', 'Close', 'Open']
#         values: list
def quote_history_dict(symbol, start, end, interval='m'):
	history = defaultdict(lambda: [])
	response = _quote_history(symbol, start, end, interval)
	dreader = csv.DictReader(response)
	for row in dreader:
		for key in row.keys():
			history[key].insert(0, row[key])
	return history

def _quote_history(symbol, start, end, interval):
	BASE_URL = 'http://ichart.yahoo.com/table.csv?s='
	ID = symbol
	sm, sd, sy = start.split('/')
	em, ed, ey = end.split('/')
	url = "%s%s&a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&g=%s" % (BASE_URL, ID, (int(sm)-1), int(sd), int(sy), (int(em)-1), int(ed), int(ey), interval)
	response = urllib.request.urlopen(url)
	return response

def get_prices(symbol, start, end, interval='m'):
	history = quote_history_dict(symbol, start, end, interval)
	prices = [round(float(x),2) for x in history['Close']]
	prices[0] = round(float(history['Open'][0]),2)
	return prices

def get_returns(symbol, start, end, interval='m'):
	history = quote_history_dict(symbol, start, end, interval)
	prices = [round(float(x),2) for x in history['Close']]
	prices[0] = round(float(history['Open'][0]),2)
	returns = [(x_y[1]/x_y[0])-1 for x_y in zip(prices[0:-1], prices[1:])]
	return returns

def get_yr_returns(symbol, start, end):
	history = quote_history_dict(symbol, start, end, 'm')
	prices = [round(float(x),2) for x in history['Close']]
	prices[0] = round(float(history['Open'][0]),2)
	prices.insert(0, prices[0])
	returns = [(x_y1[1]/x_y1[0])-1 for x_y1 in zip(prices[0::12][:-1], prices[12::12])]
	return returns

def avg_return(symbol, start, end, interval='m'):
	if interval=='y':
		return numpy.mean(get_yr_returns(symbol, start, end))
	else:
		return numpy.mean(get_returns(symbol, start, end, interval))

def cov_matrix(symbols, start, end, interval='m'):
	if interval=='y':
		data = [numpy.array(get_yr_returns(s, start, end)) for s in symbols]
	else:
		data = [numpy.array(get_returns(s, start, end, interval)) for s in symbols]
	x = numpy.array(data)
	return cov_nearest(numpy.cov(x))


### Portfolio Optiimization
### Sean Welleck | 2014
#
# Finds an optimal allocation of stocks in a portfolio,
# satisfying a minimum expected return.
# The problem is posed as a Quadratic Program, and solved
# using the cvxopt library.
# Uses actual past stock data, obtained using the stocks module.

from cvxopt import matrix, solvers
import numpy

# solves the QP, where x is the allocation of the portfolio:
# minimize   x'Px + q'x
# subject to Gx <= h
#            Ax == b
#
# Input:  n       - # of assets
#         avg_ret - nx1 matrix of average returns
#         covs    - nxn matrix of return covariance
#         r_min   - the minimum expected return that you'd
#                   like to achieve
# Output: sol - cvxopt solution object
def optimize_portfolio(n, avg_ret, covs, r_min):
	P = covs
	# x = variable(n)
	q = matrix(numpy.zeros((n, 1)), tc='d')
	# inequality constraints Gx <= h
	# captures the constraints (avg_ret'x >= r_min) and (x >= 0)
	G = matrix(numpy.concatenate((
		-numpy.transpose(numpy.array(avg_ret)), 
		-numpy.identity(n)), 0))
	h = matrix(numpy.concatenate((
		-numpy.ones((1,1))*r_min, 
		numpy.zeros((n,1))), 0))
	# equality constraint Ax = b; captures the constraint sum(x) == 1
	A = matrix(1.0, (1,n))
	b = matrix(1.0)
	sol = solvers.qp(P, q, G, h, A, b)
	return sol

### setup the parameters
symbols = ['GOOG', 'AIMC', 'CE', 'BH', 'AHGP', 'AB', 'HLS', 'BKH', 'LUV']
# pull data from this date range
start   = '1/1/2010'
end     = '1/1/2014'
n       = len(symbols)
# average yearly return for each stock
avg_ret = matrix([avg_return(s, start, end, 'y') for s in symbols])
# covariance of asset returns
covs    = matrix(numpy.array(cov_matrix(symbols, start, end, 'y')))
# minimum expected return threshold
r_min   = 0.10

### solve
solution = optimize_portfolio(n, avg_ret, covs, r_min)
y = solution['x']
print(sum(y))
