def calculate_rocket_trajectory(payload_mass: float, burn_time: float) -> float:
    """Simple placeholder function for atlas discovery tests."""
    if burn_time == 0:
        raise ValueError("burn_time cannot be zero")
    return payload_mass / burn_time
