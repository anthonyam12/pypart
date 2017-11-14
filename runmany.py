"""
    Runs the pypart script many times and produces and average R^2 value.
"""

from pypart import *
import sys

'''
    Print usage
'''
def usage():
    print("Usage:")
    print("\tpython runmany.py <data file (csv/xlsx)> <response> <delayed value {0,1}> <number runs>")


"""
    Parse command line paramaters.
"""
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
    Runs the program.
'''
def run(iters, args):
    avgR2 = 0
    iters = int(iters)
    pruneCps = []
    for i in range(iters):
        print("\nIteration " + str(i) + " out of " + str(iters) + "...")
        startTime = time.time()
        cpTableHead = pypart_run(args)
        minXError = 9999999999
        minRelError = 99999999
        prunecp = 0
        print("Time elapsed:", str(time.time() - startTime), "seconds.")

        # TESTED: CPs are equal with rpart cps (if cp = 0.0 as param)
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
        printUsage()
        exit(0)
    iterations = sys.argv[len(sys.argv) - 1]
    dataFilename, response, delayed = parseParams(sys.argv)
    r2, pruneCp = run(iterations, sys.argv[:-1])

    print("\nTotal Time elapsed:", str(time.time() - start_time), "seconds.")
    print("Done.")
    print("Prune CPs: " + str(pruneCp) + ".\n")
    print("\nAverage R^2 over " + str(iterations) + " iterations: " + str(r2) + "\n")
