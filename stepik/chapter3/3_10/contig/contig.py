f = open('dataset_317292_5.txt')
kmers = [line.strip() for line in f.readlines()]
f.close()

###### STEP 1: CONSTRUCT DE BRUIJN GRAPH ######

# adjacency list representation of the de Bruijn graph
# for each k-mer:
#   prefix -> suffix
adjacency_list = {}
for kmer in kmers:
    prefix = kmer[:-1]
    suffix = kmer[1:]
    if prefix in adjacency_list:
        adjacency_list[prefix].append(suffix)
    else:
        adjacency_list[prefix] = [suffix]

###### STEP 1: FIND ALL MAXIMAL NON-BRANCHING PATHS IN DE BRUIJN GRAPH ######

# find in-degrees and out-degrees for each node

# node -> [in-degree,out-degree]
node_degrees = {}
for outgoing_node, incoming_nodes in adjacency_list.items():
    # increment the out-degree for outgoing_node by the number of incoming nodes
    if outgoing_node in node_degrees:
        node_degrees[outgoing_node][1] += len(incoming_nodes)
    else:
        node_degrees[outgoing_node] = [0, len(incoming_nodes)]

    # increment the in-degree for each incoming node by 1
    for incoming_node in incoming_nodes:
        if incoming_node in node_degrees:
            node_degrees[incoming_node][0] += 1
        else:
            node_degrees[incoming_node] = [1, 0]

# find maximal non-branching paths

# Paths ← empty list
paths = []

# for each node v in graph
for v in list(node_degrees.keys()):
    # if v is not a 1-in-1-out node
    if node_degrees[v] != [1,1]:
        # if out(v) > 0
        if node_degrees[v][1] > 0:
            # for each outgoing edge (v, w) from v
            for w in adjacency_list[v]:
                # NonBranchingPath ← the path consisting of single edge (v, w)
                non_branching_path = [v,w]
                # while w is a 1-in-1-out node
                while node_degrees[w] == [1,1]:
                    # extend NonBranchingPath by the edge (w, u)
                    u = adjacency_list[w][0]
                    non_branching_path.append(u)
                    # w ← u
                    w = u
                # add NonBranchingPath to the set Paths
                paths.append(non_branching_path)

# for each isolated cycle Cycle in Graph
#   add Cycle to Paths

# isolated cycles won't contain any of the nodes traversed in paths, so remove those nodes from our graph
for path in paths:
    for node in path:
        if node in adjacency_list:
            del adjacency_list[node]

# remove any nodes that aren't 1-in-1-out nodes
for node in list(adjacency_list.keys()):
    # if node isn't a 1-in-1-out node
    if node_degrees[node] != [1,1]:
        del adjacency_list[node]

# adjacency_list now consists of only 1-in-1-out nodes that weren't traversed in any of our other paths
# while adjacency_list is not empty
while adjacency_list:
    # select any node as the starting node for our cycle
    start_node = list(adjacency_list.keys())[0]
    
    curr_node = start_node
    next_node = adjacency_list[start_node][0]

    cycle = [start_node]

    first_time_visiting_start_node = True
    while curr_node != start_node or first_time_visiting_start_node:
        first_time_visiting_start_node = False

        # remove curr_node from adjacency_list
        del adjacency_list[curr_node]

        # add next_node to cycle
        cycle.append(next_node)

        # update curr_node and next_node
        curr_node = next_node

        # make sure we haven't reached a dead end
        if next_node not in adjacency_list:
            continue
        next_node = adjacency_list[next_node][0]
    
    # add our cycle to paths
    paths.append(cycle)

###### STEP 3: FORM CONTIGS FROM MAXIMAL NON-BRANCHING PATHS ######

contigs = []
for path in paths:
    contig = path[0] # add the entire first kmer to the contig
    for i in range(1, len(path)):
        contig += path[i][-1] # add the end of each kmer to the contig
    contigs.append(contig)

###### STEP 4: PRINT CONTIGS ######

for contig in contigs:
    print(contig, end=' ')
print('')
