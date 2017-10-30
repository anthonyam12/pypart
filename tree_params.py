class Params(object):
    def __init__(self, maxNodes, minObs, response, minNode, maxDepth, delay, xval, numObs):
        self.maxNodes = maxNodes
        self.minObs = minObs
        self.response = response
        self.minNode = minNode      # minimum number of observations for terminal node
        self.maxDepth = maxDepth
        self.delayed = delay
        self.xval = xval
        self.iscale = 0
        self.where = [1 for _ in range(0, numObs)]
