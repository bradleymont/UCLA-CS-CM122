f = open('rosalind_ini5.txt')
even_lines = f.readlines()[1::2] # slicing: [start:end(exclusive):step_size]
f.close()

print(''.join(even_lines))