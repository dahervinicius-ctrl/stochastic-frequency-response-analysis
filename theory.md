For the simulation of wind power output, the Ornstein-Uhlenbeck (OU) process was chosen since we assume we have a goal for power generation for wind energy that should revolve around a $P_w$ since if we produce more, there could be mechanical stress in the wind turbine (though we can endure some "overproduction"), and we want it to not bee to low.

OU Process: $$dx_t = \theta(\mu - x_t)dt + \sigma dW_t$$

- $\theta$: mean reversion speed (how fast it goes back to "normal" operation)
- $\mu$: long term mean of wind speed
- $\sigma$: volatility 


For wind power generation, the basic equation is the follow:
$\frac{1}{2}\rho A v^3 \eta _{total}$

- v: speed of wind at hub height
- $\rho$: air density
- $\eta _{total}$: Total efficiency of wind turbine ($C_p \times \eta _{turbine}$ ) 
- A: Sweep area of turbine blades


Assumptions:

- Offshore wind farm in north-west Germany (Based off Sylt's airport EDXW)
- since data is collected onshore, we will assume an offshore mean velocity 25%* higher and maybe 90% of the standard deviation due to less obstruction at the sea
- Turbine: Vestas V236-15.0 MW with some assumptions
- Blade size: 115,5m (sweep area considers radius = 118m)
- Air density: 1,225 kg/m^3
- Total wind turbine efficiency: 40%
- No energy production for: 30m/s < $v$ < 3m/s

*This will be assumed to be the velocity at Hub's altitude for simplification