import pandas as pd

class CPMM(object):
    def __init__(self, initial_state, fee):
        '''
        Parameters
        ----------
        initial_state   dict
                        dictionary containing the assets and initial liquidity of the market. Example: initial_state = {'A': 500, 'B': 500}

        fee             float
                        number between 0 and 1 representing the fixed fee of the CPMM
        '''
        self._state = initial_state.copy()
        self._fee = fee
        self._fee_inverse = 1.0 + fee
        self._fee_sum = []
        self._liquidity = {}
        self._book = []
        if (fee<0) | (fee>1):
            raise ValueError('Fee needs to be inside [0,1] interval')

    def get_prices(self, asset=None, compared_to=None):
        '''
        Parameters
        ----------
        asset           str
                        Optional. Name of the asset that you want to know the proce

        comparet_to     str
                        Optional. Name of the asset inside the pool that you want to compare with
        
        -------
        Returns         float/dict
                        Returns a float number in case that the name of the asset is provided.
                        If not, returns a dictionary with all the asset prices in the pool
        '''
        temp_dict = self._state.copy()
        del temp_dict['ZTG']
        
        if (asset is None) & (compared_to is None):
            prices = {}
            for key, value in temp_dict.items():
                prices[key] = (sum(temp_dict.values())-value)/(sum(temp_dict.values()))
        elif compared_to is None:
            prices = (sum(temp_dict.values())-temp_dict[asset])/sum(temp_dict.values())
        else:
            prices = temp_dict[compared_to]/temp_dict[asset]

        return prices


    def buy_shares(self, in_number, asset_out, asset_in='ZTG'):
        '''
        Parameters
        ----------
        in_number       int
                        Asset amount that is intended to put into the pool
        
        asset_out       float
                        Name of the asset that is taken out of the pool (bought)
        
        asset_in        float
                        Name of asset that is put into the pool (ZTG by default)

        -------
        Returns         float
                        Amount of assets that the pool is going to give away (fees discounted)
        '''
        k = self._state[asset_in] * self._state[asset_out]
        num_in = in_number / self._fee_inverse
        num_out = self._state[asset_out] - k / (self._state[asset_in] + num_in)
        self._state[asset_in] += in_number
        self._state[asset_out] -= num_out
        self._fee_sum += [in_number - num_in] #fee is expressed in ZTG
        self._book.append({'operation': 'buy',
                            'shares': num_out,
                            'outcome': asset_out,
                            'paid': in_number,
                            'fee': in_number - num_in
                        })
        return num_out

    def sell_shares(self, out_number, asset_in, asset_out='ZTG'):
        '''
        Parameters
        ----------
        out_number      int
                        Asset amount that is intended to extract outside the pool
        
        asset_in        float
                        Name of the asset that is taken out of the pool (sold)
        
        asset_out       float
                        Name of asset that is put into the pool (ZTG by default)

        -------
        Returns         float
                        Amount of assets that the pool is going to receive (fees discounted)
        '''
        k = self._state[asset_in] * self._state[asset_out]
        num_out = out_number/self._fee_inverse
        num_in = self._state[asset_in] - k / (self._state[asset_out] - num_out)
        self._state[asset_out] -= num_out
        self._state[asset_in] += num_in
        self._fee_sum += [out_number - num_out] 
        self._book.append({'operation': 'sell',
                            'shares': num_in,
                            'outcome': asset_in,
                            'paid': out_number,
                            'fee': out_number - num_out
                        })
        return num_in

    def provide_liquidity(self, id, amount):
        '''
        Use
        ---
        Determines the share distribution of a liquidity provider. They don't pay fee

        Parameters
        ----------
        id              int
                        Number that enables to identify each Liquidity Provider by separate
        
        amount          int
                        Total amount of ZTG provided

        -------
        Returns         dict
                        A dictionary with the quantity of shares provided plus the total amount of ZTG
        '''
        getprices = self.get_prices()
        liquidity_prividing = {}
        for key, value in getprices.items():
            liquidity_prividing[key] = value*amount
            self._state[key] += value*amount
        
        liquidity_prividing['total_provided'] = amount
        self._liquidity[id] = liquidity_prividing

        self._book.append({'operation': 'liquidity_providing',
                            'shares': amount,
                            'outcome': '-',
                            'paid': amount,
                            'fee': 0
                        })

        return liquidity_prividing

    @property
    def book(self):
        return pd.DataFrame(self._book)
    
    @property
    def state(self):
        return self._state