import pandas as pd

#####
# Data Handling Function
#####
def getDataFrameFromCSV(filename):
    if str(filename).endswith(".csv"):
        return pd.read_csv(filename)
    else:
        return pd.read_excel(filename)


"""
    Returns explanatory and response variable sub data frames

    !How to split data!
        xData = df.loc[:, df.columns != response]
        yData = df.loc[:, df.columns == response]
"""
def getResponseColumn(df, response):
    return df.loc[:, df.columns == response]


def getExplanatoryColumns(df, response):
    return df.loc[:, df.columns != response]

def getColumnForVariable(df, col):
    return df.loc[:, df.columns == col]
