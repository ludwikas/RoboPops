#### UPDDATED: REMOVED FUNCTION TO SEND TO ROBOT CONTROLLER

import W3C_A_Calculate_StepDelay_Interpolate
import W3C_A_Format_dynamic_voltage_values
import W3CNEW_A_SendNewL_ExtractSpeeds
import W3A_A_Format_TCP

robot_ip = "192.168.40.128"

ρ = 0.002015                                                          # g/mm^3
m = 6.7                                                               # g
V_p = W3C_A_Calculate_StepDelay_Interpolate.calculate_Vp(ρ, m)        # mm^3 per 1 revolution
w_target = 3.5                                                        # mm
h_target = 3.4                                                        # mm
Ns = 1035                                                             # unit

new_min = 0.475
new_max = 0

ip_address = "145.94.133.95"
notification_port = 30004
file_path_urscript_newl = "URscript_newmovel.txt"
output_file_path_2f = "Formatted_URscript2.txt"
file_path_2f = "Formatted_URscript2.txt"
output_file_path = "Joint_Speeds.txt"
output_file_path_lspeed = "Linear_speeds_2.txt"
output_file_path_FinalFormat = "FinalFormat_URscript.txt"
        


W3A_A_Format_TCP.format_urscript(file_path_urscript_newl, output_file_path_2f, ip_address, message_prefix="Move")
total_moves = W3CNEW_A_SendNewL_ExtractSpeeds.extract_total_moves(file_path_2f)
W3CNEW_A_SendNewL_ExtractSpeeds.send_urscript(file_path_2f, robot_ip)
joint_speeds_data = W3CNEW_A_SendNewL_ExtractSpeeds.monitor_joint_speeds(robot_ip, notification_port=notification_port, total_moves=total_moves)
W3CNEW_A_SendNewL_ExtractSpeeds.write_joint_speeds_to_file(joint_speeds_data)

cartesian_speeds = W3CNEW_A_SendNewL_ExtractSpeeds.extract_cartesian_speeds(output_file_path)
v_linear = W3CNEW_A_SendNewL_ExtractSpeeds.calculate_linear_speeds(cartesian_speeds)
W3CNEW_A_SendNewL_ExtractSpeeds.write_speeds_in_file(v_linear, output_file_path_lspeed)

v_new = W3C_A_Calculate_StepDelay_Interpolate.read_v_values(output_file_path_lspeed)
step_delay_values = W3C_A_Calculate_StepDelay_Interpolate.calculate_step_delay(Ns, V_p, w_target, h_target, v_new)
old_max = W3C_A_Calculate_StepDelay_Interpolate.sort_max_delay(step_delay_values)
old_min = W3C_A_Calculate_StepDelay_Interpolate.sort_min_delay(step_delay_values)
voltage_values = W3C_A_Calculate_StepDelay_Interpolate.map_step_delay_to_voltage(step_delay_values, old_min, old_max, new_min, new_max)
W3C_A_Format_dynamic_voltage_values.format_urscript_voltages(file_path_urscript_newl, output_file_path_FinalFormat, voltage_values)