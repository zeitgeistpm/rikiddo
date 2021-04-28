import math
from lsdLMSRCoreFunctions import getVolumeRatio, z_r, eValue, lsdCostFunction, lsdPriceFunction_i, minRevenue
# from getAssetData import getVolumeData
import pandas as pd
from datetime import datetime, date, timedelta
from scipy.stats import pearsonr
import json
import numpy as np
import random
import time
from tqdm import tqdm
# import getKnownAssetValues

symbol1= 'BUSDUSDT'
symbol2= 'BNBUSDT'

fee, m, p, n, k = 0.03, 0.005, 6, 0.9, 1 #assume a low correlated pair of assets


# %% Simulation Settings
b = 0.75
minRev = minRevenue(b, fee)
q_1 = 30000 
q_2 = 1000000

ratio_q_1 = q_1 / (q_1 + q_2)
ratio_q_2 = q_2 / (q_1 + q_2)
simulationRecord = pd.DataFrame([])
indexer = 0

#Initial state
account1 = f'account_{symbol1}'
account2 = f'account_{symbol2}'
data = {'transactionNumber': [0], 
        account1 : [q_1], 
        account2: [q_2], 
        'totalFee': [fee], 
        'whoBuy': ['Initial'], 
        'ratioVolume': [q_1/q_2], 
        'z': [0], 
        'buy': ['Initial'], 
        'sell': ['Initial'],
        'transactCost': [0]}

simulationRecord = simulationRecord.append(pd.DataFrame.from_dict(data))

transaction = 0
start_time = time.time()
print('--------------------------------------LOOP PRINTS--------------------------------------')
#%% Loop simulation
# for i in tqdm(range(4000)):
while time.time() - start_time <4:
    transaction += 1
    symbols = [symbol1, symbol2]
    poolInventory= [q_1, q_2]
    buyAsset = random.choice(symbols)
    indexNum = symbols.index(buyAsset)
    if indexNum == 0:
        yElement = symbols[1]
    else:
        yElement = symbols[0]
    # print(indexNum)
    # print(f'We are going to buy {buyAsset} and we will give away {yElement}')

    r = getVolumeRatio(symbols, simulationRecord)
    z = z_r(r, m, p, n)
    totalFee = fee + z
    if totalFee < minRev:
        print('Your fee is lower than expected. Bounding with minRevenue')
        totalFee = minRev

    #how much you want to buy
    deltaQ = random.uniform(0, 5000)

    if indexNum == 0:
        q_1 += deltaQ
        q_2 -= deltaQ*ratio_q_2
    else:
        q_1 -= deltaQ*ratio_q_1
        q_2 += deltaQ

    if (q_1<0) | (q_2<0): 
        print('no liquidity')
        break
    #cost function 
    eVal, dynamicFee = eValue(poolInventory, totalFee)
    C_q = lsdCostFunction([q_1, q_2], eVal, dynamicFee)

    transactCost = C_q - data['transactCost'][-1]

    previousState =[data[f'account_{symbol1}'][-1], data[f'account_{symbol2}'][-1]]

    P_q_1 = lsdPriceFunction_i(C_q, totalFee, previousState, poolInventory)

    print(C_q, P_q_1)


#     ########################## ESTABLISHING BOUNDS FOR THE POOL ###################################
#     # print(f'final fee: {totalFee}')

#     if (totalFee> minFee) & (totalFee<maxFee):
#         # print("The total fee is in range, you don't have liquidity problems")
#         pass
#     else:
#         print("The total fee is OUT OF RANGE, you have liquidity problems, so we will turn down your pool")
#         break



    data['transactionNumber'].append(transaction)
    data[f'account_{symbol1}'].append(q_1)
    data[f'account_{symbol2}'].append(q_2)
    data['totalFee'].append(totalFee)
    data['whoBuy'].append(buyAsset)
    data['ratioVolume'].append(r)
    data['z'].append(z)
    if indexNum == 0:
        data['sell'].append(deltaQ*ratio_q_2)
    else:
        data['sell'].append(deltaQ*ratio_q_1)
    data['buy'].append(deltaQ)
    data['transactCost'].append(transactCost)

    transaction += 1

###############################################################################################

print("--- %s seconds ---" % (time.time() - start_time))
print(f'We made {transaction} transactions in 4 seconds with LSD-LMSR')
simulationRecord = simulationRecord.append(pd.DataFrame.from_dict(data))
simulationRecord.to_csv('simulationRecord.csv')

netProfit = sum(data['transactCost'])
# print(f'the Liquidity Providers will make {netProfit}')