from best_split import *
from node import Node

"""
    Partitions the data set until the stopping criteria are met. Assumes user passed cp = 0.0 (rp.alpha = 0 in rpart)
    TODO: add more docs
"""
def partition(node, nodeNum, params):
    response = params.response
    y = getResponseColumn(node.data, response)
    tempcp = AnovaSS(y)
    node.dev = tempcp

    if nodeNum == 1:
        node.cp = node.dev

    if nodeNum > 1 and tempcp > node.cp:
        tempcp = node.cp

    if nodeNum > params.maxNodes or node.numObs < params.minObs or tempcp <= 0:
        node.leftNode = None
        node.rightNode = None
        node.yval = y.iloc[:, 0].mean()
        node.dev = tempcp
        node.cp = 0
        return 0, tempcp
    else:
        # find best split for the node
        left, right = bsplit(node, response, params)

        # update 'where' list
        leftIndices = list(left.index)
        rightIndices = list(right.index)
        for index in leftIndices:
            params.where[index] = nodeNum * 2
        for index in rightIndices:
            params.where[index] = (nodeNum * 2) + 1

        # partition left side of data set
        node.leftNode = Node()
        node.leftNode.numObs = len(left)
        node.leftNode.data = left
        node.leftNode.response = response
        node.leftNode.nodeId = nodeNum * 2
        node.leftNode.cp = tempcp
        leftSplit, leftRisk = partition(node.leftNode, (2 * nodeNum), params)

        # update estimate of cp
        tempcp = (node.dev - leftRisk) / (leftSplit + 1)
        tempcp2 = (node.dev - node.leftNode.dev)
        if tempcp < tempcp2:
            tempcp = tempcp2
        if tempcp > node.cp:
            tempcp = node.cp

        # partition right side of data set
        node.rightNode = Node()
        node.rightNode.numObs = len(right)
        node.rightNode.data = right
        node.rightNode.response = response
        node.rightNode.nodeId = (nodeNum * 2) + 1
        node.rightNode.cp = tempcp
        rightSplit, rightRisk = partition(node.rightNode, 1 + (2 * nodeNum), params)

        # calculate actual cp as if this node is the top node of the tree, to be fixed later
        # TESTED: produces same cp values as rpart (on cars data set at least)
        tempcp = (node.dev - (leftRisk + rightRisk)) / (leftSplit + rightSplit + 1)
        if node.rightNode.cp > node.leftNode.cp:
            if tempcp > node.leftNode.cp:
                leftRisk = node.leftNode.dev
                leftSplit = 0

                tempcp = (node.dev - (leftRisk + rightRisk)) / (leftSplit + rightSplit + 1)
                if tempcp > node.rightNode.cp:
                    rightRisk = node.rightNode.dev
                    rightSplit = 0
        elif tempcp > node.rightNode.cp:
            rightSplit = 0
            rightRisk = node.rightNode.dev
            tempcp = (node.dev - (leftRisk + rightRisk)) / (leftSplit + rightSplit + 1)
            if tempcp > node.leftNode.cp:
                leftRisk = node.leftNode.dev
                leftSplit = 0

        node.cp = (node.dev - (leftRisk + rightRisk)) / (leftSplit + rightSplit + 1)
        return leftSplit + rightSplit + 1, leftRisk + rightRisk
