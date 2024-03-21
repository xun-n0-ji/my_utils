import tkinter as tk
import time

def rgb_rgb2code(R, G, B):
    rgb_code = '#'
    for c in [R, G, B]:
        rgb_code += f"{c:0=2x}"
    return rgb_code

def rgb_code2rgb(rgb_code):
    r, g, b = [rgb_code[1+2*i:3+2*i] for i in range(3)][:]
    rgb = []
    for c in [r, g, b]:
        rgb.append(int(c, 16))
    return rgb

# referred to https://www.ishikawasekkei.com/index.php/2020/03/30/python-tkinter-predefined-color/
def rgb_name2code(color_name):
    root = tk.Tk()
    rgb = root.winfo_rgb(color_name)
    rgb_code  = "#%02X%02X%02X"%(rgb[0]//256, rgb[1]//256, rgb[2]//256)
    root.destroy()
    return rgb_code

# too weight! ~ 0.1s
def rgb_name2rgb(color_name):
    start = time.perf_counter()
    root = tk.Tk()
    rgb = root.winfo_rgb(color_name)
    root.destroy()
    print(time.perf_counter() - start)
    return list(map(lambda c:c//256, rgb))

if __name__ == '__main__':
    #print(rgb_name2code("blue"))
    #print(rgb_name2rgb("blue"))
    print(rgb_code2rgb("#0000FF"))