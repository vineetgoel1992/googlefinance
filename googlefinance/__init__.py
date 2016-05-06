import json
import sys
import demjson
from googlefinance.company_info import CompanyInfo, Executive

try:
    from urllib.request import Request, urlopen
except ImportError:  # python 2
    from urllib2 import Request, urlopen

__author__ = 'Hongtao Cai'

googleFinanceKeyToFullName = {
    u'id'     : u'ID',
    u't'      : u'StockSymbol',
    u'e'      : u'Index',
    u'l'      : u'LastTradePrice',
    u'l_cur'  : u'LastTradeWithCurrency',
    u'ltt'    : u'LastTradeTime',
    u'lt_dts' : u'LastTradeDateTime',
    u'lt'     : u'LastTradeDateTimeLong',
    u'div'    : u'Dividend',
    u'yld'    : u'Yield',
    u's'      : u'LastTradeSize',
    u'c'      : u'Change',
    u'c'      : u'ChangePercent',
    u'el'     : u'ExtHrsLastTradePrice',
    u'el_cur' : u'ExtHrsLastTradeWithCurrency',
    u'elt'    : u'ExtHrsLastTradeDateTimeLong',
    u'ec'     : u'ExtHrsChange',
    u'ecp'    : u'ExtHrsChangePercent',
    u'pcls_fix': u'PreviousClosePrice'
}

def buildUrl(symbols):
    symbol_list = ','.join([symbol for symbol in symbols])
    # a deprecated but still active & correct api
    return 'http://finance.google.com/finance/info?client=ig&q=' \
        + symbol_list

def buildNewsUrl(symbol, qs='&start=0&num=1000'):
   return 'http://www.google.com/finance/company_news?output=json&q=' \
        + symbol + qs

def buildStockPageUrl(symbol):
    return 'http://www.google.com/finance?output=json&q=' \
        + symbol

def request(symbols):
    url = buildUrl(symbols)
    req = Request(url)
    resp = urlopen(req)
    # remove special symbols such as the pound symbol
    content = resp.read().decode('ascii', 'ignore').strip()
    content = content[3:]
    return content

def requestNews(symbol):
    url = buildNewsUrl(symbol)
    req = Request(url)
    resp = urlopen(req)
    content = resp.read()

    content_json = demjson.decode(content)

    #print "total news: ", content_json['total_number_of_news']

    article_json = []
    news_json = content_json['clusters']
    for cluster in news_json:
        for article in cluster:
            if article == 'a':
                article_json.extend(cluster[article])

    return article_json


def request_company_info(symbol):
    url = buildStockPageUrl(symbol)
    req = Request(url)
    resp = urlopen(req)
    content = resp.read()

    # Check json request for this
    garbage_prefix_length = 4
    content_json = demjson.decode(content[garbage_prefix_length:].strip())[0]

    name = content_json['name']
    summary = content_json['summary'][0]
    url = summary['url']
    overview = summary['overview']
    management_json = content_json['management']
    management = []
    for exec_json in management_json:
        executive = Executive(
            name=exec_json['name'],
            title=exec_json['title']
        )
        management.append(executive)

    return CompanyInfo(
        name=name,
        website=url,
        overview=overview,
        management=management
    )


def replaceKeys(quotes):
    global googleFinanceKeyToFullName
    quotesWithReadableKey = []
    for q in quotes:
        qReadableKey = {}
        for k in googleFinanceKeyToFullName:
            if k in q:
                qReadableKey[googleFinanceKeyToFullName[k]] = q[k]
        quotesWithReadableKey.append(qReadableKey)
    return quotesWithReadableKey

def getQuotes(symbols):
    '''
    get real-time quotes (index, last trade price, last trade time, etc) for stocks, using google api: http://finance.google.com/finance/info?client=ig&q=symbols

    Unlike python package 'yahoo-finance' (15 min delay), There is no delay for NYSE and NASDAQ stocks in 'googlefinance' package.

    example:
    quotes = getQuotes('AAPL')
    return:
    [{u'Index': u'NASDAQ', u'LastTradeWithCurrency': u'129.09', u'LastTradeDateTime': u'2015-03-02T16:04:29Z', u'LastTradePrice': u'129.09', u'Yield': u'1.46', u'LastTradeTime': u'4:04PM EST', u'LastTradeDateTimeLong': u'Mar 2, 4:04PM EST', u'Dividend': u'0.47', u'StockSymbol': u'AAPL', u'ID': u'22144'}]

    quotes = getQuotes(['AAPL', 'GOOG'])
    return:
    [{u'Index': u'NASDAQ', u'LastTradeWithCurrency': u'129.09', u'LastTradeDateTime': u'2015-03-02T16:04:29Z', u'LastTradePrice': u'129.09', u'Yield': u'1.46', u'LastTradeTime': u'4:04PM EST', u'LastTradeDateTimeLong': u'Mar 2, 4:04PM EST', u'Dividend': u'0.47', u'StockSymbol': u'AAPL', u'ID': u'22144'}, {u'Index': u'NASDAQ', u'LastTradeWithCurrency': u'571.34', u'LastTradeDateTime': u'2015-03-02T16:04:29Z', u'LastTradePrice': u'571.34', u'Yield': u'', u'LastTradeTime': u'4:04PM EST', u'LastTradeDateTimeLong': u'Mar 2, 4:04PM EST', u'Dividend': u'', u'StockSymbol': u'GOOG', u'ID': u'304466804484872'}]

    :param symbols: a single symbol or a list of stock symbols
    :return: real-time quotes list
    '''
    if type(symbols) == type('str'):
        symbols = [symbols]
    content = json.loads(request(symbols))
    return replaceKeys(content);

def getNews(symbol):
    return requestNews(symbol);


def getCompanyInfo(symbol):
    return request_company_info(symbol)


if __name__ == '__main__':
    try:
        symbols = sys.argv[1]
    except:
        symbols = "GOOG,AAPL"

    symbols = symbols.split(',')

    print(json.dumps(getNews("GOOG"), indent=2))
    print(json.dumps(getQuotes(symbols), indent=2))
    print getCompanyInfo("GOOG")
