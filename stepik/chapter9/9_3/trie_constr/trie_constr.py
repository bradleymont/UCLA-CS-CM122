f = open('dataset_317406_4.txt')
patterns = [line.strip() for line in f.readlines()]
f.close()

# returns the terminal node of the edge from currentNode to currentSymbol if one exists
# returns None if one doesn't exist
def findEdge(currentNode, currentSymbol):
    outgoingEdges = trie[currentNode] # list of edges, each represented as [terminal node, edge label]
    for currEdge in outgoingEdges:
        currEdgeLabel = currEdge[1]
        # we found an outgoing edge to currentSymbol
        if currEdgeLabel == currentSymbol:
            # return the terminal node of the edge
            return currEdge[0]

    return None # no edges found

# adjacency list representation of a trie
# maps an initial node # to its outgoing edges
# where an outgoing edge is represented as [terminal node, edge label]
# assume the root is node 0
trie = {0: []}

# the number of the next node to get added to the trie
newNodeNum = 1

# for each string Pattern in Patterns
for pattern in patterns:
    # currentNode = root
    currentNode = 0
    for currentSymbol in pattern:
        nextNode = findEdge(currentNode, currentSymbol)
        # if there is an outgoing edge from currentNode with label currentSymbol
        if nextNode:
            currentNode = nextNode
        else:
            # add a new node newNode to Trie
            trie[newNodeNum] = []

            # add a new edge from currentNode to newNode with label currentSymbol
            trie[currentNode].append([newNodeNum, currentSymbol])

            # currentNode ← newNode
            currentNode = newNodeNum

            # update newNodeNum
            newNodeNum += 1

# print the trie
for initialNode, edges in trie.items():
    for edge in edges:
        terminalNode = edge[0]
        label = edge[1]
        print(str(initialNode) + "->" + str(terminalNode) + ":" + label)
