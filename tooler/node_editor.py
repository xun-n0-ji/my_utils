import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance


class Node:
    """ノードを表すクラス"""
    def __init__(self, editor, x, y, node_type, label):
        self.editor = editor
        self.x = x
        self.y = y
        self.node_type = node_type
        self.label = label
        self.connections = []  # 接続先ノードのリスト
        self.in_circle = None
        self.out_circle = None

        # ノード本体（角丸四角を描画）
        self.rect = self.editor.canvas.create_rounded_rectangle(
            x, y, x + 120, y + 60, fill="#2c3e50", outline="#ecf0f1", width=2, radius=10, tags="node"
        )
        self.text = self.editor.canvas.create_text(
            x + 60, y + 30, text=label, fill="#ecf0f1", tags="node"
        )

        # 入力円
        if self.node_type != "input":
            self.in_circle = self.editor.canvas.create_oval(
                x - 5, y + 25, x + 5, y + 35, fill="#3498db", outline="#2980b9", width=2, tags="circle"
            )
            self.editor.canvas.tag_bind(self.in_circle, "<Button-1>", self.start_connection)
            self.editor.canvas.tag_bind(self.in_circle, "<B1-Motion>", self.drag_connection)
            self.editor.canvas.tag_bind(self.in_circle, "<ButtonRelease-1>", self.end_connection)

        # 出力円
        if self.node_type != "output":
            self.out_circle = self.editor.canvas.create_oval(
                x + 115, y + 25, x + 125, y + 35, fill="#e74c3c", outline="#c0392b", width=2, tags="circle"
            )
            self.editor.canvas.tag_bind(self.out_circle, "<Button-1>", self.start_connection)
            self.editor.canvas.tag_bind(self.out_circle, "<B1-Motion>", self.drag_connection)
            self.editor.canvas.tag_bind(self.out_circle, "<ButtonRelease-1>", self.end_connection)

        # ドラッグ移動
        self.editor.canvas.tag_bind(self.rect, "<B1-Motion>", self.drag)
        self.editor.canvas.tag_bind(self.text, "<B1-Motion>", self.drag)

    def drag(self, event):
        """ノードをドラッグ移動"""
        dx = event.x - self.x - 60
        dy = event.y - self.y - 30
        self.x += dx
        self.y += dy

        self.editor.canvas.move(self.rect, dx, dy)
        self.editor.canvas.move(self.text, dx, dy)
        if self.in_circle:
            self.editor.canvas.move(self.in_circle, dx, dy)
        if self.out_circle:
            self.editor.canvas.move(self.out_circle, dx, dy)

        # 接続された線を更新
        self.editor.update_lines()

    def start_connection(self, event):
        """接続開始（線を生成）"""
        current_circle = self.editor.canvas.find_withtag("current")[0]
        if current_circle == self.in_circle:
            # 入力円の場合、既存接続を解除
            self.disconnect()
        else:
            # 出力円の場合、接続開始
            self.editor.current_line = self.editor.canvas.create_line(
                event.x, event.y, event.x, event.y, fill="white", arrow=tk.LAST, tags="dynamic_line"
            )
            self.editor.connection_start_node = self

    def drag_connection(self, event):
        """接続中の線を更新（マウス位置に追従）"""
        if self.editor.current_line:
            self.editor.canvas.coords(
                self.editor.current_line,
                self.x + 120,
                self.y + 30,
                event.x,
                event.y,
            )

    def end_connection(self, event):
        """接続を確定"""
        if self.editor.current_line:
            overlapping_items = self.editor.canvas.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
            for item in overlapping_items:
                target_node = self.editor.get_node_from_circle(item)
                if target_node and target_node != self:
                    self.connect_to(target_node)
                    self.editor.update_sequence()
                    break

            # 線を削除（確定または失敗時）
            self.editor.canvas.delete(self.editor.current_line)
            self.editor.current_line = None
            self.editor.connection_start_node = None

    def disconnect(self):
        """既存接続を解除"""
        lines_to_remove = []

        for line in self.editor.lines:
            if line[0] == self:  # 出力ノードの場合
                if line[1] in self.connections:
                    self.connections.remove(line[1])
                self.editor.canvas.delete(line[2])
                lines_to_remove.append(line)

            elif line[1] == self:  # 入力ノードの場合
                if self in line[0].connections:
                    line[0].connections.remove(self)
                self.editor.canvas.delete(line[2])
                lines_to_remove.append(line)

        # キャンバスと接続リストから削除
        for line in lines_to_remove:
            self.editor.lines.remove(line)

        # 接続順序を更新
        self.editor.update_sequence()

    def connect_to(self, other_node):
        """他のノードとの接続を作成"""
        # 重複接続を防ぐ　<- これいるかな？
        if other_node not in self.connections:
            self.connections.append(other_node)

        # キャンバスに線を描画
        x1, y1 = self.x + 120, self.y + 30  # 出力円の位置
        x2, y2 = other_node.x, other_node.y + 30  # 入力円の位置
        line = self.editor.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill="white", tags="connection")
        
        # 接続情報を保存
        self.editor.lines.append((self, other_node, line))


class NodeEditor(tk.Toplevel):
    """ノードエディタのクラス"""
    def __init__(self, master, apply_processing_callback):
        super().__init__(master)
        self.title("ノードエディタ")
        self.geometry("800x600")
        self.canvas = CustomCanvas(self, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.nodes = []
        self.lines = []  # 接続線のリスト
        self.current_line = None
        self.connection_start_node = None
        self.apply_processing_callback = apply_processing_callback
        self.sequence = []  # ノードの順序

        # 初期ノード
        self.input_node = self.add_node(50, 200, "input", "Input")
        self.output_node = self.add_node(650, 200, "output", "Output")
        
        # 入力ノードと出力ノードを接続
        self.connect_nodes(self.input_node, self.output_node)

        # 接続順序を更新
        self.update_sequence()

        # 右クリックメニュー
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="グレースケール", command=lambda: self.add_processing_node("grayscale"))
        self.menu.add_command(label="明るさ調整", command=lambda: self.add_processing_node("brightness"))

        self.canvas.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """右クリックメニューを表示"""
        self.menu.post(event.x_root, event.y_root)

    def add_node(self, x, y, node_type, label):
        """新しいノードを追加"""
        node = Node(self, x, y, node_type, label)
        self.nodes.append(node)
        return node

    def add_processing_node(self, processing_type):
        """画像処理ノードを追加"""
        x, y = self.input_node.x + 150, self.input_node.y + 100 * len(self.nodes)
        self.add_node(x, y, "processing", processing_type.capitalize())

    def get_node_from_circle(self, circle_id):
        """円のIDからノードを取得"""
        for node in self.nodes:
            if node.in_circle == circle_id or node.out_circle == circle_id:
                return node
        return None
    
    def connect_nodes(self, source_node, target_node):
        """ノード間の接続を作成"""
        source_node.connections.append(target_node)
        x1, y1 = source_node.x + 120, source_node.y + 30  # 出力円の位置
        x2, y2 = target_node.x, target_node.y + 30       # 入力円の位置
        line = self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill="white", tags="connection")
        self.lines.append((source_node, target_node, line))

    def update_lines(self):
        """接続された線を再描画"""
        for source, target, line in self.lines:
            x1, y1 = source.x + 120, source.y + 30
            x2, y2 = target.x, target.y + 30
            self.canvas.coords(line, x1, y1, x2, y2)

    def update_sequence(self):
        """接続順序を更新し、コールバックを呼び出す"""
        self.sequence = [self.input_node]
        visited = set()

        def dfs(node):
            for target in node.connections:
                if target not in visited:
                    visited.add(target)
                    self.sequence.append(target)
                    dfs(target)

        dfs(self.input_node)

        if self.input_node in self.sequence and self.output_node in self.sequence:
            # 入力と出力が正しく接続されている場合
            self.apply_processing_callback(self.sequence)
        else:
            # 入力または出力が切断されている場合
            self.apply_processing_callback(None)  # 特殊な指示として None を渡す



class MainApp(tk.Tk):
    """メインアプリケーションクラス"""
    def __init__(self):
        super().__init__()
        self.title("画像処理ツール")
        self.geometry("800x600")

        self.processor = None
        self.displayed_image = None

        self.canvas = tk.Canvas(self, width=600, height=400, bg="gray")
        self.canvas.pack(pady=20)

        self.upload_button = tk.Button(self, text="画像を選択", command=self.upload_image)
        self.upload_button.pack()

        self.node_editor_button = tk.Button(self, text="ノードエディタを開く", command=self.open_node_editor)
        self.node_editor_button.pack()

        self.node_editor = None

    def upload_image(self):
        """画像をアップロードして表示"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if file_path:
            image = Image.open(file_path)
            self.processor = ImageProcessor(image)
            self.show_image(self.processor.image)

    def show_image(self, img):
        """Canvasに画像を表示"""
        tk_image = ImageTk.PhotoImage(img)
        self.displayed_image = tk_image
        self.canvas.create_image(300, 200, image=tk_image)

    def open_node_editor(self):
        """ノードエディタを開く"""
        if not self.node_editor or not self.node_editor.winfo_exists():
            self.node_editor = NodeEditor(self, self.apply_processing)

    def apply_processing(self, sequence):
        """ノードエディタから処理を適用"""
        if sequence is None:
            # 真っ黒画像を表示
            black_image = Image.new("RGB", self.processor.image.size, (0, 0, 0))
            self.show_image(black_image)
        elif self.processor:
            for node in sequence:
                if node.label == "Grayscale":
                    self.processor.apply_grayscale()
                elif node.label == "Brightness":
                    self.processor.apply_brightness(1.5)
            self.show_image(self.processor.image)



class ImageProcessor:
    """画像処理を担当するクラス"""
    def __init__(self, image):
        self.image = image.copy()
        self.original_image = image.copy()

    def apply_grayscale(self):
        """グレースケールを適用する"""
        self.image = self.image.convert("L")

    def apply_brightness(self, factor):
        """明るさ調整を適用する"""
        enhancer = ImageEnhance.Brightness(self.image)
        self.image = enhancer.enhance(factor)

class CustomCanvas(tk.Canvas):
    """カスタムキャンバス（角丸四角描画を追加）"""
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        """角丸四角形を描画"""
        points = [
            x1 + radius, y1,
            x1 + radius, y1,
            x2 - radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
