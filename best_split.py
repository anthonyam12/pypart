"""
    Determines the best split point for a node.
"""
from anova import *

LEFT = -1
RIGHT = 1

"""
    Find the best split for ANOVA (regression trees)

    Data comes from the dataframe stored in 'node.data'. This will be trimmed to only include the
    data that reaches this node.
"""
def bsplit(node, response, params):
    dataFrame = node.data
    yBar = getResponseColumn(dataFrame, response).iloc[:, 0].mean()
    deviance = AnovaSS(getResponseColumn(dataFrame, response))
    xDf = getExplanatoryColumns(node.data, response)
    bestSS = 9999999999
    baseSS = bestSS
    bestL1 = None
    bestL2 = None

    for var in xDf.columns:
        # sort on var? Yes, produces rpart results
        dataFrame = dataFrame.sort_values([var])
        where, direction, split, improvement = AnovaSplitPoint(dataFrame, response, params.minNode, var)

        # first split, left = 'yes' in the tree
        if direction < 0:       # < x go left -- swapped > with < after and the tree is EXACTLY like rpart's
            L1 = dataFrame[dataFrame[var] < split]
            L2 = dataFrame[dataFrame[var] >= split]
        else:                   # < x go right (> x go left)
            L1 = dataFrame[dataFrame[var] > split]
            L2 = dataFrame[dataFrame[var] <= split]

        if params.delayed > 0 and improvement > 0:
            # create L3 and L4 from L1 an d L5 and L6 from L2
            # split L1
            bestLeftSS = 9999999999
            bestRightSS = 9999999999
            for var2 in xDf.columns:
                L1 = L1.sort_values([var2])
                whereL, directionL, splitL, improvementL = AnovaSplitPoint(L1, response, params.minNode, var2)
                if directionL < 0:
                    L3 = L1[L1[var2] < splitL]
                    L4 = L1[L1[var2] >= splitL]
                else:
                    L3 = L1[L1[var2] > splitL]
                    L4 = L1[L1[var2] <= splitL]
                thisSSLeft = AnovaSS(getResponseColumn(L3, response)) + AnovaSS(getResponseColumn(L4, response))

                if thisSSLeft < bestLeftSS and improvementL > 0:
                    bestLeftSS = thisSSLeft

                L2 = L2.sort_values([var2])
                whereR, directionR, splitR, improvementR = AnovaSplitPoint(L2, response, params.minNode, var2)
                if directionR < 0:
                    L5 = L2[L2[var2] < splitR]
                    L6 = L2[L2[var2] >= splitR]
                else:
                    L5 = L2[L2[var2] > splitR]
                    L6 = L2[L2[var2] <= splitR]
                thisSSRight = AnovaSS(getResponseColumn(L5, response)) + AnovaSS(getResponseColumn(L6, response))

#                if node.numObs == 96:
#                    print("splitR\tdirectionR\timproveR\tsplitL\n\tdirectionL\timproveL")
#                    print(var2, "\n\t", splitR, directionR, improvementR, "\n\t", splitL, directionL, improvementL)

                if thisSSRight < bestRightSS and improvementR > 0:
                    bestRightSS = thisSSRight

            if bestLeftSS != baseSS and bestRightSS != baseSS:
                thisSS = bestLeftSS + bestRightSS
            else:
                thisSS = baseSS
        else:
            thisSS = AnovaSS(getResponseColumn(L1, response)) + AnovaSS(getResponseColumn(L2, response))

        if thisSS == baseSS:
            thisSS = AnovaSS(getResponseColumn(L1, response)) + AnovaSS(getResponseColumn(L2, response))
        if thisSS < bestSS and improvement > 0:     # improvement > 0 -> a non-zero split point
            bestL1 = L1
            bestL2 = L2
            bestSS = thisSS

            node.splitPoint = split
            node.direction = direction
            node.splitIndex = where
            node.varName = var
            node.yval = yBar
            node.dev = deviance
            node.improvement = improvement

    return bestL1, bestL2
