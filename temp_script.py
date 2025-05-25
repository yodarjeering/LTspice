# -*- coding: utf-8 -*-
from collections import defaultdict
import re
import os
OUTPUT_DIR = "C:/Users/Owner/Desktop/my_program/kyo-pro/input_data/output"
NET_FILE_PATH = "C:/Users/Owner/Desktop/my_program/kyo-pro/input_data/sample.net"
LST_FILE_PATH ="C:/Users/Owner/Desktop/my_program/kyo-pro/input_data/sample.lst"
CCF_FILE_PATH = "C:/Users/Owner/Desktop/my_program/kyo-pro/input_data/sample.ccf"
# 
# 
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
# 
# 
def parse_lst_file_old(lines):
    ref_to_value = {}
    current_refdes = []
    last_valid_value = ""
    for line in lines:
        # 「区切り線やコメントなど、無視すべき行なら処理をスキップする」ためのフィルターです。
        if re.match(r'^\s*-+', line) or re.match(r'^\s*#', line):
            continue
        parts = line.strip().split()
        if len(parts) >= 3:
            # 前に溜まっていたリファレンスがあれば登録
            if current_refdes and last_valid_value:
                for r in current_refdes:
                    ref_to_value[r] = last_valid_value
                current_refdes = []
            
            # 部品のリファレンス番号と値を取得
            refdes_part = parts[2]
            value_part = parts[-1]
            ref_list = [r.strip() for r in refdes_part.split(',') if r.strip()]
            current_refdes.extend(ref_list)
            last_valid_value = value_part
        elif len(parts) == 2:
            ref_to_value[parts[1]] = parts[-1]
            #   
        elif ',' in line:
            ref_list = [r.strip() for r in line.strip().split(',') if r.strip()]
            current_refdes.extend(ref_list)
        else:
            if len(parts)==1:
                ref_to_value[parts[0]] = last_valid_value
    # 最後のバッチも忘れずに処理
    if current_refdes and last_valid_value:
        for r in current_refdes:
            ref_to_value[r] = last_valid_value
    return ref_to_value
# 
# ノード情報を修正する関数
def format_node(node):
    if re.fullmatch(r'\d+', node):
        return f"N{node}"
    else:
        return node
# 部品ごとに修正を入れる関数
def get_prefix(comp,needs_value):
    for prefix in sorted(needs_value.union(
        {'CN','D','IC','LED','PAT','PC','REG','SW','T','TR','X','ZNR','ZD','MOD','JP'}
        ), key=lambda x: -len(x)):
        if comp.upper().startswith(prefix):
            return prefix
    return comp[0].upper()
# 数字、文字が混在していてもソートできる関数
def natural_sort_key(pin):
    return [int(s) if s.isdigit() else s for s in re.findall(r'\d+|[A-Za-z]+', pin)]
# 

def parse_lst_file(lines):
    ref_to_value = {}
    ref_to_partspec = {}

    current_part = ""
    current_value = ""
    current_refs = []

    for line in lines:
        # ヘッダーや区切り線をスキップ
        if re.match(r'^\s*[-#]', line):
            continue

        parts = line.strip().split()

        # 新しい部品定義行（4列以上ある）
        if len(parts) >= 4:
            # 現在のリストがあれば保存
            if current_refs and current_part and current_value:
                for r in current_refs:
                    ref_to_value[r] = current_value
                    ref_to_partspec[r] = current_part
                current_refs = []

            refdes_raw = parts[2]
            current_part = parts[3]
            current_value = parts[4] if len(parts) >= 5 else ""
            current_refs = [r.strip() for r in refdes_raw.split(',') if r.strip()]

        # 継続行（部品番号が複数行にまたがる）
        elif ',' in line:
            print(f'parts:{parts}')
            continued_refs = [r.strip() for r in line.strip().split(',') if r.strip()]
            current_refs.extend(continued_refs)

    # 最後のブロックを保存
    if current_refs and current_part and current_value:
        for r in current_refs:
            ref_to_value[r] = current_value
            ref_to_partspec[r] = current_part

    return ref_to_value, ref_to_partspec

# netファイルをltspice記述に変換する関数
def convert_net_to_ltspice(input_lines,ref_value_dict,ref_partname_dict):
    # 部品ごとの {ピン番号: ノード名} マップ
    component_pins = defaultdict(dict)
    node_to_pins = defaultdict(list)  # ノードに接続しているピン情報

    label_nodes = set()
    for line in input_lines:
        if ';' not in line:
            continue
        line = line.strip()
        if line.startswith('$'):
            node_part, pin_list = line[1:].split(';', 1)
        else:
            node_part, pin_list = line.split(';', 1)
            label_nodes.add(node_part)  # $がない＝ラベル的ノードとして扱う
        for entry in pin_list.split(','):
            if '^' in entry:
                comp, pin = entry.strip().split('^')
                component_pins[comp][pin] = node_part
                node_to_pins[node_part].append((comp, pin))
    result_lines = []
    for comp, pin_map in component_pins.items():
        nodes = [format_node(pin_map[pin]) for pin in sorted(pin_map.keys(), key=natural_sort_key)]
        # 定数設定が必要な部品記号セット, TBD:将来的にユーザからの入力に対応できるようにする
        needs_value = {'C', 'L', 'R', 'RA', 'RCU'}
        prefix = get_prefix(comp, needs_value)
        part_name = ref_partname_dict[comp]

        if prefix in needs_value:    
            value = ref_value_dict[comp]
            result_lines.append(f"{comp} {' '.join(nodes)} {value} *parts_name:{part_name}")

        elif prefix in {'D', 'LED', 'ZD'} and len(nodes) == 2:
            if 'A' in pin_map and 'K' in pin_map:
                a_node = format_node(pin_map['A'])
                k_node = format_node(pin_map['K'])
                result_lines.append(f"{comp} {a_node} {k_node} D **parts_name:{part_name}")
            else:
                # 仮に1→A、2→Kと仮定
                a_node = format_node(pin_map.get('1', list(pin_map.values())[0]))
                k_node = format_node(pin_map.get('2', list(pin_map.values())[1]))
                result_lines.append(f"{comp} {a_node} {k_node} D *POLARITY_CHECK **parts_name:{part_name}")
        # elif prefix == 'D' and len(nodes) == 2:
        #     result_lines.append(f"{comp} {' '.join(nodes)} D")
        else:
            result_lines.append(f"{comp} {' '.join(nodes)} **parts_name:{part_name}")
    # ラベルノードの処理
    label_nodes_list = sorted(label_nodes)
    
    result_lines.append("*--BEGIN_LABEL_NODES--")
    for label_node in label_nodes_list:
        result_lines.append(f"V_{label_node} 0 {label_node} DC 5")
    result_lines.append("*--END_LABEL_NODES--")
    result_lines.append("* .directive_placeholder")
    result_lines.append(".backanno")
    result_lines.append(".end")
    return result_lines
# 
#
def main():
    with open(NET_FILE_PATH, encoding="utf-8") as f:
        lines = f.readlines()
    input_lines = merge_multiline_net_entries(lines)
    
    with open(LST_FILE_PATH, encoding="utf-8") as f:  # 部品の値を取得するためのファイル
        lst_lines_tmp = f.readlines()
    
    # 「区切り線やコメントなど、無視すべき行なら処理をスキップする」ためのフィルターです。
    # lst_linesの前処理
    lst_lines = []
    for line in lst_lines_tmp:
        if 'Page' in line:
            continue
        lst_lines.append(line)
    
    ref_value_dict,ref_partname_dict = parse_lst_file(lst_lines)

    ltspice_netlist = convert_net_to_ltspice(input_lines,ref_value_dict,ref_partname_dict)  # lines は入力ファイルの各行
    os.makedirs(OUTPUT_DIR, exist_ok=True)  # すでに存在していてもエラーにならない

    with open(os.path.join(OUTPUT_DIR, "output_file.cir"), "w", encoding="utf-8") as f:
        for line in ltspice_netlist:
            f.write(line + "\n")
    
# pythonのおしゃんなメイン文の実行の仕方
if __name__ == "__main__":
    main()
    
