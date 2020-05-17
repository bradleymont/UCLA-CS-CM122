f = open('dataset_317406_8.txt')
text = f.readline().strip()
patterns = [line.strip() for line in f.readlines()]
f.close()

# returns the terminal node of the edge from currentNode to currentSymbol if one exists
# returns None if one doesn't exist
def findEdge(trie, currentNode, currentSymbol):
    outgoingEdges = trie[currentNode] # list of edges, each represented as [terminal node, edge label]
    for currEdge in outgoingEdges:
        currEdgeLabel = currEdge[1]
        # we found an outgoing edge to currentSymbol
        if currEdgeLabel == currentSymbol:
            # return the terminal node of the edge
            return currEdge[0]

    return None # no edges found

# takes in a list of patterns and returns a trie
def formTrie(patterns):
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
            nextNode = findEdge(trie, currentNode, currentSymbol)
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
    return trie

# returns true if any of the strings in the trie match a prefix of string s
def prefixTrieMatch(s, trie):
    endOfS = False

    # symbol ← first letter of s
    pos = 0
    symbol = s[pos]
    # v ← root of trie
    v = 0
    while True:
        # if v is a leaf in trie (leaves in the trie map to [])
        if not trie[v]:
            # then we've reached the end of a string in trie that matches a prefix of string s
            return True
        # if v isn't a leaf and we've reached the end of s - no match found
        elif endOfS:
            return False
        w = findEdge(trie, v, symbol)
        # else if there is an edge (v, w) in trie labeled by symbol
        if w:
            # symbol ← next letter of Text
            pos += 1

            if pos < len(s):
                symbol = s[pos]
            else:
                endOfS = True

            # v ← w
            v = w
        else:
            # no matches found
            return False

# returns the starting indices where a string in the trie appears as a substring of one of the suffixes of test
def trieMatch(text, trie):
    startIndices = []
    # for eachh suffix of text
    for start in range (len(text) - 1):
        suffix = text[start:]
        # if there exists a string in the trie that matches a prefix of the suffix of text starting at "start"
        if prefixTrieMatch(suffix, trie):
            # add that as a matching start index
            startIndices.append(start)

    return startIndices

# STEP 1: form a trie from patterns 
trie = formTrie(patterns)

# STEP 2: use trie matching to find all starting positions in text where a string from patterns appears as a substring
indices = trieMatch(text, trie)

print(' '.join(map(str, indices)))
