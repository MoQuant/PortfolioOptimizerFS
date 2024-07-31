def address(ticker):
    url = 'https://financialmodelingprep.com/'
    endpoint = 'api/v3/historical-price-full/{}?apikey={}'
    key = ''
    return url + endpoint.format(ticker, key)

import asyncio
import websockets
import json
import requests
import numpy as np
import pandas as pd
from scipy.optimize import minimize

def Beta(x, y):
    coef = np.cov(x, y)
    beat = coef[0][1]
    box = coef[0][0]
    return float(beat / box)

def Capital_Asset_Pricing_Model(rf, rm, beta):
    return float(rf + beta*(rm - rf))

def MinimizeRisk(beta, capm, target_return):
    beta, capm = np.array(beta), np.array(capm)
    def objective(W):
        return W @ beta
    def constraint(W):
        return W @ capm - target_return
    def constraint2(W):
        return W @ np.ones(len(W)) - 1
    def constraint3(W):
        return W
    W = np.ones(len(beta))
    cons = [{'type':'ineq','fun':constraint},
            {'type':'eq','fun':constraint2},
            {'type':'ineq','fun':constraint3}]
    res = minimize(objective, W, method='SLSQP', bounds=None, constraints=cons)
    return res.x

def MaximizeReturn(beta, capm, target_beta):
    beta, capm = np.array(beta), np.array(capm)
    def objective(W):
        return -(W @ capm)
    def constraint(W):
        return -(W @ beta - target_beta)
    def constraint2(W):
        return W @ np.ones(len(W)) - 1
    def constraint3(W):
        return W
    W = np.ones(len(beta))
    cons = [{'type':'ineq','fun':constraint},
            {'type':'eq','fun':constraint2},
            {'type':'ineq','fun':constraint3}]
    res = minimize(objective, W, method='SLSQP', bounds=None, constraints=cons)
    return res.x


class Server:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.session = requests.Session()
    def start_server(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(websockets.serve(self.server, self.host, self.port))
        loop.run_forever()
    async def server(self, ws, path):
        print("Client Connected")
        while True:
            resp = await ws.recv()
            resp = json.loads(resp)

            tickers = resp['tickers'].split(',')
            rf = float(resp['riskfree'])
            target_beta = float(resp['beta'])
            target_return = float(resp['return'])
            balance = float(resp['balance'])

            sp500, close, prices = self.GatherData(tickers)
            
            rate_of_return = close[1:]/close[:-1] - 1.0
            market_rate = sp500[-1]/sp500[0] - 1.0
            spROR = sp500[1:]/sp500[:-1] - 1.0

            BETA, CAPM = [], []
            rorT = rate_of_return.T
            
            for x in rorT:
                beta = Beta(spROR, x)
                capm = Capital_Asset_Pricing_Model(rf, market_rate, beta)
                BETA.append(beta)
                CAPM.append(capm)

            minrisk = MinimizeRisk(BETA, CAPM, target_return).tolist()
            maxretn = MaximizeReturn(BETA, CAPM, target_beta).tolist()
            minshares = []
            maxshares = []
            for i, j, p in zip(minrisk, maxretn, prices):
                weightLow = int((balance*i)/p)
                weightHigh = int((balance*j)/p)
                minshares.append(weightLow)
                maxshares.append(weightHigh)

            table = [['Ticker','Price','Beta','E[R]','MinShares','MaxShares']]
            for t, p, bt, ct, mish, mxsh in zip(tickers, prices, BETA, CAPM, minshares, maxshares):
                table.append([t, p, round(bt,3), round(ct,4), mish, mxsh])
            
            message = {
                'tickers': tickers,
                'table': table,
                'minrisk': minrisk,
                'maxretn': maxretn
            }

            await ws.send(json.dumps(message))

    def GatherData(self, tickers):
        sp500 = self.session.get(address('SPY')).json()
        sp500 = pd.DataFrame(sp500['historical'])['adjClose'].values.tolist()[::-1]
        close = []
        prices = []
        for tick in tickers:
            value = self.session.get(address(tick)).json()
            value = pd.DataFrame(value['historical'])['adjClose'].values.tolist()[::-1]
            close.append(value)
            prices.append(value[-1])
        return np.array(sp500), np.array(close).T, prices



print("Server Booted")
Server().start_server()
