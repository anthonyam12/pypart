"""
    Runs the pypart script many times and produces and average R^2 value.
"""

from pypart import *
import sys
import copy


def copyTree(root):
    iTree = copy.deepcopy(root)
    if root.leftNode is not None:
        copySubTree(root.leftNode, iTree.leftNode)
    if root.rightNode is not None:
        copySubTree(root.rightNode, iTree.leftNode)

    return iTree

'''
    Recursive function to print the tree
'''
def copySubTree(node, iTree):
    iTree = copy.deepcopy(node)
    if node.leftNode is not None:
        copySubTree(node.leftNode, iTree.leftNode)
    if node.rightNode is not None:
        copySubTree(node.rightNode, iTree.rightNode)


'''
    Print usage
'''
def usage():
    print("Usage:")
    print("\tpython runmany.py <data file (csv/xlsx)> <response> <delayed value {0,1}> <number runs>")


'''
    Runs the program.
'''
def run(iters, args):
    datafilename, resp, delay = parseParams(args)
    df = getDataFrameFromCSV(datafilename)
    if not str(resp) in df.columns:
        print("\nResponse variable not in data frame.")
        print("Args: ", args)
        usage()
        exit(0)

    # max node = 2^(d+1) - 1, where d = depth
    maxDepth = 30
    maxNodes = (2 ** (maxDepth + 1)) - 1
    minObs = 20
    minNode = 7
    xVal = 10
    params = Params(maxNodes, minObs, resp, minNode, maxDepth, delay, xVal, len(df))
    tree = buildTree(df, params)

    # run the cross validations and calc R^2 a set number of times
    avgR2 = 0
    pruneCps = []
    iters = int(iters)
    for i in range(iters):
        iTree = copyTree(tree)
        print("\nIteration " + str(i) + " out of " + str(iters) + "...")
        minXError = 9999999999
        minRelError = 99999999
        prunecp = 0

        # do cross validations
        cpTableHead = buildCpTable(iTree, params)

        # xrisk = xerror, risk = rel error, xstd = xstd
        tempCp = cpTableHead
        while tempCp is not None:
            if tempCp.xrisk < minXError:
                minXError = tempCp.xrisk
                minRelError = tempCp.risk
                prunecp = tempCp.cp
            tempCp = tempCp.forward

        avgR2 += (1 - minRelError)
        pruneCps.append(prunecp)

    return (avgR2 / iters), pruneCps


'''
    If run from the command line.
'''
if __name__ == "__main__":
    start_time = time.time()
    if len(sys.argv) < 4:
        usage()
        exit(0)
    iterations = sys.argv[len(sys.argv) - 1]
    r2, pruneCp = run(iterations, sys.argv[:-1])

    print("\nTotal Time elapsed:", str(time.time() - start_time), "seconds.")
    print("Done.")
    print("Prune CPs: " + str(pruneCp) + ".\n")
    print("\nAverage R^2 over " + str(iterations) + " iterations: " + str(r2) + "\n")
