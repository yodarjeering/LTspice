# -*- coding: utf-8 -*-
from collections import defaultdict
import re
import os
OUTPUT_DIR = "C:/Users/Owner/Desktop/my_program/kyo-pro/40_LTspice/out_put"
NET_FILE_PATH = "C:/Users/Owner/Desktop/my_program/kyo-pro/40_LTspice/py_code/input_sample.net"
 
def convert_net_to_ltspice(input_lines):
    # 部品ごとの {ピン番号: ノード名} マップ
    component_pins = defaultdict(dict)
    node_to_pins = defaultdict(list)  # ノードに接続しているピン情報
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
    # ソートしてLTspice形式へ変換
    result_lines = []
    voltage_sources = set()
    
    for comp, pin_map in component_pins.items():
        # ピン番号でソートし、対応するノードを取得
        # "GND"を含む場合は "0" に変換
        def format_node(node):
            if 'GND' in node.upper():
                return '0'
            elif re.fullmatch(r'\d+', node):
                return f"N{node}"
            else:
                return node
        nodes = [format_node(pin_map[pin]) for pin in sorted(pin_map.keys(), key=lambda x: int(x))]
        
        # R, L, C の場合はダミー定数 '777' を追加
        if comp[0].upper() in {'R', 'L', 'C'}:
            result_lines.append(f"{comp} {' '.join(nodes)} 777")
        else:
            result_lines.append(f"{comp} {' '.join(nodes)}")
    # 電圧源ノード検出：Vを含み、かつ部品として定義されていないノード名を対象にする
    used_nodes = set(node_to_pins.keys())
    used_components = set(component_pins.keys())
    for node in used_nodes:
        if 'V' in node.upper() and node not in used_components:
            voltage_sources.add(node)
    for v_node in voltage_sources:
        result_lines.append(f"V_{v_node} 0 {v_node} DC 5")  # 仮電圧値
    # 将来のディレクティブ検索用マーカー
    result_lines.append("* .directive_placeholder")
    result_lines.append(".backanno")
    result_lines.append(".end")
    return result_lines
def main():
    # 例: ファイル読み込みして処理
    with open(NET_FILE_PATH, encoding="utf-8") as f:
        lines = f.readlines()
    ltspice_netlist = convert_net_to_ltspice(lines)  # lines は入力ファイルの各行
    os.makedirs(OUTPUT_DIR, exist_ok=True)  # すでに存在していてもエラーにならない
    with open(os.path.join(OUTPUT_DIR, "output_file.cir"), "w", encoding="utf-8") as f:
        for line in ltspice_netlist:
            f.write(line + "\n")
    print("11")
if __name__ == "__main__":
    main()
