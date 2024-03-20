import cv2
import numpy as np
from mask_GB import get_mask, image_cnv
def process_frames(video_path):
    # 動画を読み込む
    video = cv2.VideoCapture(video_path)
    
    # 動画からフレーム数を取得する
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # 動画のFPS（フレームレート）を取得する
    fps = int(video.get(cv2.CAP_PROP_FPS))
    
    # フレームごとの処理
    while True:
        ret, frame = video.read()
        if not ret:
            break  # フレームの読み込みに失敗した場合、ループを抜ける
        
        # ここでフレームごとの処理を行う
        # 例えば、画面にフレームを表示する場合は以下のようにする
        frame[get_mask(frame)] = 0
        cv2.imshow('Frame',frame)
        
        # 'q' キーが押されたら終了する
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # リソースを解放する
    video.release()
    cv2.destroyAllWindows()

# テスト用の動画のパス
video_path = 'image\ms_minutes_walking_GB - Made with Clipchamp.mp4'

# 動画を読み込んでフレームごとに処理する
process_frames(video_path)
