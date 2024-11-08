import W7_Calculate_StepDelay_Interpolate

# This script is focused on formatting the voltage values into the URscript 
#creating the 12_FinalFormat_URscript.txt 
# This could have been inside the W7 script as it calls and runs every calculation 
#to get the proper voltage values

def format_urscript_voltages(file_path_urscript_newl, output_file_path_FinalFormat, voltage_values):
    # Read the input URScript file
    with open(file_path_urscript_newl, "r") as file:
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
            insertions.append((i + 1, "  set_analog_out(0, 0.5)\n"))                             ### Control where the test extrusion happens and the value of it   
            continue

        # Start inserting analog output before 'movel' after we find 'movej'
        if found_movej and "movel" in line:
            if voltage_index < len(voltage_values):
                voltage_value = voltage_values[voltage_index]
                # Collect the insertion information
                insertions.append((i+1, f"  set_analog_out(0, {voltage_value})\n"))              ###i+1 will start inserting after the first movel this can always be changed
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
    with open(output_file_path_FinalFormat, "w") as file:
        file.writelines(modified_lines)

def main():
    # Input, output file paths, and voltage mapping
    # Setup for the translation function
    old_min = 1100
    old_max = 60000
    new_min = 0.5
    new_max = 0
    #setup for formating
    file_path_urscript_newl = "URscript_newmovel.txt"
    output_file_path_FinalFormat = "FinalFormat_URscript.txt"

    # Get step delay values and map them to voltages

    ρ = 0.002015                                                        # g/mm^3
    m = 6.7                                                             # g
    V_p = W7_Calculate_StepDelay_Interpolate.calculate_Vp(ρ, m)         # mm^3 per 1 revolution
    w_target = 5.5                                                      # mm
    h_target = 5                                                        # mm
    Ns = 1035                                                           # unit
    
    output_file_path_lspeed = "Linear_speeds_2.txt"
    v_new = W7_Calculate_StepDelay_Interpolate.read_v_values(output_file_path_lspeed)
    step_delay_values = W7_Calculate_StepDelay_Interpolate.calculate_step_delay(Ns, V_p, w_target, h_target, v_new)
    voltage_values = W7_Calculate_StepDelay_Interpolate.map_step_delay_to_voltage(step_delay_values, old_min, old_max, new_min, new_max)
    # Format the URScript file with the voltages
    format_urscript_voltages(file_path_urscript_newl, output_file_path_FinalFormat, voltage_values)

if __name__ == "__main__":
    main()
