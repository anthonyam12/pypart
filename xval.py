"""
    The functions in this file run cross validations to properly set the values in the CpTable. That is, to set the
    risk, xrisk, xstd, and cp.
"""

from partition import *

import math

'''
    Do the cross validation.

    numXval = number of cross-validations
    cpTableHead = pointer to the head of the cpTable
    xGrp = created in rpart.R, subset of X used for cross validation
    maxCat = max # of categories for categorical variables
'''
def xval(cpTableHead, xGrp, dataframe, params):
    cpList = [cpTableHead.cp * 10]
    cpTemp = cpTableHead
    while cpTemp.forward is not None:
        cpList.append(math.sqrt(cpTemp.cp * cpTemp.forward.cp))
        cpTemp = cpTemp.forward

    # prevDelayed = params.delayed
    # if len(dataframe) > 500 or len(dataframe.columns) > 8:
    #     params.delayed = 0

    totalWt = len(dataframe)
    oldWt = totalWt

    cvo = CrossValidationObj(xGrp, dataframe)
    xtemp, xpred = [], []
    print("\tPerforming cross validations...")
    for xgroup in set(xGrp):
        print("\t\tGroup " + str(xgroup) + " out of " + str(len(set(xGrp))))
        xGroupDf = cvo.dataframeList[xgroup - 1][0]
        xGroupRemainderDf = cvo.dataframeList[xgroup - 1][1]

        temp = len(xGroupDf)
        for i in range(0, len(cpList)):
            cpList[i] *= temp / oldWt
        # rp.alpha *= temp / oldWt     # this is 0 in our case
        # NOTE: oldWt and temp are actually weights for the dataframes, our weights are all 1's so this means they are
        # equal to the number of observations in the dataframe
        oldWt = temp
        xTree = Node()
        xTree.numObs = temp
        xTree.data = xGroupDf
        xTree.cp = AnovaSS(getResponseColumn(xGroupDf, params.response))
        partition(xTree, 1, params)
        fixCp(xTree, xTree.cp)

        for index, row in xGroupRemainderDf.iterrows():
            rundown(xTree, row, cpList, xtemp, xpred, params.response)

            temp = cpTableHead
            for value in xtemp:
                temp.xrisk += value
                temp.xstd += value**2
                temp = temp.forward
            xtemp, xpred = [], []

    temp = cpTableHead
    while temp is not None:
        temp.xstd = math.sqrt(temp.xstd - (temp.xrisk * temp.xrisk) / totalWt)
        temp = temp.forward

    # params.delayed = prevDelayed


'''
    Runs an observations down the tree to get the xrisk and xstd for the CP table
'''
def rundown(tree, row, cpList, xtemp, xpred, response):
    for cp in cpList:
        while cp < tree.cp:
            tree = branch(tree, row)
            if tree is None:
                print("Warning....")
                exit(0)

        xpred.append(tree.yval)
        xtemp.append(AnovaPred(row[response], tree.yval))


'''
    The branch function actually takes the observation down the tree and gets the error
'''
def branch(tree, row):
    if tree.leftNode is None:
        return None

    splitVar = tree.varName
    splitPoint = tree.splitPoint
    direction = tree.direction

    if row[splitVar] > splitPoint:
        direction = -direction

    if direction < 0:
        return tree.leftNode
    return tree.rightNode


'''
    Fixes the cp values as we do cross validations.
'''
def fixCp(node, parentCp):
    if node.cp > parentCp:
        node.cp = parentCp

    if node.leftNode:
        fixCp(node.leftNode, node.cp)
        fixCp(node.rightNode, node.cp)


class CrossValidationObj(object):
    def __init__(self, xGroups, dataframe):
        self.xGroups = xGroups
        self.dataframe = dataframe
        self.dataframeList = []     # list of dataframes, 1 per xgroup (just y values, assuming constant weights)
        self.createXGroupDataframes()

    def createXGroupDataframes(self):
        for i in set(self.xGroups):
            groupIndices = []
            remainderIndices = []
            for j in range(0, len(self.xGroups)):
                val = self.xGroups[j]
                if val != i:
                    groupIndices.append(j)
                else:
                    remainderIndices.append(j)
            self.dataframeList.append([self.dataframe.iloc[groupIndices], self.dataframe.iloc[remainderIndices]])
