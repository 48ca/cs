import sys

index = int(sys.argv[1])
i = index - index%3
i = i - i%27 + i%9
print(str(3*(i//27)+(i%9)//3))
