"""
    Main program for the CART implementation with pseudo delayed greedy splitting.
    This could be replaced with a user interface if need be.

    Using Python 3.6.1 for development.
"""

from print_tree import *
from tree_params import Params
from pypart_to_rpart import *
from make_cp_table import *
from CpTable import *
from xval import *

import sys
import random
import time
from os.path import splitext

#####
# Functions
#####
'''
    Prints a message on how to use from CMD or Terminal
'''
def printUsage():
    # add delayed param?
    print("Usage:\n    python pypart.py <data file (csv/xlsx)> <response> [optional: <delayed value {0,1}>]")


'''
    Validate and parse command line parameters
'''
def parseParams(argv):
    filename = str(argv[1])
    resp = argv[2]

    delay = 0
    if len(argv) > 3:
        delay = argv[3]

    if not (filename.endswith("csv") or filename.endswith("xlsx")):
        print("\nData file must be of type 'csv' or 'xlsx'.")
        print("Args: ", argv)
        printUsage()
        exit(0)

    return filename, resp, int(delay)


'''
    Builds the tree and returns the root node
'''
def buildTree(dataFrame, params):
    root = Node()
    root.numObs = len(dataFrame)
    root.data = dataFrame

    print("Building tree...")
    partition(root, 1, params)

    return root


'''
    Scale the complexity of each node by its deviance (risk)
'''
def fixTree(tree, cp_scale, nodeId, nodeCnt, inode):
    tree.cp *= cp_scale
    tree.nodeId = nodeId
    nodeCnt[0] += 1
    inode.append(nodeId)

    if tree.leftNode is not None:
        fixTree(tree.leftNode, cp_scale, 2 * nodeId, nodeCnt, inode)
    if tree.rightNode is not None:
        fixTree(tree.rightNode, cp_scale, (2 * nodeId) + 1, nodeCnt, inode)


'''
    Builds the CP table for the tree for pruning
'''
def buildCpTable(root, params):
    print("Building CP table...")

    # store params
    whereSave = list(params.where)
    cpList = [root.cp]
    uniqueCp = [2]
    parent = [root.cp]

    makeCpList(root, parent, cpList, uniqueCp)
    cpList.sort(reverse=True)       # sort the CP values largest to smallest
    # make doublely linked list
    cpTableHead = CpTable()
    currCpTable = cpTableHead
    prevCpTable = cpTableHead.back
    for cp in cpList:
        currCpTable.cp = cp
        if cp != cpList[len(cpList) - 1]:
            currCpTable.forward = CpTable()
        if prevCpTable is not None:
            currCpTable.back = prevCpTable
        prevCpTable = currCpTable
        currCpTable = currCpTable.forward
    cpTableTail = prevCpTable

    makeCpTable(root, root.cp, 0, cpTableTail)

    if params.xval > 1:
        # a vector of length "numObs" assigning each row in the original data frame to one of the cross-validation df's
        xGroups = []
        for _ in range(0, len(root.data)):
            xGroups.append(random.randint(1, params.xval))
        params.xval = len(set(xGroups))     # update # of xvals depending on how many groups are formed randomly

        # do cross validations
        xval(cpTableHead, xGroups, root.data, params)

    tempCp = cpTableHead
    scale = 1 / root.dev
    while tempCp is not None:
        tempCp.cp *= scale
        tempCp.risk *= scale
        tempCp.xstd *= scale
        tempCp.xrisk *= scale
        tempCp = tempCp.forward
    cpTableHead.risk = 1.0      # 0 otherwise

    params.where = whereSave
    return cpTableHead


'''
    Create csv file(s) to be imported into R making this tree an Rpart tree.

    baseFilename = string before the '.' in the data file's name
'''
def pypartToRpart(root, baseFilename, cpTable, where):
    print("Creating pypart to rpart CSV files...")

    frameFilename = baseFilename + ".frame.csv"
    writeFrameCSV(root, frameFilename)

    cpFilename = baseFilename + ".cptable.csv"
    writeCPTableCSV(cpTable, cpFilename)

    whereFilename = baseFilename + ".where.csv"
    writeWhereCSV(where, whereFilename)

    splitFilename = baseFilename + ".splits.csv"
    writeSplitCsv(root, splitFilename)


#####
#   Run the whole process
#####
def pypart_run(args):
    if len(args) < 3:
        printUsage()
        exit(0)
    dataFilename, response, delayed = parseParams(args)

    outputFilename = splitext(dataFilename)[0] + ".tree"
    if delayed > 0:
        outputFilename += ".delayed"

    df = getDataFrameFromCSV(dataFilename)
    if not str(response) in df.columns:
        print("\nResponse variable not in data frame.")
        print("Args: ", args)
        printUsage()
        exit(0)

    # max node = 2^(d+1) - 1, where d = depth
    maxDepth = 30
    maxNodes = (2 ** (maxDepth + 1)) - 1
    minObs = 20
    minNode = 7
    xVal = 10
    params = Params(maxNodes, minObs, response, minNode, maxDepth, delayed, xVal, len(df))

    # this is how it's done in rpart.c as well (build tree -> build CP table)
    tree = buildTree(df, params)
    cpTableHead = buildCpTable(tree, params)
    count = [0]
    inode = []
    fixTree(tree, (1 / tree.dev), 1, count, inode)
    count = count[0]

    for i in range(0, len(df)):
        k = params.where[i]
        while True:
            j = 0
            while j < count:
                if inode[j] == k:
                    params.where[i] = j + 1
                j += 1
            k /= 2
            if j >= count:
                break

    # TESTED: CPs are equal with rpart cps (if cp = 0.0 as param)
    # xrisk = xerror, risk = rel error, xstd = xstd
    # tempCp = cpTableHead
    # while tempCp is not None:
    #     print(tempCp.cp, tempCp.nsplit, tempCp.risk, tempCp.xrisk, tempCp.xstd)
    #     tempCp = tempCp.forward

    printTree(tree, outputFilename)
    pypartToRpart(tree, splitext(dataFilename)[0], cpTableHead, params.where)

    return cpTableHead


#####
# Main Function
#####
if __name__ == "__main__":
    start_time = time.time()
    pypart_run(sys.argv)
    print("Time elapsed:", str(time.time() - start_time), "seconds.")
    print("Done.")
