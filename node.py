class Node(object):
    def __init__(self):
        # nodes
        self.leftNode = None
        self.rightNode = None

        self.nodeId = 0
        self.splitPoint = 0.0
        self.splitIndex = 0     # this is actually (x[index] + x[index + 1]) / 2
        self.direction = 0
        self.varName = ''

        self.cp = 0.0
        self.numObs = 0
        self.dev = 0.0
        self.yval = 0.0
        self.ncompete = 0
        self.nsurrogate = 0
        self.improvement = 0

        # data frames=
        self.data = None
        self.response = ''

    def print(self):
        output = "split point: " + str(self.splitPoint) + "\nvarName: " + str(self.varName) \
                 + "\ncp: " + str(self.cp) + "\nnumObs: " + str(self.numObs) + "\n"
        print(output)

    def printLeft(self):
        self.leftNode.print()

    def printRight(self):
        self.rightNode.print()
