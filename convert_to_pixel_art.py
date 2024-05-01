from PIL import Image

# 画像を読み込んで、ドット絵に変換する関数
def convert_to_pixel_art(input_image_path, output_image_path, pixel_size):
    # 画像を開く
    image = Image.open(input_image_path)
    
    # 画像を指定したサイズにリサイズ
    width, height = image.size
    new_width = pixel_size * (width // pixel_size)
    new_height = pixel_size * (height // pixel_size)
    image = image.resize((new_width, new_height))
    
    # ドット絵に変換
    pixel_art = image.quantize(colors=256, method=1)
    
    # ドット絵を保存
    pixel_art.save(output_image_path)

# テスト用の画像変換
if __name__ == "__main__":
    input_image_path = r"C:\Users\pshun\Pictures\OM Workspace\2023_10_29\PA290031_01.jpg"  # あなたの画像のパスに置き換えてください
    output_image_path = "output_pixel_art.png"  # 出力ファイルのパス
    pixel_size = 1 # ピクセルの大きさ

    convert_to_pixel_art(input_image_path, output_image_path, pixel_size)
