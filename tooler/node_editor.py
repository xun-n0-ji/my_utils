import tkinter as tk

class NodeEditor:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # ノードを保存するためのリスト
        self.nodes = []
        self.lines = []

        # ノードを作成
        self.create_node(100, 100, "Node 1")
        self.create_node(300, 200, "Node 2")

        # 接続線を作成
        self.connect_nodes(self.nodes[0], self.nodes[1])

        # ドラッグイベントを設定
        self.selected_node = None
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def create_node(self, x, y, text):
        """ノードを作成してCanvasに追加"""
        size = 80
        node = {
            "id": len(self.nodes),
            "x": x,
            "y": y,
            "rect": self.canvas.create_rectangle(x, y, x + size, y + size, fill="lightblue"),
            "text": self.canvas.create_text(x + size // 2, y + size // 2, text=text)
        }
        self.nodes.append(node)

    def connect_nodes(self, node1, node2):
        """2つのノードを接続する線を作成"""
        x1 = node1["x"] + 40
        y1 = node1["y"] + 40
        x2 = node2["x"] + 40
        y2 = node2["y"] + 40
        line = self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST)
        self.lines.append(line)

    def on_click(self, event):
        """クリックでノードを選択"""
        for node in self.nodes:
            if self.canvas.find_withtag(tk.CURRENT):
                if self.canvas.find_withtag(tk.CURRENT)[0] == node["rect"]:
                    self.selected_node = node
                    break

    def on_drag(self, event):
        """ドラッグでノードを移動"""
        if self.selected_node:
            dx = event.x - self.selected_node["x"]
            dy = event.y - self.selected_node["y"]
            self.canvas.move(self.selected_node["rect"], dx, dy)
            self.canvas.move(self.selected_node["text"], dx, dy)
            self.selected_node["x"] = event.x
            self.selected_node["y"] = event.y

            # 接続線を更新
            self.update_lines()

    def update_lines(self):
        """ノード移動後、接続線を更新"""
        for i, line in enumerate(self.lines):
            node1 = self.nodes[i]
            node2 = self.nodes[(i + 1) % len(self.nodes)]
            x1 = node1["x"] + 40
            y1 = node1["y"] + 40
            x2 = node2["x"] + 40
            y2 = node2["y"] + 40
            self.canvas.coords(line, x1, y1, x2, y2)

if __name__ == "__main__":
    root = tk.Tk()
    editor = NodeEditor(root)
    root.mainloop()
