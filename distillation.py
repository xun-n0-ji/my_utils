import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR

# 大きな教師モデル
teacher_model = LargeModel()
teacher_model.load_state_dict(torch.load('teacher_model.pth'))
teacher_model.eval()

# 軽量な生徒モデル
student_model = LightModel()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(student_model.parameters(), lr=0.001)
scheduler = StepLR(optimizer, step_size=30, gamma=0.1)

# トレーニングデータ
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

# 知識蒸留のパラメータ
temperature = 5.0
alpha = 0.7

for epoch in range(100):
    student_model.train()
    for images, labels in train_loader:
        optimizer.zero_grad()

        # 教師モデルの出力（ソフトラベル）
        with torch.no_grad():
            soft_labels = teacher_model(images)

        # 生徒モデルの出力
        student_output = student_model(images)

        # ソフトターゲットとハードターゲットの損失を計算
        loss_soft = nn.KLDivLoss()(F.log_softmax(student_output/temperature, dim=1),
                                   F.softmax(soft_labels/temperature, dim=1)) * (temperature**2)
        loss_hard = criterion(student_output, labels)
        loss = alpha * loss_soft + (1 - alpha) * loss_hard

        loss.backward()
        optimizer.step()

    scheduler.step()

    print(f'Epoch {epoch+1}, Loss: {loss.item()}')
