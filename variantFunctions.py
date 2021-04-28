def getVolumeRatio(symbol, symbols, df):
    '''
    symbol: str. Name of the particular symbol
    symbols: a list of every symbol in the pool
    df: the name of the dataframe where the data is storaged
    '''
    
    volumeSum = []
    for i in range(0,df.shape[0]):
        rowSum= 0
        for symbol in symbols:
            colname = f'asset_{symbol}'
            rowSum += df[colname][i]
        volumeSum += [rowSum]
    periodLengthLong = math.ceil(df.shape[0]*0.3)
    if periodLengthLong==0:
        periodLengthLong = 1
    #calculate EMA for the average volume
    longWindow = volumeSum.ewm(span=periodLengthLong).mean()[-1]
    periodLengthShort = math.ceil(df.shape[0]*0.1)
    if periodLengthShort == 0:
        periodLengthShort = 1
    shortWindow = volumeSum.ewm(span=periodLengthShort).mean()[-1]
    rPool = shortWindow/longWindow
    colname = f'volume_{symbol}'
    #calculate EMA for the average volume
    longWindowAsset = df[colname].ewm(span=periodLengthLong).mean()[-1]
    shortWindowAsset = df[colname].ewm(span=periodLengthShort).mean()[-1]
    rAsset = shortWindowAsset/longWindowAsset
    return rAsset/rPool