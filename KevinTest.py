# Bank, 3 clerks (store).py

import salabim as sim
import numpy as np


class ShipGenerator(sim.Component):
    def setup(self, amount_of_ships):
        self.amount_of_ships = amount_of_ships

    def process(self):
        for _ in range(self.amount_of_ships):
            start_port_string = port_choice()
            start_port = port_dict[start_port_string]
            end_port_string = port_choice(current_port=start_port_string)
            end_port = port_dict[end_port_string]

            Ship(current_port=start_port, destination_port=end_port,
                 current_port_string=start_port_string,
                 destination_port_string=end_port_string)


class Ship(sim.Component):
    def setup(self, current_port, destination_port,
              current_port_string, destination_port_string):
        self.length = 100
        self.current_port = current_port
        self.current_port_string = current_port_string
        self.destination_port = destination_port
        self.destination_port_string = destination_port_string

    def process(self):
        for n in range(100):
            # Leave the current port's queue if it's in one
            if self in self.current_port.queue:
                self.leave(self.current_port.queue)

            # Start 'sailing'
            self.hold(30)

            # Enter the destination port's queue
            self.enter(self.destination_port.queue)

            # Update current port
            self.current_port = self.destination_port
            self.current_port_string = self.destination_port_string

            # Generate a new destination port
            end_port_string = port_choice(current_port=self.current_port_string)
            end_port = port_dict[end_port_string]

            # Update the destination ports
            self.destination_port = end_port
            self.destination_port_string = end_port_string


class Port(sim.Component):
    def setup(self):
        self.name = self.name()
        self.queue = sim.Queue(self.name)


def port_choice(current_port=None):
    port_list = ['Rotterdam', 'Antwerp', 'Amsterdam', 'Duisburg', 'Vlissingen',
                 'Paris', 'Liege', 'Terneuzen', 'Moerdijk', 'Cologne',
                 'Mannheim',
                 'Karlsruhe', 'Louviere', 'Sittard', 'Velsen', 'Strasbourg',
                 'Dordrecht', 'Neuss', 'Ludwigshafen', 'Brussels', 'Delfzijl']
    port_odds = [0.297, 0.199, 0.111, 0.083, 0.048, 0.041, 0.029, 0.023, 0.019,
                 0.016, 0.015, 0.013, 0.013, 0.013, 0.013, 0.013, 0.012, 0.011,
                 0.011, 0.010, 0.010]

    if current_port is not None:
        current_port_index = port_list.index(current_port)
        del port_list[current_port_index]
        del port_odds[current_port_index]

        new_port_odds = [odd / sum(port_odds) for odd in port_odds]

        chosen_port = str(np.random.choice(port_list, 1, p=new_port_odds)[0])

        return chosen_port
    else:
        chosen_port = str(np.random.choice(port_list, 1, p=port_odds)[0])

        return chosen_port


env = sim.Environment(trace=True)

ShipGenerator(amount_of_ships=10)

port_rotterdam = Port('Rotterdam')
port_antwerp = Port('Antwerp')
port_amsterdam = Port('Amsterdam')
port_duisburg = Port('Duisburg')
port_vlissingen = Port('Vlissingen')
port_paris = Port('Paris')
port_Liege = Port('Liege')
port_terneuzen = Port('Terneuzen')
port_moerdijk = Port('Moerdijk')
port_cologne = Port('Cologne')
port_mannheim = Port('Mannheim')
port_karlsruhe = Port('Karlsruhe')
port_louviere = Port('Louviere')
port_sittard = Port('Sittard')
port_velsen = Port('Velsen')
port_strasbourg = Port('Strasbourg')
port_dordrecht = Port('Dordrecht')
port_neuss = Port('Neuss')
port_ludwigshafen = Port('Ludwigshafen')
port_brussels = Port('Brussels')
port_delfzijl = Port('Delfzijl')

port_dict = {'Rotterdam': port_rotterdam,
             'Antwerp': port_antwerp,
             'Amsterdam': port_amsterdam,
             'Duisburg': port_duisburg,
             'Vlissingen': port_vlissingen,
             'Paris': port_paris,
             'Liege': port_Liege,
             'Terneuzen': port_terneuzen,
             'Moerdijk': port_moerdijk,
             'Cologne': port_cologne,
             'Mannheim': port_mannheim,
             'Karlsruhe': port_karlsruhe,
             'Louviere': port_louviere,
             'Sittard': port_sittard,
             'Velsen': port_velsen,
             'Strasbourg': port_strasbourg,
             'Dordrecht': port_dordrecht,
             'Neuss': port_neuss,
             'Ludwigshafen': port_ludwigshafen,
             'Brussels': port_brussels,
             'Delfzijl': port_delfzijl}

env.run(till=1000)

