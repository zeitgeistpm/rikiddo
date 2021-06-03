import math
from lsdLMSRCoreFunctions import getVolumeRatio, z_r, eValue, lsdCostFunction, lsdPriceFunction_i, minRevenue
import pandas as pd
from datetime import datetime, date, timedelta
import json
import numpy as np
import random
import time
import matplotlib.pyplot as plt

symbol1= 'Will'
symbol2= 'Will_not'

fee, m, p, n, k = 0.03, 0.8, 8, 1, 1 #low correlated pair of assets
traderMaxFee = 10.2

# %% Simulation Settings
b = 0.7
minRev = minRevenue(b, fee)
q_1 = 1000000 #max volume available for q_1 
q_2 = 1000000 #max volume available for q_2
q_1_pool = 0 #amount of q_1 inside the pool
q_2_pool = 0 #amount of q_2 inside the pool
liquidityBounds = [q_1<10000, q_2<10000]

ratio_q_1 = q_1 / (q_1 + q_2)
ratio_q_2 = q_2 / (q_1 + q_2)
simulationRecord = pd.DataFrame([])
indexer = 0

#Initial state
account1 = f'account_{symbol1}'
account2 = f'account_{symbol2}'
account1_pool = f'account_{symbol1}_pool'
account2_pool = f'account_{symbol2}_pool'
data = {'transactionNumber': [0], 
        account1 : [q_1], 
        account2: [q_2], 
        account1_pool : [0], 
        account2_pool: [0],
        'totalVolume': q_1+q_2,
        'totalPoolVolume': [0],
        'totalFee': [fee], 
        'whoBuy': ['Initial'], 
        'ratioVolume': [q_1/q_2], 
        'z': [0], 
        'order': ['Initial'],
        'transactCost': [0],
        'previousCost': [0],
        'deltaQ': [0],
        'costPerUnit': [0], 
        'r': 1}

simulationRecord = simulationRecord.append(pd.DataFrame.from_dict(data))

transaction = 0
start_time = time.time()
print('--------------------------------------LOOP PRINTS--------------------------------------')
#%% Loop simulation

symbols = [symbol1, symbol2]
previousStateCost = 0
while time.time() - start_time <4:
    # transaction += 1
    poolInventory= [q_1_pool, q_2_pool]
    buysell = ['buy', 'sell']
    signals = [0.5, 0.5]
    buysellSignals = [0.5, 0.5]

    #The signal changes every 500 transactions
    if transaction%500 == 0:
        signals[0] = random.random()
        signals[1] = 1 - signals[0]
        buysellSignals[0] = 1 - signals[0]
        buysellSignals[1] = signals[0]
    
    buyAsset = np.random.choice(symbols, 1, True, signals)

    marketSignal = np.random.choice(buysell, 1, True, buysellSignals)

    indexNum = symbols.index(buyAsset)
    if indexNum == 0:
        yElement = symbols[1]
    else:
        yElement = symbols[0]
    
    if (q_1>=1000000) | (q_2>=1000000) | (q_1_pool<=0) | (q_2_pool<=0) & (marketSignal == 'sell'):
        marketSignal = 'buy'
        #establishing bounds to the buy or sell decission

    asset_pool = f'account_{symbols[indexNum]}_pool'
    r = getVolumeRatio('totalPoolVolume', simulationRecord, transaction)

    z = z_r(r, m, p, n)
    totalFee = fee + z
    if totalFee < minRev:
        print('Your fee is lower than expected. Bounding with minRevenue')
        totalFee = minRev

    #how much you want to buy or sell
    deltaQ = random.uniform(0, 1000)

    #Pool liquidity bounds
    if (q_1<15000) | (q_2<15000):
        print('LIQUIDITY WARNING: Rising fee dramatically')
        totalFee = 0.5
    
    if totalFee <= traderMaxFee:
        #Cost function 
        eVal, dynamicFee = eValue(poolInventory, totalFee)

        if marketSignal == 'buy':
            if indexNum == 0:
                q_1 -= deltaQ
                q_1_pool += deltaQ
            else:
                q_2_pool += deltaQ
                q_2 -= deltaQ

            if (q_1<0) | (q_2<0): 
                print('no liquidity')
                break
        
        elif marketSignal == 'sell':
            if indexNum == 0:
                q_1 += deltaQ
                q_1_pool -= deltaQ
            else:
                q_2_pool -= deltaQ
                q_2 += deltaQ
        

        C_q = lsdCostFunction([q_1_pool, q_2_pool], eVal, dynamicFee)
        
        transactCost = C_q - previousStateCost

        previousState =[data[f'account_{symbol1}'][-1], data[f'account_{symbol2}'][-1]]

        P_q_1 = lsdPriceFunction_i(C_q, totalFee, previousState, poolInventory)

        print(C_q, P_q_1)

        costPerUnit = (transactCost-deltaQ)/deltaQ

        simdata = {'transactionNumber': [transaction], 
        account1 : [q_1], 
        account2: [q_2], 
        account1_pool : [q_1_pool], 
        account2_pool: [q_2_pool],
        'totalVolume': [q_1+q_2],
        'totalPoolVolume': [q_2_pool+q_2_pool],
        'totalFee': [totalFee], 
        'whoBuy': [buyAsset], 
        'ratioVolume': [r], 
        'z': [z], 
        'order': [marketSignal],
        'transactCost': [transactCost],
        'previousCost': [previousStateCost],
        'deltaQ': [deltaQ],
        'costPerUnit': [costPerUnit], 
        'r': r}

        df_simdata = pd.DataFrame(data=simdata)
        simulationRecord = simulationRecord.append(df_simdata)
        simulationRecord['profitCumSum'] = simulationRecord['transactCost'].cumsum()
        previousStateCost = C_q
        transaction += 1
    
    else:
        print('Fee is too high for the trader')

###############################################################################################

print("--- %s seconds ---" % (time.time() - start_time))
print(f'We made {transaction} transactions in 4 seconds with LSD-LMSR')
simulationRecord.to_csv('simulationRecord.csv')

plt.scatter(simulationRecord['totalFee'], simulationRecord['transactCost'])
plt.xlabel('Total Fee')
plt.ylabel('Transaction Cost')
plt.savefig('fee-cost.png')
plt.show()

plt.scatter(simulationRecord['r'], simulationRecord['totalFee'])
plt.xlabel('r')
plt.ylabel('Total Fee')
plt.savefig('profitsum-cost.png')
plt.show()
