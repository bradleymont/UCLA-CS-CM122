f = open('dataset_317284_3.txt')
k = int(f.readline())
Text = f.readline().strip()
f.close()

for i in range(len(Text) - k + 1):
    print(Text[i:(i + k)])
