f = open('test.txt')
k = int(f.readline())
f.close()

# STEP 1: CONSTRUCT K-MER COMPOSITION (ALL POSSIBLE BINARY VALUES)

# generate all possible k-mers
max_value = (2 ** k) - 1 # maximum possible value with k bits

k_mers = []
for i in range(max_value + 1):
    binary_i = bin(i)[2:]
    # pad with zeroes on left end
    zero_padding = '0' * (k - len(binary_i))
    k_mers.append(zero_padding + binary_i)

# STEP 2: CONSTRUCT DE BRUIJN GRAPH OF K-MER COMPOSITION

# adjacency list representation of the De Bruijn graph
# for every k-mer
#   prefix -> suffix
unvisited_edges = {}

for k_mer in k_mers:
    prefix = k_mer[:-1]
    suffix = k_mer[1:]
    if prefix in unvisited_edges:
        unvisited_edges[prefix].append(suffix)
    else:
        unvisited_edges[prefix] = [suffix]

# STEP 3: FIND EULERIAN CYCLE IN DE BRUIJN GRAPH

# form a cycle by randomly walking in graph (don't visit the same edge twice!)
def findCycle(unvisited_edges, old_cycle):

    # select a node start_node in cycle with still unexplored edges
    if not old_cycle: # if it's our first cycle, we pick the first one in the unvisited_edges dict
        start_node = list(unvisited_edges.keys())[0]
    else:
        for explored_node in old_cycle:
            # if that node still has unexplored edges, set it as the start node
            if explored_node in unvisited_edges:
                start_node = explored_node
                break

    new_cycle = [start_node]

    # keep following the edges until we return to the start node
    # note: we randomly choose to pick the first edge coming out of each node
    curr_node = start_node
    next_node = list(unvisited_edges[start_node])[0]
    first_time_visiting_start_node = True
    while curr_node != start_node or first_time_visiting_start_node:
        first_time_visiting_start_node = False

        # remove curr_node -> next_node edge from unvisited_edges - since we are visiting it
        # if we are removing the only outgoing edge for curr_node, then remove curr_node from the unvisited_nodes dict
        if len(unvisited_edges[curr_node]) == 1:
            del(unvisited_edges[curr_node])
        else:
            unvisited_edges[curr_node].remove(next_node)

        # add next node to Cycle list
        new_cycle.append(next_node)

        # update curr_node and next_node
        curr_node = next_node

        # check if we've reached a dead end
        if next_node not in unvisited_edges: # we've reached a dead end
            continue
        next_node = list(unvisited_edges[next_node])[0]

    # if this our first cycle, we can simply return that cycle
    if not old_cycle:
        return new_cycle

    # we found our new cycle, but we must first traverse old cycle (starting at start_node)
    # unless if this is our first cycle
    index_of_start = old_cycle.index(start_node) 
    old_cycle = old_cycle[index_of_start:-1] + old_cycle[0:index_of_start]

    # and then we can traverse new_cycle after traversing old_cycle starting at start_node
    return old_cycle + new_cycle

cycle = []

while (unvisited_edges): # while there are still unexplored edges in Graph

    # form new cycle by traversing cycle (starting at a node in the current cycle with unexplored edges) 
    # and then randomly walking
    cycle = findCycle(unvisited_edges, cycle)

# STEP 3: RECONSTRUCT K-UNIVERSAL STRING FROM EULERIAN CYCLE
# we must chop off the ends to avoid double counting of the starting node
k_universal_string = ''

for i in range(0, len(cycle) - 1):
    k_universal_string += cycle[i][-1]

print(k_universal_string)