import numpy as np
Amount_of_Holdup_base = []
Amount_of_Holdup_inn = []
from KevinTest_integrate import Sim
from InnovationCase_integrate import Sim2
import matplotlib.pyplot as plt

Total_bat_base = []
Total_warn_base = []
Total_charge_base = []
Total_cont_base = []

Total_bat_inn = []
Total_warn_inn = []
Total_charge_inn = []
Total_cont_inn = []

num_sim = 300

for i in range(num_sim):
    zero_hold, tot_bat, tot_warn, tot_charge, tot_con = Sim()
    if i == 0:
        Amount_of_Holdup_base.append(zero_hold)
        Last_hold = Amount_of_Holdup_base[-1]
        Total_bat_base.append(tot_bat)
        Total_warn_base.append(tot_warn)
        Total_charge_base.append(tot_charge)
        Total_cont_base.append(tot_con)
    else:
        Amount_of_Holdup_base.append(zero_hold-Last_hold)
        Last_hold = zero_hold
        Total_bat_base.append(tot_bat)
        Total_warn_base.append(tot_warn)
        Total_charge_base.append(tot_charge)
        Total_cont_base.append(tot_con)
    print(f"Sim {i+1}/{num_sim} done")

for j in range(num_sim):
    zero_hold, tot_bat, tot_warn, tot_charge, tot_con = Sim2()
    if j == 0:
        Amount_of_Holdup_inn.append(zero_hold)
        Last_hold = Amount_of_Holdup_inn[-1]
        Total_bat_inn.append(tot_bat)
        Total_warn_inn.append(tot_warn)
        Total_charge_inn.append(tot_charge)
        Total_cont_inn.append(tot_con)
    else:
        Amount_of_Holdup_inn.append(zero_hold-Last_hold)
        Last_hold = zero_hold
        Total_bat_inn.append(tot_bat)
        Total_warn_inn.append(tot_warn)
        Total_charge_inn.append(tot_charge)
        Total_cont_inn.append(tot_con)
    print(f"Sim2 {j+1}/{num_sim} done")



print(Amount_of_Holdup_base)
print(Total_bat_base)
print(Total_warn_base)
print(Total_charge_base)
print(Total_cont_base)
#print(Amount_of_Holdup_inn)
Array_holdup_base = np.array(Amount_of_Holdup_base)
Array_holdup_inn = np.array(Amount_of_Holdup_inn)
Array_Bat_base = np.array(Total_bat_base)
Array_Warn_base = np.array(Total_warn_base)
Array_Charge_base = np.array(Total_charge_base)
Array_Cont_base = np.array(Total_cont_base)
Array_Bat_inn = np.array(Total_bat_inn)
Array_Warn_inn = np.array(Total_warn_inn)
Array_Charge_inn = np.array(Total_charge_inn)
Array_Cont_inn = np.array(Total_cont_inn)
#print(Array.mean())
#print(Array.std())


print("\n\nResults between simulations")
print(f"Mean waiting time: \nBase case: {Array_holdup_base.mean()}\nInnovation case: {Array_holdup_inn.mean()}")

fig1 = plt.figure(figsize=(10,10))
plt.hist(Array_holdup_base,bins=20)
plt.title("Base case Hold up")
plt.xlabel("Hours of total waittime")
plt.show()

fig2 = plt.figure(figsize=(10,10))
plt.hist(Array_holdup_inn,bins=20)
plt.title("Innovation case Hold up")
plt.xlabel("Hours of total waittime")
plt.show()

fig3 = plt.figure(figsize=(10,10))
plt.hist(Array_Bat_base,bins=20)
plt.title("Base case Total Batteries")
plt.xlabel("Total batteries in ports")
plt.show()

fig4 = plt.figure(figsize=(10,10))
plt.hist(Array_Warn_base,bins=20)
plt.title("Base case Total Warnings")
plt.xlabel("Total warnings isued by ports")
plt.show()

fig5 = plt.figure(figsize=(10,10))
plt.hist(Array_Charge_base,bins=20)
plt.title("Base case Total Charged Batteries")
plt.xlabel("Total charged batteries in the simulation")
plt.show()

fig6 = plt.figure(figsize=(10,10))
plt.hist(Array_Cont_base,bins=20)
plt.title("Base case Total transported Containers")
plt.xlabel("Total transported cargo containers during the simulation")
plt.show()

fig7 = plt.figure(figsize=(10,10))
plt.hist(Array_Bat_inn,bins=20)
plt.title("Innovation case Total Batteries")
plt.xlabel("Total batteries in ports")
plt.show()

fig8 = plt.figure(figsize=(10,10))
plt.hist(Array_Warn_inn,bins=20)
plt.title("Innovation case Total Warnings")
plt.xlabel("Total warnings isued by ports")
plt.show()

fig9 = plt.figure(figsize=(10,10))
plt.hist(Array_Charge_inn,bins=20)
plt.title("Innovation case Total Charged Batteries")
plt.xlabel("Total charged batteries in the simulation")
plt.show()

fig10 = plt.figure(figsize=(10,10))
plt.hist(Array_Cont_inn,bins=20)
plt.title("Innovation case Total transported Containers")
plt.xlabel("Total transported cargo containers during the simulation")
plt.show()