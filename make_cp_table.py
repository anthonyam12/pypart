"""
    The functions in this file will be used to build the cp table similar to the one built with rpart.
"""

'''
    Prior to building the CP table we build a sorted list of CP values
'''
def makeCpList(node, parentCp, cpList, uniqueCp):
    if node.cp > parentCp[0]:
        node.cp = parentCp[0]

    meCp = [node.cp]
    if node.leftNode is not None:
        makeCpList(node.leftNode, meCp, cpList, uniqueCp)
        makeCpList(node.rightNode, meCp, cpList, uniqueCp)

    if meCp[0] < parentCp[0]:
        if meCp[0] in cpList:
            return
        cpList.append(meCp[0])
        uniqueCp[0] += 1

'''
    Function responsible for building the CP table
'''
def makeCpTable(node, parentCp, nsplit, cpTail):
    if node.leftNode is not None:
        makeCpTable(node.leftNode, node.cp, 0, cpTail)
        cpTable = makeCpTable(node.rightNode, node.cp, nsplit + 1, cpTail)
    else:
        cpTable = cpTail

    while cpTable.cp < parentCp:
        cpTable.risk += node.dev
        cpTable.nsplit += nsplit
        cpTable = cpTable.back

    return cpTable
