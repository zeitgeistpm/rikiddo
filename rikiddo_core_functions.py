import pandas as pd
from datetime import datetime, date, timedelta
import json
import numpy as np
import random
import math

def fixFee(vig, n):
    fee = vig/(n*math.log(n))
    return fee

def getVolumeRatio(totalCol, df, transactionNumber):
    '''
    totalCol: the name of the column that stores the total volume of the entire amount of assets.
    df: the name of the dataframe where the data is storaged
    '''
    temp = df.copy()
    volumeSum = temp[totalCol]
    if transactionNumber+1 <7:
        periodLengthLong = transactionNumber+1
    else:
        periodLengthLong = 6 
    periodLengthShort = 1 
    if df.shape[0]<1:
        periodLengthShort = 1
    if df.shape[0]<2:
        periodLengthLong = 1

    #calculate EMA for the average volume
    if len(volumeSum) >3:
        longWindow = math.ceil((temp[totalCol].rolling(periodLengthLong).mean().tolist())[-1])
        shortWindow = math.ceil((temp[totalCol].rolling(periodLengthShort).mean()).tolist()[-1])
    else:
        print('long len less than 2')
        if len(volumeSum)>1:
            shortWindow = volumeSum.mean()
            longWindow = volumeSum.mean()
        elif len(volumeSum)==1:
            shortWindow = math.ceil(volumeSum[0])
            longWindow = math.ceil(volumeSum[0])

    if longWindow ==0:
        r = 0
    else:
        r = shortWindow/longWindow


    return r

def z_r(r):
    z = (0.01*(r))/math.sqrt(6 + (r)**2)
    return z


def eValue(q, totalFee):
    eVal = 0
    sumQ = sum(q)
    dynamicFee = totalFee*sumQ
    for q_i in q:
        if dynamicFee !=0:
            e = math.exp(q_i/dynamicFee)
        else:
            e = math.exp(q_i/0.005) #0.005 is the fixed value assumed for the initial fee
        eVal += e

    return eVal, dynamicFee

def lsdCostFunction(q, dynamicFee):
    '''
    q: list
    The cost function captures the amount of total assets wagered in the market where C(q0) 
    is the market maker’s maximum subsidy to the market
    '''
    qa = np.array(q)
    qa = qa/dynamicFee
    vector = np.vectorize(np.exp)
    x = vector(qa)
    cost= dynamicFee*math.log(x.sum())
    return cost

def lsdPriceFunction_i(costFunction,totalFee,q_i,q_j):
    '''
    The price function Pi(q) gives the current cost of buying an infinitely 
    small quantity of the category i token.
    '''
    sumQj = sum(q_j)
    e_j, dynamicFee = eValue(q_j, totalFee)
    e_i, dynamicFee = eValue(q_i, totalFee)
    sum_ej = 0
    qxe = 0
    for q in q_j:
        e = math.exp(q/dynamicFee)
        sum_ej += e
        qxe += q*e
    
    numerator = e_i*sumQj - qxe
    denominator = sumQj*sum_ej
    if sumQj != 0:
        p_i = totalFee*math.log(e_j) + (numerator/denominator)
    else:
        p_i = totalFee*math.log(e_j)
    return p_i

def minRevenue(b, fee):
    '''
    b value must be between 0 and 1
    '''
    w = b*fee
    return w


# def poolInitialValues(initialAmount, listOfProportions):
