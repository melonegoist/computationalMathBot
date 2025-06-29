import random

file = open("..data/random_data/random_matrix.txt", mode="w")
N = int(input("Enter matrix size: "))
file.write(str(N))

for i in range(N**2):
    if (i % N == 0):
        file.write("\n")

    if (i+1)%N == 0:
        endpoint = ""
    else:
        endpoint = " "

    file.write(str(random.randint(-100, 100)) + endpoint)

file.close()
