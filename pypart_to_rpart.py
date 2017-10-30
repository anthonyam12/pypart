"""
    Creates the requisite amount of csv files so one can import these files into R. This will allow the user to compare
    rpart trees and pypart trees using native rpart functions.
"""
import csv

'''
    Write CSV file that will mimic the rpart.tree$frame dataframe when imported to R.
    To put the rows in the correct order we traverse the tree from left to right.

    TESTED: was able to import into R with the command below, seems to work

    From R: read.csv("<framefilename>", headers=True, row.names=1)
'''
def writeFrameCSV(root, frameFilename):
    # initialize csv list with headers and root node information
    csvList = [["", "var", "n", "wt", "dev", "yval", "complexity", "ncompete", "nsurrogate"],
               [1, root.varName, root.numObs, root.numObs, root.dev, root.yval, root.cp, root.ncompete,
                root.nsurrogate]]

    # write frame CSV
    if root.leftNode is not None:
        appendNodeFrameLine(root.leftNode, 2, csvList)
    if root.rightNode is not None:
        appendNodeFrameLine(root.rightNode, 3, csvList)

    with open(frameFilename, "w") as csvFile:
        writer = csv.writer(csvFile, lineterminator='\n')
        writer.writerows(csvList)

'''
    Recursively traverse tree and add each node's information to the CSV list
'''
def appendNodeFrameLine(node, nodeId, frameList):
    varName = node.varName
    if node.leftNode is None and node.rightNode is None:
        varName = "<leaf>"

    frameList.append([nodeId, varName, node.numObs, node.numObs, node.dev, node.yval, node.cp, node.ncompete,
                      node.nsurrogate])

    if node.leftNode is not None:
        appendNodeFrameLine(node.leftNode, (2 * nodeId), frameList)
    if node.rightNode is not None:
        appendNodeFrameLine(node.rightNode, (2 * nodeId) + 1, frameList)

'''
    Write CSV file that will mimic the rpart.tree$cptable dataframe.

    From R: read.csv("<cptableFilename>", headers=True, row.names=1)
'''
def writeCPTableCSV(cpTableHead, cptableFilename):
    # initialize csv list with headers and root node information
    csvList = [["", "CP", "nsplit", "rel error", "xerror", "xstd"]]

    tempCp = cpTableHead
    i = 1
    while tempCp is not None:
        cp = tempCp.cp
        nsplit = tempCp.nsplit
        relError = tempCp.risk
        xerror = tempCp.xrisk
        xstd = tempCp.xstd
        csvList.append([i, cp, nsplit, relError, xerror, xstd])

        tempCp = tempCp.forward
        i += 1

    with open(cptableFilename, "w") as csvFile:
        writer = csv.writer(csvFile, lineterminator='\n')
        writer.writerows(csvList)


'''
    Write the CSV file to mimic the rpart tree's 'where' dataframe.

    which = vector of final node numbers for each input obs

    From R file docs:
        Where is a vector of values (one per row in the original data frame) matching the node
        number that each row will end up in with the node in the tree... For example, the cars.csv
        file has 398 rows and a tree with cp=0 will produce 35 leaves, in this case where would have
        names(tree$where) <- 1:398 and length(unique(tree$where)) = 35, each entry in tree$where would be
        the node each value ends in so tree$where[1] will h
'''
def writeWhereCSV(where, whereFilename):
    csvList = [["name", "node"]]

    i = 1
    for val in where:
        csvList.append([i, val])
        i += 1

    with open(whereFilename, "w") as csvFile:
        writer = csv.writer(csvFile, lineterminator='\n')
        writer.writerows(csvList)


'''
    Write a CSV file for the all the splits, mimics an rpart tree's 'split' dataframe
'''
def writeSplitCsv(root, splitFilename):
    csvList = [["name", "count", "ncat", "improve", "index", "adj"],
               [root.varName, root.numObs, root.direction, root.improvement, root.splitPoint, 0]]

    # ncat = direction for continous, adj = ??? (0 for cars in rpart) name = split var name,
    # count = # obs in node, improve = improvement, index = split point
    if root.leftNode is not None:
        appendSplitNode(root.leftNode, csvList)
    if root.rightNode is not None:
        appendSplitNode(root.rightNode, csvList)

    with open(splitFilename, "w") as csvFile:
        writer = csv.writer(csvFile, lineterminator='\n')
        writer.writerows(csvList)

'''
    Recursively walk through the tree, adding node information as we go
'''
def appendSplitNode(node, lst):
    varname = node.varName
    count = node.numObs
    ncat = node.direction
    improve = node.improvement
    index = node.splitPoint
    adj = 0

    terminal = node.rightNode is None and node.leftNode is None

    if not terminal:
        lst.append([varname, count, ncat, improve, index, adj])
        if node.leftNode is not None:
            appendSplitNode(node.leftNode, lst)
        if node.rightNode is not None:
            appendSplitNode(node.rightNode, lst)
