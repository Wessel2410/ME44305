import numpy as np
Amount_of_Holdup = []
from KevinTest_integrate import Sim

for i in range(10):
    Res = Sim()
    if i == 0:
        Amount_of_Holdup.append(Res)
        Last = Amount_of_Holdup[-1]
    else:
        Amount_of_Holdup.append(Res-Last)
        Last = Res
        
print(Amount_of_Holdup)
Array = np.array(Amount_of_Holdup)
print(Array.mean())
print(Array.std())