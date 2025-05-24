# -*- coding: utf-8 -*-
from collections import defaultdict
import re
import os
OUTPUT_DIR = "C:/Users/Owner/Desktop/my_program/kyo-pro/input_data/output"
NET_FILE_PATH = "C:/Users/Owner/Desktop/my_program/kyo-pro/input_data/sample.net"
LST_FILE_PATH ="C:/Users/Owner/Desktop/my_program/kyo-pro/input_data/sample.lst"
CCF_FILE_PATH = "C:/Users/Owner/Desktop/my_program/kyo-pro/input_data/sample.ccf"
def merge_multiline_net_entries(lines):
    merged_lines = []
    current_line = ""
    for line in lines:
        striped = line.strip()
        if not striped:
            continue  # 空行スキップ
        if ';' in striped and not current_line:
            current_line = striped
        else:
            current_line += striped  # 続きの行を結合
        # 行末がカンマで終わっていなければ1ブロック終わりと判断
        if not striped.endswith(','):
            merged_lines.append(current_line)
            current_line = ""
    # 最後に余りがあれば追加
    if current_line:
        merged_lines.append(current_line)
    return merged_lines
def parse_lst_file(lines):
    ref_to_value = {}
    current_value = ""
    current_refdes = []
    last_valid_value = ""
    for line in lines:
        if re.match(r'^\s*-+', line) or re.match(r'^\s*#', line):
            continue
        parts = line.strip().split()
        if len(parts) >= 3:
            # 前に溜まっていたリファレンスがあれば登録
            if current_refdes and last_valid_value:
                for r in current_refdes:
                    ref_to_value[r] = last_valid_value
                current_refdes = []
            refdes_part = parts[2]
            value_part = parts[-1]
            ref_list = [r.strip() for r in refdes_part.split(',') if r.strip()]
            current_refdes.extend(ref_list)
            current_value = value_part
            last_valid_value = value_part
        elif len(parts) == 2:
            ref_to_value[parts[1]] = parts[-1]
        elif ',' in line:
            ref_list = [r.strip() for r in line.strip().split(',') if r.strip()]
            current_refdes.extend(ref_list)
        else:
            if len(parts)==1:
                ref_to_value[parts[0]] = last_valid_value
                print(f'refdes_part:{refdes_part}, parts:{parts} in list')
    # 最後のバッチも忘れずに処理
    if current_refdes and last_valid_value:
        for r in current_refdes:
            ref_to_value[r] = last_valid_value
    return ref_to_value
def convert_net_to_ltspice(input_lines):
    # 部品ごとの {ピン番号: ノード名} マップ
    component_pins = defaultdict(dict)
    node_to_pins = defaultdict(list)  # ノードに接続しているピン情報
    with open(LST_FILE_PATH, encoding="utf-8") as f: # 部品の値を取得するためのファイル
        lst_lines = f.readlines()
    ref_value_dict = parse_lst_file(lst_lines)
    print(f'ref_value_dict["R119"]:{ref_value_dict["R119"]}')
    
    for line in input_lines:
        if ';' not in line:
            continue
        
        # `$` ありでもなしでも処理（ネット名の抽出）
        line = line.strip()
        if line.startswith('$'):
            node_part, pin_list = line[1:].split(';', 1)
            # print(f'node_part:{node_part},pin_list:{pin_list}') # ----------> node_part:N002,pin_list:R1^2,L1^1
        else:
            node_part, pin_list = line.split(';', 1)
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
        # "GND"を含む場合は "0
        def format_node(node):
            if 'GND' in node.upper():
                return '0'
            elif re.fullmatch(r'\d+', node):
                return f"N{node}"
            else:
                return node
            
        def natural_sort_key(pin):
        # 例: "2" → [2], "K" → ["K"], "A1" → ["A", 1]
            return [int(s) if s.isdigit() else s for s in re.findall(r'\d+|[A-Za-z]+', pin)]
        # nodes = [format_node(pin_map[pin]) for pin in sorted(pin_map.keys(), key=lambda x: int(x))]
        nodes = [format_node(pin_map[pin]) for pin in sorted(pin_map.keys(), key=natural_sort_key)]
        
        if comp[0].upper() in {'R', 'L', 'C'} and not (comp[0:3].upper() in {'LED'}):
            value = ref_value_dict[comp]
            result_lines.append(f"{comp} {' '.join(nodes)} {value}")
        elif comp[0].upper() == 'D' and len(nodes) == 2:
            result_lines.append(f"{comp} {' '.join(nodes)} D")  # LTspice組み込み汎用ダイオードモデル
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
    # print(f'ref_value_dict:{ref_value_dict}')
    
    # 例: ファイル読み込みして処理
    print("here")
    with open(NET_FILE_PATH, encoding="utf-8") as f:
        lines = f.readlines()
    input_lines = merge_multiline_net_entries(lines)
    ltspice_netlist = convert_net_to_ltspice(input_lines)  # lines は入力ファイルの各行
    os.makedirs(OUTPUT_DIR, exist_ok=True)  # すでに存在していてもエラーにならない
    
    with open(os.path.join(OUTPUT_DIR, "output_file.cir"), "w", encoding="utf-8") as f:
        for line in ltspice_netlist:
            f.write(line + "\n")
    
if __name__ == "__main__":
    main()
    # print(f'ref_value_dict:{ref_value_dict}')
    
    # 例: ファイル読み込みして処理
    with open(NET_FILE_PATH, encoding="utf-8") as f:
        lines = f.readlines()
    input_lines = merge_multiline_net_entries(lines)
    ltspice_netlist = convert_net_to_ltspice(input_lines)  # lines は入力ファイルの各行
    os.makedirs(OUTPUT_DIR, exist_ok=True)  # すでに存在していてもエラーにならない
    
    with open(os.path.join(OUTPUT_DIR, "output_file.cir"), "w", encoding="utf-8") as f:
        for line in ltspice_netlist:
            f.write(line + "\n")
    
if __name__ == "__main__":
    main()
