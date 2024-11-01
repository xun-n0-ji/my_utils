import tkinter as tk
from tkinter import Toplevel

class CustomMenu:
    def __init__(self, root, items, width=180, bg_color="#f0f0f0", highlight_color="#c0c0c0", border_color="#a0a0a0", transparent_color="#00ff00", radius=10):
        self.root = root
        self.items = items
        self.width = width
        self.bg_color = bg_color
        self.highlight_color = highlight_color
        self.border_color = border_color
        self.transparent_color = transparent_color
        self.radius = radius
        self.menu = None
        self.submenu = None
        self.submenu_active = False  # フラグを初期化

        # 右クリックでメニューを表示
        self.root.bind("<Button-3>", self.show_menu)

        # メインウィンドウが最小化されたときにメニューを閉じる
        self.root.bind("<Unmap>", self.on_root_minimize)

    def show_menu(self, event):
        if self.menu:
            self.menu.destroy()

        # メインメニューの作成と最前面設定
        self.menu = Toplevel(self.root)
        self.menu.overrideredirect(True)
        self.menu.geometry(f"{self.width}x{40 + 40 * len(self.items)}+{event.x_root}+{event.y_root}")
        self.menu.config(bg=self.transparent_color)
        self.menu.wm_attributes("-transparentcolor", self.transparent_color)

        canvas = tk.Canvas(self.menu, width=self.width, height=40 + 40 * len(self.items), bg=self.transparent_color, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # メインメニューの項目を描画
        self.show_menu_items(canvas, self.items)

    def show_menu_items(self, canvas, items, x_offset=0):
        """指定されたキャンバスにメニュー項目を描画"""
        height = 40 * len(items)
        self.create_rounded_rectangle(canvas, self.width, height, self.radius, self.bg_color, border_color=self.border_color)
        
        for index, (text, command) in enumerate(items):
            display_text = f"{text} {'▸' if isinstance(command, list) else ''}"

            # Canvasを使用して角丸ハイライトを表示
            item_canvas = tk.Canvas(canvas, width=self.width - 20, height=30, bg=self.bg_color, highlightthickness=0)
            item_canvas.place(x=10 + x_offset, y=10 + index * 30)

            # デフォルトの角丸背景
            self.create_rounded_rectangle(item_canvas, self.width - 20, 30, self.radius, self.bg_color)
            item_canvas.text_id = item_canvas.create_text(20, 15, text=display_text, anchor="w", font=("Arial", 10))

            # ハイライト効果とコマンドのバインド
            item_canvas.bind("<Enter>", lambda e, ic=item_canvas, cmd=command: self.on_item_enter(e, ic, cmd))
            item_canvas.bind("<Leave>", lambda e, ic=item_canvas, cmd=command: self.on_item_leave(e, ic, cmd))
            if not isinstance(command, list):
                item_canvas.bind("<Button-1>", lambda e, cmd=command: self.execute_command(cmd))

    def on_item_enter(self, event, item_canvas, command):
        # ハイライト色で角丸背景を描画
        self.highlight_item(item_canvas)
        if isinstance(command, list):
            self.show_submenu(event, command)

    def on_item_leave(self, event, item_canvas, command):
        # デフォルト色に戻す
        self.unhighlight_item(item_canvas)
        if isinstance(command, list):
            self.hide_submenu()

    def show_submenu(self, event, sub_items):
        if self.submenu:
            self.submenu.destroy()

        # サブメニューを生成し、メインメニューの一段階下に設定
        self.submenu = Toplevel(self.menu)
        self.submenu.overrideredirect(True)
        x, y = event.widget.winfo_rootx() + 140, event.widget.winfo_rooty()
        self.submenu.geometry(f"{self.width}x{40 * len(sub_items)}+{x}+{y}")
        self.submenu.config(bg=self.transparent_color)
        self.submenu.wm_attributes("-transparentcolor", self.transparent_color)

        canvas = tk.Canvas(self.submenu, width=self.width, height=40 * len(sub_items), bg=self.transparent_color, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # サブメニューの項目を描画
        self.show_menu_items(canvas, sub_items)

        # サブメニューにカーソルが入ったらフラグをTrueに、出たらFalseに
        self.submenu.bind("<Enter>", lambda e: self.set_submenu_active(True))
        self.submenu.bind("<Leave>", lambda e: self.set_submenu_active(False))

    def hide_submenu(self):
        # サブメニューにカーソルがない場合にのみ閉じる
        if self.submenu and not self.submenu_active:
            self.root.after(300, self._destroy_submenu)

    def _destroy_submenu(self):
        self.submenu.destroy()

    def set_submenu_active(self, active):
        """サブメニューの表示フラグを設定"""
        self.submenu_active = active

    def highlight_item(self, item_canvas):
        # ハイライト色の角丸背景を描画
        item_canvas.delete("highlight")
        self.create_rounded_rectangle(item_canvas, self.width - 20, 30, self.radius, self.highlight_color, tag="highlight")
        item_canvas.lift(item_canvas.text_id)

    def unhighlight_item(self, item_canvas):
        # デフォルト色の角丸背景を描画
        item_canvas.delete("highlight")
        self.create_rounded_rectangle(item_canvas, self.width - 20, 30, self.radius, self.bg_color, tag="highlight")
        item_canvas.lift(item_canvas.text_id)

    def create_rounded_rectangle(self, canvas, width, height, radius, color, border_color=None, tag=None):
        if border_color:
            canvas.create_rectangle(radius, radius, width - radius, height - radius, fill=border_color, outline=border_color, tag=tag)
        
        # カーブ部分を描画
        canvas.create_arc((5, 5, radius*2, radius*2), start=90, extent=90, fill=color, outline=color, tag=tag)
        canvas.create_arc((width-radius*2, 5, width-5, radius*2), start=0, extent=90, fill=color, outline=color, tag=tag)
        canvas.create_arc((5, height-radius*2, radius*2, height-5), start=180, extent=90, fill=color, outline=color, tag=tag)
        canvas.create_arc((width-radius*2, height-radius*2, width-5, height-5), start=270, extent=90, fill=color, outline=color, tag=tag)
        
        # 四角部分を描画
        canvas.create_rectangle(radius, 5, width-radius, height-5, fill=color, outline=color, tag=tag)
        canvas.create_rectangle(5, radius, width-5, height-radius, fill=color, outline=color, tag=tag)

    def execute_command(self, command):
        if callable(command):
            command()
        if self.menu:
            self.menu.destroy()
        if self.submenu:
            self.submenu.destroy()

    def on_root_minimize(self, event):
        if self.menu:
            self.menu.destroy()
        if self.submenu:
            self.submenu.destroy()

# 使用例
def option1_action():
    print("Option 1 selected")

def option2_action():
    print("Option 2 selected")

root = tk.Tk()
root.config(bg="black")
root.geometry("400x300")

# カスタムメニューのインスタンスを作成
items = [
    ("Option 1", option1_action),
    ("Class", [("Suboption 1", option1_action), ("Suboption 2", option2_action)]),
    ("Option 2", option2_action)
]
custom_menu = CustomMenu(root, items)

root.mainloop()
