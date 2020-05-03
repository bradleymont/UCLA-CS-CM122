f = open('rosalind_ini6.txt')
words = f.read().split()
f.close()

wordToFrequency = {}

for word in words:
    if word in wordToFrequency:
        wordToFrequency[word] += 1
    else:
        wordToFrequency[word] = 1

for word, frequency in wordToFrequency.items():
    print(word, frequency)