import numpy as np
from scipy.optimize import fmin_cobyla
import pandas as pd
import math 

class AutomatedMarketMaker(object):
    def __init__(self, possible_outcomes, vig=0.1, init=1.0, market='RIKIDDO', swap_fee=0):
        """
        Parameters
        ----------
        possible_outcomes   list
                            list of all possible outcomes of the market
                                    
        vig                 float
                            parameter of the `alpha` variable used to calculate the `b` variable.
                            Corresponds to the market "vig" value
                
        init                float
                            The initial subsidies of the market, spread equally in this algorithm on all the outcomes.
        
        market              srt, 'RIKIDDO' | 'CPMM'
                            The market type. If 'CPMM' is selected, then a swap_fee value must be given.
        
        swap_fee            float
                            float value between 0 and 1, corresponding to the CPMM swap fee.
        """
        self.possible_outcomes = possible_outcomes
        self.market = market
        self.swap_fee = swap_fee

        self.init = init
        self.n = len(self.possible_outcomes)
        self._x = [np.ones([self.n])*init/self.n]
        self._book = []
        self.market_value = init
        self._history = []
        self.f = vig/self.n*np.log(self.n)
        
        if (market=='CPMM') & (swap_fee is None):
            raise ValueError("Swap fee can't be none")
        elif (market=='CPMM') & ((swap_fee<0) | (swap_fee>1)):
            raise ValueError('Fee value needs to be in [0,1] interval')
        else:
            pass
    
    def initial_liquidity(self, possible_outcomes, amount):
        for i in range(0, len(possible_outcomes)):
            self._book.append({'name': 'Zeitgeist', 
                                'shares': amount, 
                                'outcome': i, 
                                'paid': amount*(1/len(possible_outcomes)), 
                                'fee_cost': 0,
                                'lp': 1})
            
        return self.book


    def ratio_function(self, book):
        temp = book.copy()
        temp = temp[['outcome', 'shares']]
        temp = pd.pivot_table(temp, values='shares', index = temp.index, columns='outcome', aggfunc=np.sum)
        temp = temp.fillna(method='ffill').fillna(0)
        temp['sum'] = temp.columns[0]
        for col in temp.columns[1:]:
            temp['sum'] += temp[col]

        if self.book.index[-1] <10:
            periodLengthLong = self.book.index[-1]+1
        else:
            periodLengthLong = 9 
        
        periodLengthShort = 1 
        if book.shape[0]<1:
            periodLengthShort = 1
        if book.shape[0]<2:
            periodLengthLong = 1

        #calculate EMA for the average volume
        if len(temp['sum']) >3:
            longWindow = math.ceil((temp['sum'].rolling(periodLengthLong).mean().tolist())[-1])
            shortWindow = math.ceil((temp['sum'].rolling(periodLengthShort).mean()).tolist()[-1])
            
        else:
            if len(temp['sum'])>1:
                shortWindow = temp['sum'].mean()
                longWindow = temp['sum'].mean()
            elif len(temp['sum'])==1:
                shortWindow = math.ceil(temp['sum'][0])
                longWindow = math.ceil(temp['sum'][0])
                
        if longWindow ==0:
            r = 0
        else:
            r = shortWindow/longWindow
        return r

    @property
    def b(self):
        if self.market == 'RIKIDDO':
            if len(self.book)<1:
                return self._b_init(self.x)
            else:
                return self._b(self.x, self.ratio_function(self.book))
    
    def _b_init(self, x):
        return self.f * x.sum()

    def _b(self, x, ratio_function):
        return (self.f + (0.01*ratio_function/math.sqrt(6+ratio_function**2)))* x.sum()

    @property
    def book(self):
        return pd.DataFrame(self._book)
    
    @property
    def x(self):
        return self._x[-1].copy()

    @property
    def x_history(self):
        return self._x[-1].copy()
    
    def cost(self, x):
        return self.b*np.log(np.exp(x/self.b).sum())
    
    def _new_x(self, shares, outcome):
        new_x = self.x
        new_x[outcome] += shares        
        return new_x
    
    def cpmm_spot_price(self, book, outcome):
        if book.shape[0]>1:
            temp = book.copy()
            temp = temp[['outcome', 'shares']]
            temp = pd.pivot_table(temp, values='shares', columns='outcome', aggfunc=np.sum)
            outcome_balance = temp[outcome].sum()
            colnames = list(temp.columns)
            temp['sum'] = temp.columns[0]
            for col in temp.columns[1:]:
                temp['sum'] += temp[col]
            
            temp['sum'] = temp['sum'] - temp[outcome]
                
            non_outcome_balance = temp['sum'].sum()

            ratio = outcome_balance/non_outcome_balance
            result = ratio*(1/(1-self.swap_fee))
            fee_cost = ratio*self.swap_fee
        else:
            pass

        return result, fee_cost

    def price(self, shares, outcome):
        if self.market == 'RIKIDDO':
            result = self._price(self._new_x(shares, outcome))
        elif self.market == 'CPMM':
            result, fee_cost = self.cpmm_spot_price(self.book, outcome)
        return result

    def _price(self, x):
        return self.cost(x)-self.cost(self.x)
    
    def register_x(self, x):
        self._x.append(x)
    
        
    def calculate_shares(self, paid, outcome):
        obj_func = lambda s: np.abs(self.price(s, outcome) - paid)
        return fmin_cobyla(obj_func, paid/self.p[outcome], [])
    
    def buy_shares(self, name, paid, outcome):
        try:
            if self.market == 'RIKIDDO':
                shares = self.calculate_shares(paid, outcome)
                self.register_x(self._new_x(shares, outcome))
                self._book.append({'name':name, 
                                    'shares':shares, 
                                    'outcome':outcome, 
                                    'paid':paid, 
                                    #'fee_cost': , add it for rikiddo
                                    'lp': 0})
                self._history.append(self.p)
                self.market_value += paid

            elif self.market == 'CPMM':
                outcome_price, fee_cost = self.cpmm_spot_price(self.book, outcome)
                shares = paid/outcome_price
                self.register_x(self._new_x(shares, outcome))
                self._book.append({'name':name, 
                                    'shares':shares, 
                                    'outcome':outcome, 
                                    'paid':paid, 
                                    'fee_cost': fee_cost*shares,
                                    'lp': 0})
                self._history.append(self.p)
                self.market_value += paid

            print("%s paid %2.2f ZTG, for %2.2f shares of outcome %d, which will give him %2.2f ZTG if he wins"%(
                    name, paid, shares, outcome, shares/self.x[outcome]*self.market_value))
            return shares
        except:
            raise ValueError("Seems that you didn't provide liquidity, have you?")
    
    def sell_shares(self, name, shares, outcome):
        price = self.price(-shares, outcome)
        self._book.append({'name':name, 
                            'shares':-shares, 
                            'outcome':outcome, 
                            'paid':-price, 
                            #'fee_cost': , add it for rikiddo
                            'lp': 0}) 
        self.market_value -= price        
        self._history.append(self.p)   

        return price

    def liquidity_providing(self, name, shares):
        '''
        Liquidity Providers don't perceive a fee
        '''
        prices = list(self.p)
        asset_1 = shares*prices[0]
        asset_2 = shares*prices[1]
        self._book.append({'name':name, 
                            'shares': asset_1, 
                            'outcome': self.possible_outcomes[0],
                            'paid': prices[0], 
                            'fee_cost': 0,
                            'lp': 1})
        self._book.append({'name':name, 
                            'shares': asset_2, 
                            'outcome': self.possible_outcomes[1],
                            'paid': prices[1], 
                            'fee_cost': 0,
                            'lp': 1})
        share = [asset_1, asset_2]
        return share

    def outcome_probability(self):
        if self.market == 'RIKIDDO':
            K = np.exp(self.x/self.b)
            result = K/K.sum()
        elif self.market == 'CPMM':
            x = self.x
            result = (x/x.sum())*(1/(1-self.swap_fee))
        return result
    
    @property
    def p(self):
        return self.outcome_probability()
    
    def history(self):
        return np.array(self._history)