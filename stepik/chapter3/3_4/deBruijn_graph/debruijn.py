f = open('dataset_317286_6.txt')
k = int(f.readline())
Text = f.readline().strip()
f.close()

# the De Bruijn graph for Text in adjacency list form
# the nodes are all the (k - 1)-mers of Text
# (k - 1)-mer -> adjacent (k - 1)-mers
de_bruijn_graph = {}

# construct De Bruijn Graph
for i in range(len(Text) - k + 1):
    k_mer = Text[i:(i+k)]
    prefix = k_mer[:-1]
    suffix = k_mer[1:]
    # add an edge (prefix of k-mer) -> (suffix of k-mer)
    if prefix in de_bruijn_graph:
        de_bruijn_graph[prefix].append(suffix)
    else:
        de_bruijn_graph[prefix] = [suffix]

# print De Bruijn Graph
for node, adjacent_nodes in de_bruijn_graph.items():
    print(node, end=' -> ')

    first_item = True
    for adjacent_node in adjacent_nodes:
        if first_item:
            print(adjacent_node, end='')
            first_item = False
        else:
            print(',' + adjacent_node, end='')
    print('')