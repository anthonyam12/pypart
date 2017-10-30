class CpTable(object):
    def __init__(self):
        self.cp = 0
        self.risk = 0
        self.xrisk = 0
        self.xstd = 0
        self.nsplit = 0

        # cp tables
        self.forward = None
        self.back = None
