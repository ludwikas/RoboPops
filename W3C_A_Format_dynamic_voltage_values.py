import re
import W3C_A_Calculate_StepDelay_Interpolate

def format_urscript_voltages(input_file, output_file_volt, voltage_values):
    # Read the input URScript file
    with open(input_file, "r") as file:
        lines = file.readlines()

    # Make a copy of the lines to modify
    modified_lines = lines[:]
    voltage_index = 0
    found_movej = False  # Flag to determine if we have passed the 'movej'

    # Collect all insertions to apply later
    insertions = []

    # Iterate through lines to locate 'movej' and start inserting after that
    for i in range(len(modified_lines)):
        line = modified_lines[i]

        # Locate the 'movej' command and set the flag
        if "movej" in line:
            found_movej = True
            continue

        # Start inserting analog output before 'movel' after we find 'movej'
        if found_movej and "movel" in line:
            if voltage_index < len(voltage_values):
                voltage_value = voltage_values[voltage_index]
                # Collect the insertion information
                insertions.append((i+1, f"  set_analog_out(0, {voltage_value})\n"))               #i+1 will start inserting after the first movel this can always be changed
                voltage_index += 1

    # Apply the collected insertions in reverse order to maintain correct indexing
    for index, insertion in reversed(insertions):
        modified_lines.insert(index, insertion)

    # Insert analog output to stop extrusion just before the 'end' command
    for i, line in enumerate(modified_lines):
        if "end" in line:
            modified_lines.insert(i - 1, "  set_analog_out(0, 0.0)\n")
            break

    # Write the modified lines to the output file
    with open(output_file_volt, "w") as file:
        file.writelines(modified_lines)

def main():
    # Input, output file paths, and voltage mapping
    # Setup for the translation function
    file_path_step = "stepdelay_values.txt"
    old_min = 0
    old_max = 60000
    new_min = 0.5
    new_max = 0
    #setup for formating
    input_file = "URscriptTestForVoltInsertion.txt"
    output_file_volt = "DynamicVoltScript.txt"

    # Get step delay values and map them to voltages

    ρ = 0.002015                                                        # g/mm^3
    m = 6.7                                                             # g
    V_p = W3C_A_Calculate_StepDelay_Interpolate.calculate_Vp(ρ, m)          # mm^3 per 1 revolution
    w_target = 5.5                                                      # mm
    h_target = 5                                                        # mm
    Ns = 1035                                                           # unit
    file_path_v_values = "Speeds_sequential_idx.txt"
    v_new = W3C_A_Calculate_StepDelay_Interpolate.read_v_values(file_path_v_values)
    step_delay_values = W3C_A_Calculate_StepDelay_Interpolate.calculate_step_delay(Ns, V_p, w_target, h_target, v_new)
    voltage_values = W3C_A_Calculate_StepDelay_Interpolate.map_step_delay_to_voltage(step_delay_values, old_min, old_max, new_min, new_max)
    # Format the URScript file with the voltages
    format_urscript_voltages(input_file, output_file_volt, voltage_values)

if __name__ == "__main__":
    main()
