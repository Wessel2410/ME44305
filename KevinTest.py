# Bank, 3 clerks (store).py

import salabim as sim
import numpy as np

class ShipGenerator(sim.Component):
    def process(self):
        while True:
            self.hold(sim.Uniform(5, 15))


class Ship(sim.Component):
    def setup(self, current_port, destination_port):
        self.length = 100
        self.current_port = current_port
        self.destination_port = destination_port

    def process(self):
        self.enter(self.current_port.queue)
        self.hold(30)
        self.enter(self.destination_port.queue)


class Port(sim.Component):
    def setup(self):
        self.name = self.name()
        self.queue = sim.Queue(self.name)


def port_choice():
    port_list = ['Rotterdam', 'Mannheim', 'Paris']
    port_odds = [0.5, 0.3, 0.2]
    chosen_port = str(np.random.choice(port_list, 1, p=port_odds)[0])

    return chosen_port


env = sim.Environment(trace=True)

ShipGenerator()

port_rotterdam = Port('Rotterdam')
port_mannheim = Port('Mannheim')
port_paris = Port('Paris')

port_dict = {'Rotterdam': port_rotterdam,
             'Mannheim': port_mannheim,
             'Paris': port_paris}

for _ in range(3):
    start_port = port_dict[port_choice()]
    end_port = port_dict[port_choice()]

    while end_port == start_port:
        end_port = port_dict[port_choice()]

    Ship(current_port=start_port, destination_port=end_port)

env.run(till=1000)
