import W3C_A_Calculate_StepDelay_Interpolate
import W3C_A_Format_dynamic_voltage_values
import W3A_A_Send_Collect_Main_and_Intervals

robot_ip = "192.168.40.128"

ρ = 0.002015                                                          # g/mm^3
m = 6.7                                                               # g
V_p = W3C_A_Calculate_StepDelay_Interpolate.calculate_Vp(ρ, m)        # mm^3 per 1 revolution
w_target = 5.5                                                        # mm
h_target = 5                                                          # mm
Ns = 1035                                                             # unit

old_min = 0
old_max = 60000
new_min = 0.5
new_max = 0

file_path_speed_seq = "Speeds_sequential_idx.txt"
file_path_urscript_newl = "URscript_newmovel.txt"
output_file_path_FinalFormat = "FinalFormat_URscript.txt"
file_path_FinalFormat = "FinalFormat_URscript.txt"


v_new = W3C_A_Calculate_StepDelay_Interpolate.read_v_values(file_path_speed_seq)
step_delay_values = W3C_A_Calculate_StepDelay_Interpolate.calculate_step_delay(Ns, V_p, w_target, h_target, v_new)
voltage_values = W3C_A_Calculate_StepDelay_Interpolate.map_step_delay_to_voltage(step_delay_values, old_min, old_max, new_min, new_max)
W3C_A_Format_dynamic_voltage_values.format_urscript_voltages(file_path_urscript_newl, output_file_path_FinalFormat, voltage_values)
W3A_A_Send_Collect_Main_and_Intervals.send_urscript(file_path_FinalFormat, robot_ip, 30002)