# -*- coding: utf-8 -*-
from collections import defaultdict
import re
import os
OUTPUT_DIR = "C:/Users/Owner/Desktop/my_program/kyo-pro/40_LTspice/out_put"
NET_FILE_PATH = "C:/Users/Owner/Desktop/my_program/kyo-pro/40_LTspice/py_code/input_sample.net"
 
def convert_net_to_ltspice(input_lines):
    # ���i���Ƃ� {�s���ԍ�: �m�[�h��} �}�b�v
    component_pins = defaultdict(dict)
    node_to_pins = defaultdict(list)  # �m�[�h�ɐڑ����Ă���s�����
    for line in input_lines:
        if not line.startswith('$') or ';' not in line:
            continue
        node_part, pin_list = line.strip()[1:].split(';', 1) 
        # print(f'node_part:{node_part},pin_list:{pin_list}') # ----------> node_part:N002,pin_list:R1^2,L1^1
        for entry in pin_list.split(','): 
            # print(f'entry:{entry}') # ----------> entry:R1^2
            if '^' in entry:
                comp, pin = entry.strip().split('^')
                component_pins[comp][pin] = node_part
                node_to_pins[node_part].append((comp, pin))  
                # print(f'comp:{comp},pin:{pin}') # ----------> comp:R1,pin:2
    # �\�[�g����LTspice�`���֕ϊ�
    result_lines = []
    voltage_sources = set()
    
    for comp, pin_map in component_pins.items():
        # �s���ԍ��Ń\�[�g���A�Ή�����m�[�h���擾
        # "GND"���܂ޏꍇ�� "0" �ɕϊ�
        def format_node(node):
            if 'GND' in node.upper():
                return '0'
            elif re.fullmatch(r'\d+', node):
                return f"N{node}"
            else:
                return node
        nodes = [format_node(pin_map[pin]) for pin in sorted(pin_map.keys(), key=lambda x: int(x))]
        
        # R, L, C �̏ꍇ�̓_�~�[�萔 '777' ��ǉ�
        if comp[0].upper() in {'R', 'L', 'C'}:
            result_lines.append(f"{comp} {' '.join(nodes)} 777")
        else:
            result_lines.append(f"{comp} {' '.join(nodes)}")
    # �d�����m�[�h���o�FV���܂݁A�����i�Ƃ��Ē�`����Ă��Ȃ��m�[�h����Ώۂɂ���
    used_nodes = set(node_to_pins.keys())
    used_components = set(component_pins.keys())
    for node in used_nodes:
        if 'V' in node.upper() and node not in used_components:
            voltage_sources.add(node)
    for v_node in voltage_sources:
        result_lines.append(f"V_{v_node} 0 {v_node} DC 5")  # ���d���l
    # �����̃f�B���N�e�B�u�����p�}�[�J�[
    result_lines.append("* .directive_placeholder")
    result_lines.append(".backanno")
    result_lines.append(".end")
    return result_lines
def main():
    # ��: �t�@�C���ǂݍ��݂��ď���
    with open(NET_FILE_PATH, encoding="utf-8") as f:
        lines = f.readlines()
    ltspice_netlist = convert_net_to_ltspice(lines)  # lines �͓��̓t�@�C���̊e�s
    os.makedirs(OUTPUT_DIR, exist_ok=True)  # ���łɑ��݂��Ă��Ă��G���[�ɂȂ�Ȃ�
    with open(os.path.join(OUTPUT_DIR, "output_file.cir"), "w", encoding="utf-8") as f:
        for line in ltspice_netlist:
            f.write(line + "\n")
    print("11")
if __name__ == "__main__":
    main()
