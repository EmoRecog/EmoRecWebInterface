import pyaudio
import pprint

def get_ip_device_index(p, input_name):
    pp = pprint.PrettyPrinter(indent=4)
    for x in range(0,p.get_device_count()):
        info = p.get_device_info_by_index(x)    
        # pp.pprint(p.get_device_info_by_index(x))
        if input_name in info["name"]:
            # pp.pprint(p.get_device_info_by_index(x))
            chosen_ip_device_index = info["index"]
            # chosen_ip_device_name = info["name"]
        
    return chosen_ip_device_index


def get_op_device_index(p, output_name):
    pp = pprint.PrettyPrinter(indent=4)
    for x in range(0,p.get_device_count()):
        info = p.get_device_info_by_index(x)    
        # pp.pprint(p.get_device_info_by_index(x))        
        if output_name in info["name"]:
                chosen_op_device_index = info["index"]
                # chosen_op_device_name = info["name"]
    return chosen_op_device_index