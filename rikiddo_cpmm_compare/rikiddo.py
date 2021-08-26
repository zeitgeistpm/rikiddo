import numpy as np
from scipy.optimize import fmin_cobyla
import pandas as pd
import math 

class RikiddoScoringRule(object):
    def __init__(self, possible_outcomes, n_params, vig=0.05, init=1.0):
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
        
        n_param             list
                            A list that consists on the 3 parameters that influnces the variable fee
                            
        """
        self.possible_outcomes = possible_outcomes

        self.init = init
        self.n = len(self.possible_outcomes)
        self._x = [np.ones([self.n])*init/self.n]
        self._book = []
        self.market_value = init
        self._history = []
        self.f = vig/self.n*np.log(self.n)
        self._prices = []
        
        if len(n_params) != 3:
            raise valueError("3 parameters were expected, seems that you've provided more/less")
           
        self.param_1 = n_params[0]
        self.param_2 = n_params[1]
        self.param_3 = n_params[2]
        
    def outcome_probability(self):
        K = np.exp(self.x/self.b)
        result = K/K.sum()
        
        return result
    
    @property
    def p(self):
        return self.outcome_probability()
    
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

        if self.book.index[-1] <6:
            periodLengthLong = self.book.index[-1]+1
        else:
            periodLengthLong = 5 
        
        periodLengthShort = 1 
        if book.shape[0]<1:
            periodLengthShort = 1
        if book.shape[0]<2:
            periodLengthLong = 1

        #calculate EMA for the average volume
        if len(temp['shares']) >5:
            longWindow = math.ceil((temp['shares'].rolling(periodLengthLong).mean().tolist())[-1])
            shortWindow = math.ceil((temp['shares'].rolling(periodLengthShort).mean()).tolist()[-1])
            
        else:
            if len(temp['shares'])>1:
                shortWindow = temp['shares'].mean()
                longWindow = temp['shares'].mean()
            elif len(temp['shares'])==1:
                shortWindow = math.ceil(temp['shares'][0])
                longWindow = math.ceil(temp['shares'][0])
                
        if longWindow ==0:
            r = 0
        else:
            r = shortWindow/longWindow
        return r

    @property
    def b(self):
        if len(self.book)<1:
            return self._b_init(self.x)
        else:
            return self._b(self.x, self.ratio_function(self.book))
    
    def _b_init(self, x):
        return self.f * x.sum()

    def _b(self, x, ratio_function):
        return (self.f + (self.param_1*ratio_function/math.sqrt(self.param_2+ratio_function**self.param_3)))* x.sum()

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

    def price(self, shares, outcome):
        result = self._price(self._new_x(shares, outcome))
        
        return result

    def _price(self, x):
        return self.cost(x)-self.cost(self.x)
    
    def register_x(self, x):
        self._x.append(x)
    
        
    def calculate_shares(self, paid, outcome):
        obj_func = lambda s: np.abs(self.price(s, outcome) - paid)
        return fmin_cobyla(obj_func, paid/self.p[outcome], [])
    
    def buy_shares(self, name, paid, outcome):
        shares = self.calculate_shares(paid, outcome)
        self.register_x(self._new_x(shares, outcome))
        self._book.append({'name':name, 
                            'shares':shares, 
                            'outcome':outcome, 
                            'paid':paid,
                            'unit_price': paid/shares,
                           #'fee': ,
                            'lp': 0})
        self._history.append(list(self.p))
        self.market_value += paid
        #print("%s paid %2.2f ZTG, for %2.2f shares of outcome %d, which will give him %2.2f ZTG if he wins"%(
        #        name, paid, shares, outcome, shares/self.x[outcome]*self.market_value))
        return shares
    
    def sell_shares(self, name, shares, outcome):
        price = self.price(-shares, outcome)
        self._book.append({'name':name, 
                            'shares':-shares, 
                            'outcome':outcome, 
                            'paid':-price, 
                            'unit_price': price/shares,
                            #'fee_cost': , add it for rikiddo
                            'lp': 0}) 
        self.market_value -= price        
        self._history.append(list(self.p))   

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
                            'unit_price': prices[0]/asset_1,
                            'lp': 1})
        self._book.append({'name':name, 
                            'shares': asset_2, 
                            'outcome': self.possible_outcomes[1],
                            'paid': prices[1], 
                            'fee_cost': 0,
                            'unit_price': prices[1]/asset_2,
                            'lp': 1})
        self._history.append(list(self.p))
        share = [asset_1, asset_2]
        
        return share
    
    def history(self):
        return np.array(self._history)
