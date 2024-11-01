import math

def show_loading_animation(root, canvas):
    # params for drawing small circles
    radius = 20  # radius 
    circle_radius = 8  # radius of small circles
    num_circles = 8  # number of circles

    # calculation for animation
    angle_step = 360 / num_circles
    circles = []

    for i in range(num_circles):
        angle = math.radians(i * angle_step)
        x = 100 + radius * math.cos(angle)
        y = 100 + radius * math.sin(angle)
        circle = canvas.create_oval(x - circle_radius, y - circle_radius, x + circle_radius, y + circle_radius, fill="white", outline="white")
        circles.append(circle)

    # update animation
    def animate_circle(step=0):
        for i in range(num_circles):
            offset = (i + step) % num_circles
            #color_intensity = int(255 * (1 - offset / num_circles))
            color_intensity = int(255 * (offset / num_circles))
            #color = f'#{color_intensity:02x}{color_intensity:02x}{color_intensity:02x}'
            color = f'#{color_intensity:02x}{255:02x}{255:02x}'
            canvas.itemconfig(circles[i], fill=color)

        root.after(100, animate_circle, step + 1)
    
    animate_circle()  # start animation

if __name__ == "__main__":
    import tkinter as tk
    root = tk.Tk()
    loading_canvas = tk.Canvas(root, width=200, height=200, bg='white', highlightthickness=0)
    loading_canvas.pack()
    show_loading_animation(root, loading_canvas)
    root.mainloop()