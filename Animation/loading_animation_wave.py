import tkinter as tk
import math

def show_gaussian_wave_interference_animation(canvas, line_length, amplitude, frequency, speed, sigma):
    # 直線の中央を基点として配置
    start_x = 70
    end_x = start_x + line_length
    y_center = 150  # 画面の中央の高さ
    points = []  # 直線の各ポイント

    # 線を描画する初期ポイントを設定
    num_points = 250  # ポイントの数
    step = line_length / num_points

    # 初期位置に直線を描画（水平な線）
    for i in range(num_points + 1):
        x = start_x + i * step
        points.append((x, y_center))
    
    # 線を描画
    line = canvas.create_line(points, fill="white", width=2)

    # ガウシアン関数の定義（位置によって振幅を変調するために使用）
    def gaussian(x, mu, sigma):
        return math.exp(-((x - mu) ** 2) / (2 * sigma ** 2))

    # 波の振動をアニメーション
    def animate_wave(t=0):
        new_points = []
        for i, (x, _) in enumerate(points):
            # 左からの波と右からの波の干渉
            offset_left = math.sin((x - start_x) * frequency + t * speed) * amplitude * gaussian(x, (start_x+(t * 5*speed + (end_x-start_x)/2)%(end_x-start_x+1+2*3*sigma)-3*sigma), sigma)
            offset_right = math.sin((end_x - x) * frequency + t * speed) * amplitude * gaussian(x,  (end_x-((t * 5*speed + (end_x-start_x)/2)%(end_x-start_x+1+2*3*sigma))+3*sigma), sigma)
            # 干渉波は左右の波の重ね合わせ
            combined_offset = offset_left + offset_right
            new_y = y_center + combined_offset
            new_points.append((x, new_y))
        
        # 直線を更新
        canvas.coords(line, *sum(new_points, ()))

        # 次のフレームを呼び出し
        canvas.after(50, animate_wave, t + 1)

    animate_wave()  # アニメーション開始

# GUI設定
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gaussian Envelope Wave Interference Animation")

    # キャンバス作成
    canvas = tk.Canvas(root, width=600, height=300, bg='black')
    canvas.pack()

    # ガウシアン包絡波のアニメーションを開始
    show_gaussian_wave_interference_animation(canvas, line_length=500, amplitude=60, frequency=0.25, speed=0.3, sigma=70)

    root.mainloop()
