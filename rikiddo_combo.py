import numpy as np
from scipy.optimize import fmin_cobyla
import pandas as pd
import math 
from itertools import permutations

class RikiddoComboScoringRule(object):
    def __init__(self, possible_outcomes, n_params, initial_liquidity, vig=0.1, init=1.0, market='LS_LMSR', b=None):
        """
        Parameters
        ----------
        possible_outcomes   list
                            list of all possible outcomes of the market
                            
        n_params            list
                            A list that consists on the 3 parameters that influnces the variable fee
                            
        initial_liquidity   int
                            Amount of initial liquidity that is provided for each one of the assets
                                    
        vig                 float
                            parameter of the `alpha` variable used to calculate the `b` variable.
                            Corresponds to the market "vig" value
                
        init                float
                            The initial subsidies of the market, spread equally in this algorithm on all the outcomes.
        
        
                            
        """
        
        def combo_assets_maker(assets):
            possible_combos = []
            for L in range(1, len(assets)+1):
                for subset in itertools.combinations(assets, L):
                    possible_combos += [i for i in list(permutations(subset))]
                    
            combo_assets = []
            for i in possible_combos:
                value = ''
                for j in range(len(i)):
                    value += str(i[j])
                combo_assets += [value]

            return combo_assets
            
        self.possible_outcomes = combo_assets_maker(possible_outcomes)
        
        self.initial_liquidity = initial_liquidity
        
        self.init = init
        self.n = len(self.possible_outcomes)
        self._x = [np.ones([self.n])*init/self.n]
        self._book = []
        self.market_value = init
        self._history = []
        self.alpha = vig*self.n/np.log(self.n)
        
        self.param_1 = n_params[0]
        self.param_2 = n_params[1]
        self.param_3 = n_params[2]
        
    @property
    def b(self):
        if len(self.book)<45:
            return self._b_init(self.x)
        else:
              return self._b(self.x, self.ratio_function(self.book))
    
    def _b_init(self, x):
        return self.alpha * x.sum()

    def _b(self, x, ratio_function):
        total_fee = self.alpha + (self.param_1 * ratio_function/math.sqrt(self.param_2+ratio_function**self.param_3))
        if total_fee < self.alpha * 0.4:
            total_fee = self.alpha * 0.4
        return  total_fee * x.sum()
    
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
            
        periodLengthLong = 45
        periodLengthShort = 25

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
    
    def initial_liquidity(self, amount):
        print(self.possible_outcomes)
        for i in range(0, len(self.possible_outcomes)):
            self._book.append({'name': 'Zeitgeist', 
                                'shares': amount, 
                                'outcome': i, 
                                'paid': amount*(1/len(self.possible_outcomes)), 
                                'fee_cost': 0,
                                'lp': 1})
        
        return self.book
        
    @property
    def book(self):
        return pd.DataFrame(self._book)
    
    @property
    def x(self):
        return self._x[-1].copy()
    
    def cost(self, x):
        return self.b*np.log(np.exp(x/self.b).sum())
    
    def _new_x(self, shares, outcome):
        new_x = self.x
        new_x[outcome] += shares        
        return new_x
            
    def price(self, shares, outcome):
        return self._price(self._new_x(shares, outcome))
        
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
                           'paid':paid})
        self._history.append(self.p)
        self.market_value += paid
        print("%s BOUGHT %2.2f shares of outcome %d"%(
                name, shares, outcome))
        return shares
    
    def sell_shares(self, name, shares, outcome):
        price = self.price(-shares, outcome)
        self._book.append({'name':name, 
                           'shares':-shares, 
                           'outcome':outcome, 
                           'paid':-price}) 
        self.market_value -= price        
        self._history.append(self.p)   
        print("%s SOLD %2.2f shares of outcome %d"%(
                name, shares, outcome))
        
        return price
    
    def liquidity_providing(self, name, shares):
        '''
        Liquidity Providers don't perceive a fee
        '''
        prices = list(self.p)
        price_share = []
        for i in range(len(prices)):
            share = shares*prices[i]
            #exec(f'asset_{i} = shares*prices[{i}]')
            self._book.append({'name':name, 
                            'shares': share,
                            'outcome': self.possible_outcomes[i],
                            'paid': prices[i], 
                            'fee_cost': 0,
                            'unit_price': prices[i]/share,
                            'lp': 1})
            price_share += []
            
        self._history.append(list(self.p))
        print("%s provided liquidity the equivalent to %2.2f ZTG."%(
                name, shares))
        
        return price_share

    def outcome_probability(self):
        K = np.exp(self.x/self.b)
        return K/K.sum()
    
    @property
    def p(self):
        return self.outcome_probability()
    
    def history(self):
        return np.array(self._history)
