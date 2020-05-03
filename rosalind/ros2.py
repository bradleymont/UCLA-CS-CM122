f = open('rosalind_ini3.txt')
s = f.readline().strip()
a,b,c,d = f.readline().split()
f.close()

print(s[int(a):(int(b) + 1)], end=" ")
print(s[int(c):(int(d) + 1)], end="")