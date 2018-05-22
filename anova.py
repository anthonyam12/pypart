"""
    This file contains the ANOVA functions used by the CART algorithm.
"""

from data_handler import *

"""
    Calculate the error between predicted value and actual value
"""
def AnovaPred(y, yHat):
    temp = y - yHat
    return temp**2


"""
    Calculate the Sum of Squares for a given response data frame.

    TESTED: compared to R output for the same SS
"""
def AnovaSS(respDf):
    yBar = respDf.iloc[:, 0].mean()
    ss = 0      # = risk
    for val in respDf.iloc[:, 0]:
        ss += ((val - yBar)**2)

    return ss

"""
    Find the split point of a variable using ANOVA methods
"""
def AnovaSplitPoint(dataFrame, response, minNode, varName):
    LEFT = -1
    RIGHT = 1

    y = getResponseColumn(dataFrame, response)
    x = getColumnForVariable(dataFrame, varName)

    myRisk = AnovaSS(y)

    rightWt = len(dataFrame)  # Assuming equal weight (1's), replace with sum(wt) if desired (wt is a vector of weights)
    rightN = len(dataFrame)
    rightSum = sum(y.iloc[:, 0])
    grandMean = rightSum / rightWt
    
    # assuming continuous for all variables, need to special case here otherwise
    leftSum = 0
    leftWt = 0
    leftN = 0
    rightSum = 0
    best = 0
    where = 0
    i = 0
    direction = LEFT
    while rightN > minNode:
        leftWt += 1
        rightWt -= 1
        leftN += 1
        rightN -= 1
        temp = (y.iloc[i, 0] - grandMean) * 1  # 1 = wt[i]
        leftSum += temp
        rightSum -= temp
        if x.iloc[i + 1, 0] != x.iloc[i, 0] and leftN >= minNode:
            temp = ((leftSum**2) / leftWt) + ((rightSum**2) / rightWt)
            if temp > best:
                best = temp
                where = i
                if leftSum < rightSum:
                    direction = LEFT
                else:
                    direction = RIGHT
        i += 1

    if myRisk == 0:
        improve = 0
    else:
        improve = best / myRisk
    if len(x) > where + 1:
        split = (x.iloc[where, 0] + x.iloc[where + 1, 0]) / 2
    else:
        split = x.iloc[where, 0]
#    if len(dataFrame) == 96:
#        print(where, split, improve)
#        print(len(dataFrame), where, x.iloc[where, 0])
    return where, direction, split, improve
