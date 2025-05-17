from PyLTSpice import RawRead
import matplotlib.pyplot as plt

# ▼ 読み込む .raw zファイルのパス（自分の環境に合わせて指定）
raw_file = "C:/Users/Owner/Desktop/my_program/kyo-pro/40_LTspice/sample_circuit/sample.raw"

# ▼ PyLTSpiceで .raw ファイルを読み込む
ltr = RawRead(raw_file)

# ▼ 利用可能なトレース（波形）名を確認
trace_names = ltr.get_trace_names()
print("Available Traces:", trace_names)

# ▼ 時間軸データを取得
time = ltr.get_trace('time').get_wave(0)

# ▼ 最初の信号（time以外）をプロットする例
for name in trace_names:
    if name.lower() != 'time':
        signal = ltr.get_trace(name).get_wave(0)
        plt.plot(time, signal, label=name)

# ▼ グラフ表示
plt.title("LTspice Simulation Output")
plt.xlabel("Time [s]")
plt.ylabel("Signal Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
