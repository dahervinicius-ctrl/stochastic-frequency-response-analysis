Goal: Simulate a microgrid consisting of a synchronous generator, wind turbine, battery pack and load to study grid stability under different scenarios:

- synchronous generator and load, local primary control to accomodate frequency deviations and reaction time ~ dt for simulation.
- wind turbine + generator + load, simulate effects penetration of a wind turbine has in the overall grid stability since power generation of wind is modelled after a stochastic wind profile. Redispatch central to manage P_gen and maybe even implement curtailment logic if too much power is being generated.  
- wind turbine + battery pack + generator + load, manage grid stability considering powerr redispatch to and from battery to share generator's burden in controlling the grid    




Simulation of a simple microgrid consisting of generator + load

- Generator is modeled after the swing equation, with P_gen and P_load as references
- P_load modeled with standard industry profiles with the addition of white noise
- Simulation with dt = 5s (assumes the generator can change its reference point and adjust its P_gen after 5s of noticing unusual frequency deviation) 

