from asyncio.windows_events import NULL
import time
import numpy as np
from multiprocessing import Pool

# X = {}
# X = dict()
# X.update({'test' : 1})
# X.update({'test2' : 2})

# X = {1 , 2}
# X = set(((1 , 2) , 2))
# X.add(3)
# print(X)

# Y = [1 , 2 , 3]
# print(0 in Y)

# a = [1 , 2 , 3]
# a.append(4)
# print(a)

# x = np.array([0 , 1 , 2])
# print(x)
# x = list(x)
# print(x)

# X = np.array([[[np.nan , 1 , 2 , 3] , [4 , 5 , 6 , 7] , [8 , 9 , 10 , 11]] , [[0 , 1 , 2 , 3] , [4 , 5 , 6 , 7] , [8 , 9 , 10 , 11]]])
# print(X)
# print(np.nansum((X > 2) | (X < 1)))

# print(X[: , 0 , :])
# print(np.sum(X , axis = (0)).shape)

# for i , x in enumerate(np.arange(0.1, 1.01, 0.1)):
#     print(i , x)


# # 計算數值平方的函數
# def f(x):
#     return x*x

# def main():
#     # 建立含有 4 個工作者行程的 Pool
#     with Pool(processes=4) as p:
#         # 以 map 平行計算數值的平方
#         x = p.map(f, range(10000000) , chunksize=100000)
#         print(x)

# if __name__ == '__main__':
#     start = time.time()
#     main()
#     end = time.time()
#     print(f'Runtime: {end - start} sec(s)')

# p = 1000000000000000000000000000000
# q = 1000000000000000000000000000000

# print(id(p) , id(q))
time_start = time.time()
print(0 is None)

time_end = time.time()

print(time_end - time_start)
# print(p is q)