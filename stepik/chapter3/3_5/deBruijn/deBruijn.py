f = open('dataset_317287_8.txt')
Patterns = [line.strip() for line in f.readlines()]
f.close()

# adjacency list representation of the De Bruijn graph
# for every k-mer
#   prefix -> suffix
de_bruijn = {}

# construct De Bruijn graph
for k_mer in Patterns:
    prefix = k_mer[:-1]
    suffix = k_mer[1:]
    if prefix in de_bruijn:
        de_bruijn[prefix].append(suffix)
    else:
        de_bruijn[prefix] = [suffix]

# print De Bruijn graph
for node, adjacent_nodes in de_bruijn.items():
    print(node, end=' -> ')

    first_item = True
    for adjacent_node in adjacent_nodes:
        if first_item:
            print(adjacent_node, end='')
            first_item = False
        else:
            print(',' + adjacent_node, end='')
    print('')