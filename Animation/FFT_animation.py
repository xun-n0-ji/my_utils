import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 画像を読み込み
img = plt.imread(r"C:\Users\pshun\Documents\python\tkinter_killingtime\SAM_tools\test.png")  # 2値化画像
img_fft = np.fft.fft2(img)  # フーリエ変換

# 正弦波を描くための基準波形
def generate_wave(freq, amp, size):
    x = np.linspace(0, 2 * np.pi, size)
    return amp * np.sin(freq * x)

# アニメーション用のフレームを作成
fig, ax = plt.subplots()

def update(frame):
    # フレームに応じて周波数や振幅を変化させた波形を生成
    freq = frame * 0.1  # 周波数を徐々に増加
    amp = frame * 0.05  # 振幅も徐々に増加
    wave = generate_wave(freq, amp, img.shape[1])
    
    # 画像をフーリエ逆変換を使って徐々に復元
    img_reconstructed = np.fft.ifft2(img_fft * wave)
    
    # 表示
    ax.imshow(np.abs(img_reconstructed), cmap='gray')

# アニメーションを作成
ani = FuncAnimation(fig, update, frames=100, interval=100)

# アニメーションを保存または表示
ani.save('animation.gif', writer='imagemagick')
plt.show()
