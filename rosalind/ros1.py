f = open('rosalind_dna.txt')
DNA_string = f.read().strip()
f.close()

for i in 'ACG':
    print(DNA_string.count(i), end=" ")

print(DNA_string.count('T'), end="")