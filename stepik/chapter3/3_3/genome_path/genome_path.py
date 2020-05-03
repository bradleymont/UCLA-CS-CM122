f = open('dataset_317285_3.txt')
k_mers = [line.strip() for line in f.readlines()]
f.close()

genome = k_mers[0]

for i in range(1, len(k_mers)):
    genome += k_mers[i][-1] # add the last symbol of the current k-mer to the genome

print(genome)