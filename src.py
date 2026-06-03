import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def simulate_ou_process(x0, theta, mu, sigma, T, dt):
    
    # Here, T or dt could be either in hours or seconds, but then need to change the dynamics to fit 
    # (less variation from 1s to 2s for example if compared with 1h to 2h)

    n_steps = int(T / dt)
    time = np.linspace(0, T, n_steps)
    x = np.zeros(n_steps)
    x[0] = x0
    
    # Pre-generate random noise for efficiency
    epsilon = np.random.normal(0, 1, n_steps)
    
    for t in range(1, n_steps):
        # Discretization using Euler
        drift = theta * (mu - x[t-1]) * dt
        diffusion = sigma * np.sqrt(dt) * epsilon[t]
        x[t] = x[t-1] + drift + diffusion
        
    return time, x



def wind_energy_generation(
                            v: float, 
                            rho: float =1.225, 
                            radius: float =118, 
                            efficiency: float =0.4
                            ) -> float:
    

    """
    Calculates the energy output of a wind turbine based off its atributes (wind velocity at hub, 
    air density, turbine radius and efficiency)
    returns the energy output

    """

    A = np.pi * radius**2

    if (v < 3):
        energy  = 0

    elif (v > 30):
        energy = (1/2)*rho*(30**3)*A*efficiency

    else:
        energy = (1/2)*rho*(v**3)*A*efficiency
        
    return energy

wind_energy_generation_vec = np.vectorize(wind_energy_generation) # makes the function accept vectors as inputs to do batch calculations


def get_wind_speed_profile(file="asos.csv"):

    df = pd.read_csv(
        file,
        sep=",",
        usecols=[1, 2],      # second and third columns, Python uses 0-based indexing
        parse_dates=[0],     # parse the first selected column as datetime
        index_col=0          # use the first selected column as the index
    )

    df["wind_speed[m/s]"] = df["sped"] * 0.44704

    print(df["wind_speed[m/s]"].describe())

    return df
