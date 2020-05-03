f = open('dataset_317285_10.txt')
patterns = [line.strip() for line in f.readlines()]
f.close()

# adjacency list representation of overlap graph
# node -> list of adjacent nodes
overlap_graph = {}

# construct overlap graph
for curr_pattern in patterns:
    curr_suffix = curr_pattern[1:]
    for other_pattern in patterns:
        other_prefix = other_pattern[:-1]
        if (other_pattern != curr_pattern) and (curr_suffix == other_prefix):
            # add a directed edge curr_pattern -> other_pattern
            if curr_pattern in overlap_graph:
                overlap_graph[curr_pattern].append(other_pattern)
            else:
                overlap_graph[curr_pattern] = [other_pattern]
            
# print overlap graph
for node, adjacent_nodes in overlap_graph.items():
    print(node, end=" -> ")
    first_node = True
    for adjacent_node in adjacent_nodes:
        if first_node:
            print(adjacent_node, end="")
            first_node = False
        else: print(", " + adjacent_node, end="")
    print('')