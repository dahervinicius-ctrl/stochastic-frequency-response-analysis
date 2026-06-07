from pathlib import Path
import argparse
import numpy as np

import src


def build_wind_profile(
    load_profile,
    dt,
    wind_penetration=0.35,
    mean_wind_speed=12.0,
    initial_wind_speed=12.0,
    mean_reversion_time=1800.0,
    volatility=0.025,
    seed=7,
):
    """
    Create a stochastic wind generation profile with the same length as the load.

    wind_penetration is the rated turbine power on the same p.u. base as the load.
    For example, 0.35 means the wind turbine rated power is 35% of peak load.
    """
    rng_state = np.random.get_state()
    np.random.seed(seed)

    total_time = float(load_profile.index[-1] + dt)
    theta = 1 / mean_reversion_time
    _, wind_speed = src.simulate_ou_process(
        x0=initial_wind_speed,
        theta=theta,
        mu=mean_wind_speed,
        sigma=volatility,
        T=total_time,
        dt=dt,
    )

    np.random.set_state(rng_state)

    wind_speed = np.clip(wind_speed, 0.0, None)
    wind_power = src.wind_power_generation_vec(wind_speed)
    wind_power = wind_penetration * wind_power

    if len(wind_power) < len(load_profile):
        wind_power = np.pad(wind_power, (0, len(load_profile) - len(wind_power)), mode="edge")

    return wind_power[: len(load_profile)]


def main():
    parser = argparse.ArgumentParser(
        description="Run a microgrid frequency response simulation."
    )
    parser.add_argument("--dt", type=float, default=5.0, help="Load/wind sampling time [s].")
    parser.add_argument(
        "--integration-dt",
        type=float,
        default=0.5,
        help="Internal solver time step for governor and swing dynamics [s].",
    )
    parser.add_argument("--h", type=float, default=3.5, help="Generator inertia constant H [s].")
    parser.add_argument("--d", type=float, default=1.0, help="Load damping coefficient [p.u./p.u. frequency].")
    parser.add_argument("--droop-r", type=float, default=0.05, help="Droop R [p.u. frequency / p.u. power].")
    parser.add_argument("--t-governor", type=float, default=2.0, help="Governor actuator time constant [s].")
    parser.add_argument("--t-turbine", type=float, default=20.0, help="Prime mover/turbine time constant [s].")
    parser.add_argument(
        "--p-mech-ramp-rate",
        type=float,
        default=0.005,
        help="Maximum mechanical power ramp rate [p.u./s].",
    )
    parser.add_argument(
        "--p-set-ramp-rate",
        type=float,
        default=0.005,
        help="Maximum secondary dispatch setpoint ramp rate [p.u./s].",
    )
    parser.add_argument("--p-max", type=float, default=1.2, help="Generator maximum mechanical power [p.u.].")
    parser.add_argument("--p-min", type=float, default=0.0, help="Generator minimum mechanical power [p.u.].")
    parser.add_argument(
        "--wind-penetration",
        type=float,
        default=0.35,
        help="Rated wind power as a fraction of peak load. Use 0 for no wind.",
    )
    parser.add_argument(
        "--no-secondary-control",
        action="store_true",
        help="Disable slow secondary control and show pure primary droop behavior.",
    )
    parser.add_argument(
        "--secondary-time-constant",
        type=float,
        default=120.0,
        help="Secondary control time constant [s].",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Run without opening matplotlib plots.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("simulation_results.csv"),
        help="CSV file where simulation results are saved.",
    )

    args = parser.parse_args()

    load_profile = src.generate_daily_load_profile(dt=args.dt)

    if args.wind_penetration > 0:
        wind_profile = build_wind_profile(
            load_profile=load_profile,
            dt=args.dt,
            wind_penetration=args.wind_penetration,
        )
    else:
        wind_profile = np.zeros(len(load_profile))

    result = src.simulate_microgrid_governor(
        dt=args.dt,
        integration_dt=args.integration_dt,
        h=args.h,
        d=args.d,
        droop_r=args.droop_r,
        t_governor=args.t_governor,
        t_turbine=args.t_turbine,
        p_mech_ramp_rate=args.p_mech_ramp_rate,
        p_set_ramp_rate=args.p_set_ramp_rate,
        p_min=args.p_min,
        p_max=args.p_max,
        load_profile=load_profile,
        wind_profile=wind_profile,
        secondary_control=not args.no_secondary_control,
        secondary_time_constant=args.secondary_time_constant,
        plot=not args.no_plot,
    )

    output_path = args.output.resolve()
    result.to_csv(output_path)

    print("Simulation complete")
    print(f"Samples: {len(result)}")
    print(f"Frequency min/max: {result['frequency_hz'].min():.4f} / {result['frequency_hz'].max():.4f} Hz")
    print(f"Final frequency: {result['frequency_hz'].iloc[-1]:.4f} Hz")
    print(f"Final P_mech: {result['P_mech'].iloc[-1]:.4f} p.u.")
    print(f"Peak net load: {result['P_net_load'].max():.4f} p.u.")
    print(f"Results saved to: {output_path}")

    return result


if __name__ == "__main__":
    main()
