# ----- Import library -----
import pandas as pd
import numpy as np
import math
from scipy.interpolate import interp1d

distance_dataframe = pd.read_csv(r'PortData.csv', header=None)
distance_array = np.array(distance_dataframe)

port_name_array = ['Rotterdam', 'Antwerp', 'Amsterdam', 'Duisburg',
                   'Vlissingen', 'Paris', 'Liege', 'Terneuzen', 'Moerdijk',
                   'Cologne', 'Mannheim', 'Karlsruhe', 'Louviere', 'Sittard',
                   'Velsen', 'Strasbourg', 'Dordrecht', 'Neuss', 'Ludwigshafen',
                   'Brussels', 'Delfzijl']

# Delay times in days
delay_times = [0, 0.152877698, 0.341726619, 0.485611511, 0.65647482,
               0.881294964, 1.065647482, 1.290467626, 1.488309353, 1.690647482,
               1.84352518, 2.000899281, 2.158273381, 2.257194245, 2.369604317,
               2.522482014, 2.711330935, 2.954136691, 3.250899281, 3.606115108,
               3.929856115, 4.276079137, 4.685251799, 4.986510791, 5.364208633,
               5.822841727, 6, 7]

delay_probabilities = [0, 0.025316456, 0.055907173, 0.082278481, 0.116033755,
                       0.164556962, 0.207805907, 0.268987342, 0.327004219,
                       0.396624473, 0.462025316, 0.502109705, 0.464135021,
                       0.402953586, 0.333333333, 0.239451477, 0.1592827,
                       0.099156118, 0.060126582, 0.036919831, 0.024261603,
                       0.016877637, 0.009493671, 0.008438819, 0.005274262,
                       0.004219409, 0.001054852, 0]


def interpolator(interpolating_array, array_length, inter_type):
    """
    Interpolates the array over a given length.
    :param interpolating_array: Array to be interpolated
    :param array_length: Dimension of the interpolated array
    :param inter_type: Type of interpolation, such as spline
    :return interpolated_data: Interpolated array
    """
    array = np.array(interpolating_array)
    reference = np.linspace(array[0], array[-1], array_length)

    array_interp = interp1d(np.arange(array.size), array, kind=inter_type)
    interpolated_data = array_interp(np.linspace(0, array.size - 1,
                                                 reference.size))

    return interpolated_data


# Interpolate both the times and probabilities for a smoother distribution
delay_times = interpolator(delay_times, 1000,
                           "linear")
delay_probabilities = interpolator(delay_probabilities, 1000,
                                   "linear")

# Ensure that all probabilities sum to 1
scaled_probabilities = [prob / sum(delay_probabilities)
                        for prob in delay_probabilities]


def get_port_delay():
    """
    Calculates the amount of port delay in hours
    :return: float, port_delay in hours
    """

    # Decide if delay is present or not
    delay_decisions = [0, 1]
    delay = np.random.choice(delay_decisions, 1, p=[0.6, 0.4])[0]

    # If no delay, then port delay is zero hours
    if delay == 0:
        port_delay = 0

        return port_delay

    # Otherwise use probability to find the amount of port delay in hours
    else:
        port_delay = float(np.random.choice(delay_times, 1,
                                            p=scaled_probabilities)[0])
        hour_port_delay = port_delay * 24

        return hour_port_delay


def find_port_distance(start_port: str, end_port: str):
    """
    Calculates the distance between two ports
    :param start_port: starting port
    :param end_port: ending port
    :return: int, port_distance in km
    """

    start_index = port_name_array.index(start_port)
    end_index = port_name_array.index(end_port)

    port_distance = int(distance_array[start_index][end_index])

    return port_distance
