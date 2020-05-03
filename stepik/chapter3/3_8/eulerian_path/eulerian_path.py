f = open('dataset_317290_6.txt')
all_edges = [line.strip() for line in f.readlines()]
f.close()

# adjacency list representation of the Eulerian directed graph
unvisited_edges = {}

# construct adjacency list
for curr_edges in all_edges:
    outgoing_node = int(curr_edges.split()[0])
    incoming_nodes = [int(node) for node in curr_edges.split()[2].split(',')]
    unvisited_edges[outgoing_node] = incoming_nodes

# find the in-degree and out-degree for each node
# node_degrees maps a node -> (out-degree - in-degree)
# therefore, balanced nodes will have a value of 0
# the node with value 1 will be used as the start node for the Eulerian cycle (extra edge going out)
node_degrees = {}
for outgoing_node, incoming_nodes in unvisited_edges.items():
    # add to the value for the node with outgoing edges
    if outgoing_node in node_degrees:
        node_degrees[outgoing_node] += len(incoming_nodes)
    else:
        node_degrees[outgoing_node] = len(incoming_nodes)

    # subtract to the value for each of the nodes that the edge is directed toward
    for incoming_node in incoming_nodes:
        if incoming_node in node_degrees:
            node_degrees[incoming_node] -= 1
        else:
            node_degrees[incoming_node] = -1

# the start node has value 1
global_start_node = 0
for node, value in node_degrees.items():
    if value == 1:
        global_start_node = node

def find_path(old_path, unvisited_edges, unvisited_edges_in_path):

    if not old_path: # if this is our first path
        start_node = global_start_node # start at the start node for the entire path
    else: # otherwise
        # pick a node with an unvisited edge in our current path and start at that node
        start_node = list(unvisited_edges_in_path.keys())[0]
        
    new_path = [start_node]

    # keep following edges until we reach a dead end
    # note: we randomly choose to pick the first edge coming out of each node
    curr_node = start_node
    next_node = list(unvisited_edges[start_node])[0]

    while True: # we'll exit once we reach a dead end

        # remove curr_node -> next_node edge from unvisited_edges - since we are visiting it
        # if we are removing the only outgoing edge for curr_node, then remove curr_node from the unvisited_nodes dict
        if len(unvisited_edges[curr_node]) == 1:
            del(unvisited_edges[curr_node])
        else:
            unvisited_edges[curr_node].remove(next_node)

        # update unvisited_edges_in_path
        if curr_node in unvisited_edges: # if curr_node has any unvisited edges
            unvisited_edges_in_path[curr_node] = unvisited_edges[curr_node] # add them to unvisited_edges_in_path
        elif curr_node in unvisited_edges_in_path: # if curr_node NOW has no unvisited edges
            del(unvisited_edges_in_path[curr_node]) # remove it from unvisited_edges_in_path

        # add next node to path list
        new_path.append(next_node)

        # update curr_node and next_node
        curr_node = next_node

        if next_node in unvisited_edges: # if we still have more nodes to traverse in our path
            next_node = list(unvisited_edges[next_node])[0]
        else: # we've hit a dead end
            break

    # if this is our first path, just return the path we just made
    if not old_path:
        return new_path

    # we want to return our old path, but when we reach start_node in the old path
    # we want to go through the cycle we just created
    index_of_start = old_path.index(start_node)
    return old_path[:index_of_start] + new_path + old_path[(index_of_start + 1):]

path = []
# tracks the unvisited edges for only the nodes in our current path
# used to "backtrack" and go through any edges that we missed
unvisited_edges_in_path = {}

while (unvisited_edges): # while there are still unexplored edges in the graph
    # form a new path by picking a node with an unused edge in our current path,
    # then traversing a cycle starting at that node
    # then replacing that node with the cycle in our path
    path = find_path(path, unvisited_edges, unvisited_edges_in_path)
    
# print Eulerian path
first_node = True
for node in path:
    if first_node:
        print(node,end='')
        first_node = False
    else:
        print('->' + str(node), end='')

print('')