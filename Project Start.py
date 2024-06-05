import salabim as sim
import math
import numpy as np
import random

ChargingTime = 100
WarningLimit = -10
BatteryCount = 0
ContainerLoadingTime = 100
MaxBatEnergy = 100
CargoCapacity = 100

DistanceLookup = np.array([[0,1,2],[1,0,1],[2,1,0]])
WaittimeList = np.array([1,2,3])

def CalculateDistance(CurrentPort, DestinationPort):
    IndexCurrentPort = FindPortInRiver(CurrentPort)
    IndexDestination = FindPortInRiver(DestinationPort)
    return DistanceLookup[IndexCurrentPort][IndexDestination]

def GetWaitTime(DestinationPort):
    IndexDestination = FindPortInRiver(DestinationPort)
    return WaittimeList[IndexDestination]

def GetRoute(CurrentPortName):
    CurrentIndex = FindPortInRiver(CurrentPortName)
    NewIndex = CurrentIndex
    while CurrentIndex == NewIndex:
        NewIndex = np.random.randint(0, len(River))
    Cargo = CargoCapacity*random.uniform(0.5, 1)
    Batteries = 1 # TO Build using distance
    return River[NewIndex].name, Cargo, Batteries

def FindPortInRiver(Portname):
    index = 0
    Found = False
    for i in range(len(River)):
        if River[i].name == Portname:
            index = i
            Found = True
    if Found:
        return index
    else:
        print("NO PORT FOUND IN RIVER")
        

class Tship(sim.Component):
    def setup(self):
        self.speed = 14
        self.CargoCap = 100
        self.currentPort = None
        self.destinationPort = None
        self.EnergyUsage = 10 #km per kwh
        self.FullBatteries = 100
        self.EmptyBatteries = 0
        self.HalfBatteryCharge = 1
        self.Charge = 100
        self.BatteryLimit = 20
        
    
    def process(self):
        #TravelTime
        Distance = CalculateDistance(self.currentPort, self.destinationPort)
        SaillingTime = Distance/self.speed
        self.hold(SaillingTime)
        WaitingTime = GetWaitTime(self.destinationPort)
        self.hold(WaitingTime)
        
        #Empty the Batteries
        UsedCharge = Distance/self.EnergyUsage
        ChargeRatio = (self.Charge - UsedCharge)/self.Charge
        self.FullBatteries = math.floor(self.BatteryLimit * ChargeRatio)
        self.EmptyBatteries = math.floor(self.BatteryLimit* (1-ChargeRatio))
        self.HalfBatteryCharge = self.BatteryLimit * ChargeRatio - self.FullBatteries
        self.Charge -= UsedCharge
        
        # Deal with desination
        self.currentPort = self.destinationPort
        River[River.index(self.currentPort)].MyQueue.add(self)
        self.passivate()
        


class TchargingStation(sim.Component):
    def setup(self):
        self.ChargingTime = ChargingTime
        self.MyPort = None
        self.TotalCharged = 0
    
    def process(self):
        while True:
            print("In Process")
            if self.MyPort.EmptyBatteries > 0:
                self.hold(ChargingTime)
                self.MyPort.EmptyBatteries -=1
                self.TotalCharged += 1
                


class TquaySide(sim.Component):
    def setup (self):
        self.MyQueue = sim.Queue (self.name () + '-WaitingLine')
        self.Myport = None
    
    def process(self):
        while True:
            if len(self.Myport.MyQueue)==0:
                self.standby()
            else:
                Ship = self.Myport.MyQueue[0]
                self.Myport.MyQueue.remove(0)
                self.hold(Ship.CargoCap*ContainerLoadingTime)
                self.hold((Ship.EmptyBatteries+Ship.FullBatteries+1)*ContainerLoadingTime)
                self.MyPort.EmptyBatteries += (Ship.EmptyBatteries+1)
                
                ContainerTarget, BatteryCargo, Desination = GetRoute()
                
                self.hold(ContainerTarget*ContainerLoadingTime)
                self.hold(BatteryCargo*ContainerLoadingTime)
                Ship.BatteryLimit = BatteryCargo
                self.MyPort.BattertCount -= BatteryCargo
                
                Ship.Desination = Desination
                Ship.Charge = BatteryCargo*MaxBatEnergy
                Ship.FullBatteries = BatteryCargo
                Ship.EmptyBatteries = 0
                Ship.HalfBatteryCharge = 1
                sim.activate(Ship)
            

class Tport(sim.Component):
    def setup(self):
        self.MyQueue = sim.Queue (self.name () + '-WaitingToPort')
        self.name = self.name()
        self.quay = TquaySide()
        self.quay.Myport = self
        self.CS = TchargingStation()
        self.CS.MyPort = self
        self.EmptyBatteries = 20
        self.BattertCount = 0
        self.RequestBatteries = False
    
    def process(self):
        while True:
            if self.BattertCount<=WarningLimit:
                self.RequestBatteries = True
            else:
                self.RequestBatteries = False       
        

Port1 = Tport("Rotterdam")
Port2 = Tport("Nijmegen")
Port3 = Tport("Dusseldorf")

Ship1 = Tship()
Ship1.activate()
Port1.MyQueue.add(Ship1)

River = [Port1,Port2,Port3]

env = sim.Environment (trace = True)

env.run (12*3600)

