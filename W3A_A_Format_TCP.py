import re
import sys
import os

# Function to automatically format the URScript
def format_urscript(file_path_unf, output_file_path_1f: str, ip_address: str, message_prefix="Move"):
    try:
        # Check if the input file exists
        if not os.path.exists(file_path_unf):
            print(f"Error: The file '{file_path_unf}' does not exist.")
            return

        # Read the input URScript
        with open(file_path_unf, "r") as file:
            urscript = file.read()

        # Regular expression to match motion commands like movej, movel, movep, etc.
        move_pattern = r'( +\bmove[jlp]\b\s*\([^)]+\))'

        # Find all movement commands
        moves = re.findall(move_pattern, urscript, re.IGNORECASE)

        if not moves:
            print("Warning: No movement commands found in the URScript.")
        
        # Initialize counter for moves
        move_counter = 1

        # Function to add textmsg around moves with correct indentation
        def add_move_texts(match):
            nonlocal move_counter
            move = match.group(0)
            indent = re.match(r'( *)', move).group(0)  # Capture the indentation of the move
            result = (
                f'{indent}socket_send_string("{message_prefix} start {move_counter}")\n'
                f'{move}\n'
                f'{indent}socket_send_string("{message_prefix} end {move_counter}")\n'
            )
            move_counter += 1
            return result

        # Replace all move commands with the new format including the text messages
        formatted_urscript = re.sub(move_pattern, add_move_texts, urscript, flags=re.IGNORECASE)

        # Add socket_open after set_payload line
        set_payload_pattern = r'(set_payload\(Clay_extruderWeight, Clay_extruderCog\))'
        formatted_urscript = re.sub(set_payload_pattern, r'\1\n  socket_open("{}" , 30004)'.format(ip_address), formatted_urscript)

        # Add socket_close before end
        end_pattern = r'(^end\b)'
        formatted_urscript = re.sub(end_pattern, r'  socket_close()\n\1', formatted_urscript, flags=re.MULTILINE)

        # Write the modified URScript to the output file
        with open(output_file_path_1f, "w") as file:
            file.write(formatted_urscript)

        print(f"Formatted URScript has been saved to '{output_file_path_1f}'")

    except Exception as e:
        print(f"An error occurred: {e}")

###Check your IP using ipconfig in your terminal (you need to do that every time!!!)
format_urscript("URscript.txt", "Formatted_URscript.txt","145.94.157.109", "Move")