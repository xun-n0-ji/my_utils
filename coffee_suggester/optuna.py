import optuna
import sqlite3

# データベース接続とテーブルの作成
conn = sqlite3.connect('coffee_optimization.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS coffee_parameters (
                 id INTEGER PRIMARY KEY,
                 beans_weight REAL,
                 water_amount REAL,
                 brewing_time REAL,
                 grind_size TEXT,
                 water_temp REAL,
                 evaluation_score REAL
             )''')
conn.commit()

# 評価関数を定義します
def evaluate_coffee(trial):
    # コーヒーの淹れ方のパラメータ
    beans_weight = trial.suggest_uniform('beans_weight', 10, 30)  # 豆のグラム量
    water_amount = trial.suggest_uniform('water_amount', 200, 500)  # お湯の量（ml）
    brewing_time = trial.suggest_uniform('brewing_time', 2, 10)  # 抽出時間（分）
    grind_size = trial.suggest_categorical('grind_size', ['coarse', 'medium', 'fine'])  # 挽き具合
    water_temp = trial.suggest_uniform('water_temp', 85, 96)  # お湯の温度（℃）
    
    # 評価値を入力
    evaluation_score = float(input(f"Rate the coffee (0-10) for the following parameters:\n"
                                   f"Beans weight: {beans_weight}g, Water amount: {water_amount}ml, "
                                   f"Brewing time: {brewing_time}min, Grind size: {grind_size}, Water temp: {water_temp}°C\n"))
    
    # データベースにパラメータと評価値を保存
    c.execute('''INSERT INTO coffee_parameters (beans_weight, water_amount, brewing_time, grind_size, water_temp, evaluation_score)
                 VALUES (?, ?, ?, ?, ?, ?)''', (beans_weight, water_amount, brewing_time, grind_size, water_temp, evaluation_score))
    conn.commit()
    
    return evaluation_score

# Optunaによる最適化
study = optuna.create_study(direction='maximize')
study.optimize(evaluate_coffee, n_trials=50)

print("Best parameters:")
print(study.best_params)
print("Best evaluation score:")
print(study.best_value)

# データベース接続を閉じる
conn.close()
