import time

with open('tx.txt', 'r') as file:
    f = [x.strip().split(':') for x in file.readlines()]
    f = [x + x[1].split('@') for x in f]
    f = [[x[0]] + x[2:] for x in f]

    x = [','.join(['http'] + [x[3]] + [x[1]]+ [x[0]] + [x[2]] + ['https://proxy-seller.io/,0000000'] + ['1686119577']) for x in f]
    for i in x:
        print(i, end='\n')