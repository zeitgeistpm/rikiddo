import pandas as pd
from datetime import datetime, date, timedelta
from scipy.stats import pearsonr
import json
import numpy as np
import random
import math

def getVolumeRatio(symbols, df):
    '''
    symbols: a list of every symbol in the pool
    df: the name of the dataframe where the data is storaged
    '''
    volumeSum = list([])
    for i in range(0,df.shape[0]):
        rowSum= 0
        for symbol in symbols:
            colname = f'account_{symbol}'
            rowSum += df[colname][i]
        volumeSum += [rowSum]
        #More efficient way: sum directly the columns (con: this is possible because we are working with a DF. Check out Rust availability)

    # periodLengthLong = math.ceil(df.shape[0]*0.3)
    # if periodLengthLong==0:
    #     periodLengthLong = 1
    
    periodLengthLong = 2
    if df.shape[0]<2:
        periodLengthLong = 1
    #calculate EMA for the average volume
    if len(volumeSum) >1:
        longWindow = pd.Series(volumeSum).ewm(span=periodLengthLong).mean()[-1]
    else:
        longWindow = volumeSum
    
    # periodLengthShort = math.ceil(df.shape[0]*0.1)
    # if periodLengthShort == 0:
    #     periodLengthShort = 1
    
    periodLengthShort = 1
    if df.shape[0]<1:
        periodLengthShort = 1

    if len(volumeSum)>1:
        shortWindow = pd.series(volumeSum).ewm(span=periodLengthShort).mean()[-1]
    else:
        shortWindow = volumeSum
    r = shortWindow[-1]/longWindow[-1]
    return r


def z_r(r, m, p, n):
    z = (m*(r-n))/math.sqrt(p + (r-n)**2)
    return z


def eValue(q, totalFee, q_x=None):
    eVal = 0
    sumQ = sum(q)
    dynamicFee = (totalFee)*sumQ
    if q_x == None:
        for q_i in q:
            e = math.exp(q_i/dynamicFee)
            eVal += e
    else:
        for q_i in q.remove(q_x):
            e = math.exp(q_i/dynamicFee)
            eVal += e

    return eVal, dynamicFee

def lsdCostFunction(q, eVal, dynamicFee):
    '''
    q: list
    The cost function captures the amount of total assets wagered in the market where C(q0) 
    is the market maker’s maximum subsidy to the market
    '''
    sumQ = sum(q)

    eValue = math.log(eVal)
    costFunction = dynamicFee * eValue
    return costFunction

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
    p_i = costFunction + (numerator/denominator)
    return p_i

def minRevenue(b, fee):
    '''
    b value must be between 0 and 1
    '''
    w = b*fee
    return w


# def poolInitialValues(initialAmount, listOfProportions):
