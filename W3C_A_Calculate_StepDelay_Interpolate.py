import re
import numpy as np

# Function to read velocity values from file
def read_v_values(file_path_v_values):
    v_values = []
    with open(file_path_v_values, "r") as file:
        for line in file:
            match = re.search(r":\s*([-+]?\d*\.?\d+)", line)
            if match:
                v_values.append(float(match.group(1)))
    return v_values

# Function to calculate volumetric value
def calculate_Vp(ρ, m):
    V_p = m / ρ
    return V_p

# Function to calculate step delay
def calculate_step_delay(Ns, V_p, w_target, h_target, v_new):
    if isinstance(v_new, list):
        # If v_new is a list, calculate for each value in the list
        step_delays = []
        for v in v_new:
            if v == 0:
                print(f"Warning: Velocity value is zero, skipping calculation for v = {v}")
                step_delays.append(None)  # Append None to indicate skipped value
                continue

            K = V_p / Ns
            n = round((K / (w_target * h_target * v)) * 1000, 2)  # Convert to μs
            step_delays.append(n)
            print(f"Calculated step delay for v = {v} m/s: {n} μs")
        return step_delays

# Function to calculate the maximum step delay
def sort_max_delay(step_delays):
    valid_delays = [delay for delay in step_delays if delay is not None]
    if valid_delays:
        return max(valid_delays)
    else:
        return 1  # Default value if no valid delays are found

# Function to map step delay to voltage using logarithmic scaling
def map_step_delay_to_voltage(step_delay_values, old_min, old_max, new_min, new_max):
    voltage_values = []
    for value in step_delay_values:
        if value is None:
            voltage_values.append(None)  # If step delay is None, append None
            continue
        if value <= 0:
            value = 1  # Avoid log of zero or negative numbers
        scaled_value = np.log(value)  # Apply logarithm to compress the range
        old_range_log = np.log(old_max) - np.log(old_min if old_min > 0 else 1)
        voltage = new_min + ((scaled_value - np.log(old_min)) / old_range_log) * (new_max - new_min)
        voltage_values.append(float(round(voltage, 4)))  # Convert to float and round to 4 decimal places
    return voltage_values


def main():
    # Main workflow
    ρ = 0.002015                    # g/mm^3
    m = 6.7                         # g
    V_p = calculate_Vp(ρ, m)        # mm^3 per 1 revolution
    w_target = 5.5                  # mm
    h_target = 5                    # mm
    Ns = 1035                       # unit

    file_path_v_values = "Speeds_sequential_idx.txt"
    v_new = read_v_values(file_path_v_values)

    # Calculate step delays
    step_delay_values = calculate_step_delay(Ns, V_p, w_target, h_target, v_new)

    # Calculate the dynamic old_max value
    old_max = sort_max_delay(step_delay_values)

    # Map step delays to voltage values
    old_min = 0.0001
    new_min = 0.5
    new_max = 0

    voltage_values = map_step_delay_to_voltage(step_delay_values, old_min, old_max, new_min, new_max)
    print("Voltage values:", voltage_values)

if __name__ == "__main__":
    main()