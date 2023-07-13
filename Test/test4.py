import numpy as np
from numpy.ma import masked_array as mama

y = np.empty((3 , 4))

Ah = np.zeros((3 , 4))
Ahm = np.ma.array([[0 , 1 , 2 , 3]    ,  
       [4 , 5 , 6 , 7] , 
       [8 , 9 , 10 , 11]] , mask =  [[True , False , True , False] , 
       [True , False , True , False] , 
       [True , False , True , False]] , dtype = float)

Ahn = np.ma.array([[0 , 1 , 2 , 3] , 
       [4 , 5 , np.nan , 7] , 
       [8 , 9 , 10 , 11]])

print(Ahm)

x = 10.5
print(type(x))


Ahm = mama(Ahm , Ahm < 5)
print(Ahm + Ahn)

Ahm = Ahm.filled(np.nan)

print(Ahm)


# y.fill(np.nan)

print(y)

# print(Ah)
# print(Ahm.recordmask)
# Ahh = mama(np.zeros((3 , 4)))
# print(Ahh)
# Ahh = Ahm ** 2
# test = np.sum(Ahh[1, :4])
# print(Ahh)
# print(test)

# a = np.zeros(5)

# print(a)