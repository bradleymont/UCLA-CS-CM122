f = open('dataset_317412_10.txt')
lastColumn = f.readline().strip()
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

# inverts BWT and returns original text
# start at $, and repeatedly find next characters
def invertBWT(firstColumn, lastColumn, firstColIndexToKey, lastColKeyToIndex):

    textLength = len(firstColumn)

    # start at the END_CHAR in the last column
    END_CHAR_key = END_CHAR + '_' + '1'
    lastColPos = lastColKeyToIndex[END_CHAR_key]

    result = ""

    currPosInLastCol = lastColPos
    while len(result) < textLength - 1:

        # get the character after the one at currPosInLastCol
        nextChar = firstColumn[currPosInLastCol]

        # add that character to the beginning of result
        result += nextChar

        # update currPosInLastCol
        key = firstColIndexToKey[currPosInLastCol]
        currPosInLastCol = lastColKeyToIndex[key]

    # add END_CHAR to the result
    result += END_CHAR

    return result

# STEP 1: obtain 1st column by sorting last column

firstColumn = ''.join(sorted(lastColumn))
END_CHAR = firstColumn[0] # usually $

# STEP 2: Map the k-th occurance of each character to its index to take advantage of First-Last rule
# and vice versa

firstColIndexToKey = mapOccurrences(firstColumn)[1]
lastColKeyToIndex = mapOccurrences(lastColumn)[0]

# STEP 3: Use First-Last rule to invert BWT
reconstructedString = invertBWT(firstColumn, lastColumn, firstColIndexToKey, lastColKeyToIndex)

print(reconstructedString)


