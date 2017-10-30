"""
    Print the tree created from the recursive partitioning
"""

'''
    Prints the tree
'''
def printTree(root, filename):
    print("Creating tree file '" + filename + "'...")
    file = open(filename, "w")

    # print description
    file.write("node) split, number observations, deviance, yval\n\t* denotes a terminal node\n\n")

    # print root node
    devYbar = "%.5f %.5f" % (root.dev, root.yval)
    printStr = '1' + ") root " + str(root.numObs) + " " + devYbar + "\n"
    file.write(printStr)

    if root.leftNode is not None:
        printSubTree(root.leftNode, 2, 1, root, False, file)
    if root.rightNode is not None:
        printSubTree(root.rightNode, 3, 1, root, True, file)

    file.close()


'''
    Recursive function to print the tree
'''
def printSubTree(node, nodeId, myDepth, parent, right, file):
    printNode(node, nodeId, myDepth, parent, right, file)

    if node.leftNode is not None:
        printSubTree(node.leftNode, (2 * nodeId), myDepth + 1, node, False, file)
    if node.rightNode is not None:
        printSubTree(node.rightNode, (2 * nodeId) + 1, myDepth + 1, node, True, file)


'''
    Outputs the data for a single node
'''
def printNode(node, nodeId, depth, parentNode, right, file):
    tabStr = ''
    for _ in range(0, depth):
        tabStr += '\t'

    # left == 'yes'
    direction = parentNode.direction
    if right:
        direction *= -1

    if direction < 0:  # < x go left
        directionStr = "<"
    else:  # > x go left
        directionStr = ">"

    if right:
        directionStr += '='
    else:
        directionStr += ' '

    terminalStr = ''
    if node.leftNode is None and node.rightNode is None:
        terminalStr += '*'

    devYbar = "%.5f %.5f" % (node.dev, node.yval)
    printStr = tabStr + str(nodeId) + ")" + " " + parentNode.varName + directionStr + str(parentNode.splitPoint) + " " \
               + str(node.numObs) + " " + " " + devYbar + " " + terminalStr + "\n"
    # print(printStr)
    file.write(printStr)
