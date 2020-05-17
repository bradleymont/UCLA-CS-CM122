f = open('dataset_317410_5.txt')
text = f.readline().strip()
f.close()

# STEP 1: form all cyclic rotations of text
bwtMatrix = []

for i in range(len(text)):
    currRotation = text[i:] + text[:i]
    bwtMatrix.append(currRotation)

# STEP 2: sort cyclic rotations
bwtMatrix.sort()

# STEP 3: extract last column from BWT matrix
bwt = ''.join(list(map(lambda row: row[-1], bwtMatrix)))

print(bwt)