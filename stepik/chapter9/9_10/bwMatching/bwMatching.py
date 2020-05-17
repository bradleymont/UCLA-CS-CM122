f = open('dataset_317413_8.txt')
lastColumn = f.readline().strip()
Patterns = f.readline().strip().split()
f.close()

END_CHAR = None # character to indicate the end of the string (usually $)

# returns an dictionary that maps 
# a character and k => the index of the k-th occurance of character in s
# example: A_3 => 5 means that the 3rd occurance of A in s is at index 5
# ALSO, returns the inverse of this map
def mapOccurrences(s):
    occurrenceToIndex = {}
    indexToOccurrence = {}

    # maps each character to the amount of occurrences so far in the string
    charCounts = {}
    
    for i in range(len(s)):
        currChar = s[i]

        # get k (where currChar is the k-th occurrence of that character)
        k = 1
        if currChar in charCounts:
            k = charCounts[currChar] + 1

        # make the key and update maps
        occurenceKey = currChar + '_' + str(k)
        occurrenceToIndex[occurenceKey] = i
        indexToOccurrence[i] = occurenceKey

        # update charCounts
        if currChar in charCounts:
            charCounts[currChar] += 1
        else:
            charCounts[currChar] = 1

    return occurrenceToIndex, indexToOccurrence

# returns the topIndex and bottomIndex that a symbol occurs at in a column
def findSymbolInterval(symbol, column, offset):
    top = 0
    bottom = len(column) - 1

    topIndex = bottomIndex = None

    foundTop = foundBottom = False

    while top <= bottom:

        # check top
        if column[top] == symbol and not foundTop:
            topIndex = top + offset
            foundTop = True

        # check bottom
        if column[bottom] == symbol and not foundBottom:
            bottomIndex = bottom + offset
            foundBottom = True

        # if we found both, exit loop
        if foundTop and foundBottom:
            break

        # only update pointers if we haven't found symbol yet
        if not foundTop:
            top += 1
        if not foundBottom:
            bottom -= 1

    return topIndex, bottomIndex

# takes the index of a symbol in the last column, and returns the index of the corresponding
# symbol in the first column
def LastToFirst(lastColIndex, firstColKeyToIndex, lastColIndexToKey):
    key = lastColIndexToKey[lastColIndex]
    firstColIndex = firstColKeyToIndex[key]
    return firstColIndex

# returns the # of times that Pattern occurs in Text
def BWMatching(lastColumn, Pattern, firstColKeyToIndex, lastColIndexToKey):
    top = 0
    bottom = len(lastColumn) - 1

    while top <= bottom:

        # if Pattern is nonempty
        if Pattern:
            # symbol ← last letter in Pattern
            symbol = Pattern[-1]

            # remove last letter from Pattern
            Pattern = Pattern[:-1]

            # if positions from top to bottom in lastColumn contain an occurrence of symbol
            topIndex, bottomIndex = findSymbolInterval(symbol, lastColumn[top:(bottom + 1)], top)
            if topIndex != None:
                # topIndex ← first position of symbol among positions from top to bottom in lastColumn
                # bottomIndex ← last position of symbol among positions from top to bottom in lastColumn

                # top ← LastToFirst(topIndex)
                top = LastToFirst(topIndex, firstColKeyToIndex, lastColIndexToKey)

                # bottom ← LastToFirst(bottomIndex)
                bottom = LastToFirst(bottomIndex, firstColKeyToIndex, lastColIndexToKey)

            else:
                return 0
        else:
            return bottom - top + 1

# STEP 1: obtain 1st column by sorting last column

firstColumn = ''.join(sorted(lastColumn))
END_CHAR = firstColumn[0] # usually $

# STEP 2: Map the k-th occurance of each character to its index to take advantage of First-Last rule
# and vice versa

firstColKeyToIndex = mapOccurrences(firstColumn)[0]
lastColIndexToKey = mapOccurrences(lastColumn)[1]

# STEP 3: use BWMatching to find the # of matches for each pattern

for Pattern in Patterns:
    print(BWMatching(lastColumn, Pattern, firstColKeyToIndex, lastColIndexToKey), end=" ")
print()
