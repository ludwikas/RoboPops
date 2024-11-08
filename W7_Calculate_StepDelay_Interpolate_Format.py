import numpy as np

# The functions in this script are structured to 
# Read the speed values from 11_Linear_speeds_2.txt
# Calculate the value Vp which indicates the specific volume ( volume per revolution)
# Calculate the step delay (n) based on the Vp value
# Sort through the step delay list to create a dynamic min and max 
# Map the step delay values (logarithmicaly) into voltage values in a given range
# Format the voltage values into the URscript creating the 12_FinalFormat_URscript.txt

def read_v_values(file_path_v_values):
    v_values = []
    with open(file_path_v_values, "r") as file:
        for line in file:
            line = line.strip()  # Remove any leading/trailing whitespace
            try:
                v_values.append(float(line))  # Convert each line directly to float
            except ValueError:
                # Handle lines that aren't valid numbers, if any
                continue
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
    
# Function to calculate the minimum step delay
def sort_min_delay(step_delays):
    valid_delays = [delay for delay in step_delays if delay is not None]
    if valid_delays:
        return min(valid_delays)
    else:
        return 1  # Default value if no valid delays are found

# Function to map step delay to voltage using logarithmic scaling
def map_step_delay_to_voltage(step_delay_values, old_min, old_max, new_min, new_max):
    voltage_values = []
    for value in step_delay_values:
        if value is None:
            voltage_values.append(None)  
            continue
        if value <= 0:
            value = 1                                                                                                   # Avoid log of zero or negative numbers
        scaled_value = np.log(value)                                                                                    # Apply logarithm to compress the range
        old_range_log = np.log(old_max) - np.log(old_min if old_min > 0 else 1)
        voltage = new_min + ((scaled_value - np.log(old_min)) / old_range_log) * (new_max - new_min)
        voltage_values.append(float(round(voltage, 4)))                                                                 # Convert to float and round to 4 decimal places
    return voltage_values

# Function to format the calculated voltage values into the URscript 
def format_urscript_voltages(file_path_urscript_newl, output_file_path_FinalFormat, voltage_values):
    # Read the input URScript file
    with open(file_path_urscript_newl, "r") as file:
        lines = file.readlines()

    # Make a copy of the lines to modify
    modified_lines = lines[:]
    voltage_index = 0
    found_movej = False                                                                                 # Flag to determine if we have passed the 'movej'

    # Collect all insertions to apply 
    insertions = []

    # Iterate through lines to locate 'movej' and start inserting after that
    # This is a critical point of the algorithm where we are aware that this logic is 
    #not goint to work if there are other types of moves. An if statement could be inserted 
    #to more dynamically format the movel lines in further developement

    for i in range(len(modified_lines)):
        line = modified_lines[i]

        # Locate the 'movej' command and set the flag
        if "movej" in line:
            found_movej = True
            insertions.append((i + 1, "  set_analog_out(0, 0.5)\n"))                                   ### Control where the test extrusion happens and the value of it   
            continue

        # Start inserting analog output before 'movel' after we find 'movej'
        if found_movej and "movel" in line:
            if voltage_index < len(voltage_values):
                voltage_value = voltage_values[voltage_index]
                # Collect the insertion information
                insertions.append((i+1, f"  set_analog_out(0, {voltage_value})\n"))                    ###i+1 will start inserting after the first movel this can be changed
                voltage_index += 1

    # Apply the collected insertions in reverse order to maintain correct indexing
    for index, insertion in reversed(insertions):
        modified_lines.insert(index, insertion)

    # Insert analog output to stop extrusion just before the 'end' command
    # For any print the last move should be a retraction move that doesn't 
    #call for extrusion so we know that this value will always be (0,0) 
    for i, line in enumerate(modified_lines):
        if "end" in line:
            modified_lines.insert(i - 1, "  set_analog_out(0, 0.0)\n")
            break

    # Write the modified lines to the output file
    with open(output_file_path_FinalFormat, "w") as file:
        file.writelines(modified_lines)

def main():
    # Main workflow
    ρ = 0.002015                    # g/mm^3 
    m = 6.7                         # g
    V_p = calculate_Vp(ρ, m)        # mm^3 per 1 revolution
    w_target = 5.5                  # mm
    h_target = 5                    # mm
    Ns = 1035                       # unit

    file_path_urscript_newl = "URscript_newmovel.txt"
    output_file_path_FinalFormat = "FinalFormat_URscript.txt"

    file_path_v_values = "Linear_speeds_2.txt"
    v_new = read_v_values(file_path_v_values)

    # Calculate step delays
    step_delay_values = calculate_step_delay(Ns, V_p, w_target, h_target, v_new)

    # Calculate the dynamic old_max value
    old_max = sort_max_delay(step_delay_values)
    # Map step delays to voltage values
    old_min = sort_min_delay(step_delay_values)
    new_min = 0.5
    new_max = 0

    voltage_values = map_step_delay_to_voltage(step_delay_values, old_min, old_max, new_min, new_max)
    format_urscript_voltages(file_path_urscript_newl, output_file_path_FinalFormat, voltage_values)
    print("Voltage values after logarithmic mapping:", voltage_values)
    print(old_max)
    print(old_min)

if __name__ == "__main__":
    main()
