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



def wind_power_generation(
                            v: float, 
                            rho: float =1.225, 
                            radius: float =118, 
                            efficiency: float =0.4
                            ) -> float:
    

    """
    Calculates the power output of a wind turbine based off its atributes (wind velocity at hub, 
    air density, turbine radius and efficiency)
    returns the power output [W]
    
    Default: Vestas V236-15.0 MW model

    """

    rated_power = 15000000 # 15MW

    A = np.pi * radius**2

    if (v < 3):
        power  = 0

    elif (v > 31):
        power = 0

    else:
        power = (1/2)*rho*(v**3)*A*efficiency
        
    return power/rated_power # result in p.u

wind_power_generation_vec = np.vectorize(wind_power_generation) # makes the function accept vectors as inputs to do batch calculations


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

def solve_swing_equation(f_prev, p_gen, p_load, h=3.5, d=1.5, dt=0.1, f_nom=50.0):
    """
    Solves the swing equation for one time step.
    df/dt = (1 / 2H) * (P_mech - P_elec - D * delta_f)
    """
    delta_f = f_prev - f_nom
    # The swing equation: 2H * df/dt = P_gen - P_load - D * delta_f
    df_dt = (p_gen - p_load - (d * delta_f)) / (2 * h)
    
    f_next = f_prev + (df_dt * dt)
    return f_next




"""plt.plot(time, x)
plt.axhline(y=10, color='r', linestyle='--', label='Long-term Mean ($\mu$)')
plt.title("Simulated wind velocity over 3 months")
plt.xlabel("Time"); plt.ylabel("Wind Velocity")
plt.legend(); plt.show()"""

def generate_daily_load_profile(dt=0.1, P_peak = 1, P_min = 0.5):

    t = np.arange(0, 86400 + dt, dt) # 24 hours

    load = pd.DataFrame()
    load.index = t

    time = len(load) * dt

    load["P_load"] = P_min  #baseline minimum load

    # fist ramp up from 6:00 until 9:00

    time1 = (6/24)*time
    time2 = (9/24)*time
    load["aux"] = (load.index - time1) * (P_peak - P_min)/(time2 - time1)
    load["P_load"].loc[time1:time2] = P_min + load["aux"]

    # stay in peak from 9:00 until 12:00

    time1 = (9/24)*time
    time2 = (12/24)*time
    load["P_load"].loc[time1:time2] = P_peak

    # small dip for lunch break 12:00 until 13:00
    time1 = (12/24)*time
    time2 = (13/24)*time
    load["aux"] = (-1)*np.sqrt(0.2) + (load.index - time1) * ((2*np.sqrt(0.2))/(time2 - time1))
    load["P_load"].loc[time1:time2] = load["aux"]**2 + 0.8*P_peak

    # stay in peak power until 20:00
    time1 = (13/24)*time
    time2 = (20/24)*time
    load["P_load"].loc[time1:time2] = P_peak

    # ramp down from 20:00 to 22:00
    
    time1 = (20/24)*time
    time2 = (22/24)*time
    load["aux"] = (load.index - time1) * (P_min - P_peak)/(time2 - time1)
    load["P_load"].loc[time1:time2] = P_peak + load["aux"]

    # Add random noise throughout the day
    load["P_load"] = load["P_load"] + np.random.normal(0, 0.005, len(load))

    return load


def simulate_generator_load(dt=0.1, h: float = 3.5, d: float = 1.5, plot=True):

    deadzone = 0.01
    f0 = 50 # initial frequency, also nominal frequency
    P_gen = 0.5 # initial generator mechanical power

    f = f0

    frequencies = []
    generator_references = []

    load_profile = src.generate_daily_load_profile(dt=dt) #this is the profile of a random industry

    for P_load in load_profile["P_load"]:

        if (f < (f0 + deadzone)) & (f > (f0 - deadzone)): # don't change the reference value for the generator
            f = src.solve_swing_equation(f, P_gen, P_load, h = h, d=d, dt=dt, f_nom=f0)
            frequencies.append(f)
            generator_references.append(P_gen)
        else:
            f = src.solve_swing_equation(f, P_gen, P_load, h = h, d=d, dt=dt, f_nom=f0)
            frequencies.append(f)
            P_gen = P_load
            generator_references.append(P_gen)


    if plot:
        time_steps = load_profile.index / (3600)

        plt.figure(figsize=(10, 4.5))

        plt.plot(
            time_steps,
            frequencies,
            linewidth=2,
            color="tab:blue",
            label="Grid frequency"
        )

        plt.axhline(
            50.01,
            color="tab:orange",
            linestyle="--",
            linewidth=1,
            label="Upper deadzone boundary"
        )

        plt.axhline(
            49.99,
            color="tab:orange",
            linestyle="--",
            linewidth=1,
            label="Lower deadzone boundary"
        )

        plt.axhline(
            50.05,
            color="tab:red",
            linestyle="--",
            linewidth=1.5,
            label="Upper nominal boundary"
        )

        plt.axhline(
            49.95,
            color="tab:red",
            linestyle="--",
            linewidth=1.5,
            label="Lower nominal boundary"
        )

        plt.axhline(
            50,
            color="black",
            linestyle=":",
            linewidth=1,
            alpha=0.7,
            label="Nominal frequency"
        )

        # plt.ylim(49.9, 50.1)
        # plt.xlim(time_steps[0], time_steps[-1])
        plt.xlabel("Time [h]")
        plt.ylabel("Frequency [Hz]")
        plt.title("Grid Frequency Over Time")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()

