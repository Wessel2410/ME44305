# ----- Import library -----
import pandas as pd
import numpy as np

distance_dataframe = pd.read_csv(r'PortData.csv', header=None)
distance_array = np.array(distance_dataframe)

port_name_array = ['Rotterdam', 'Antwerp', 'Amsterdam', 'Duisburg', 'Vlissingen',
                 'Paris', 'Liege', 'Terneuzen', 'Moerdijk', 'Cologne',
                 'Mannheim',
                 'Karlsruhe', 'Louviere', 'Sittard', 'Velsen', 'Strasbourg',
                 'Dordrecht', 'Neuss', 'Ludwigshafen', 'Brussels', 'Delfzijl']


def find_port_distance(start_port, end_port):
    start_index = port_name_array.index(start_port)
    end_index = port_name_array.index(end_port)

    port_distance = int(distance_array[start_index][end_index])

    return port_distance
