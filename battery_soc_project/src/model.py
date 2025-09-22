import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
import joblib
import json

# Proje dizinini al
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def calculate_soc_from_voltage(voltage):
    """Voltaj değerlerinden SOC hesapla"""
    # Lityum batarya için voltaj-SOC ilişkisi
    soc = np.select(
        [
            voltage >= 4.2, 
            voltage >= 4.15,
            voltage >= 4.1,
            voltage >= 4.05,
            voltage >= 4.0,
            voltage >= 3.95,
            voltage >= 3.9, 
            voltage >= 3.85,
            voltage >= 3.8,
            voltage >= 3.75,
            voltage >= 3.7,
            voltage >= 3.65,
            voltage >= 3.6,
            voltage >= 3.55,
            voltage >= 3.5,
            voltage < 3.5
        ],
        [
            100,  # 4.2V+ → 100%
            95,   # 4.15V → 95%
            90,   # 4.1V → 90%
            85,   # 4.05V → 85%
            80,   # 4.0V → 80%
            75,   # 3.95V → 75%
            70,   # 3.9V → 70%
            65,   # 3.85V → 65%
            60,   # 3.8V → 60%
            50,   # 3.75V → 50%
            40,   # 3.7V → 40%
            30,   # 3.65V → 30%
            20,   # 3.6V → 20%
            10,   # 3.55V → 10%
            5,    # 3.5V → 5%
            0     # 3.5V- → 0%
        ]
    )
    
    return soc

def load_and_fix_data():
    """Mevcut işlenmiş veriyi yükle ve SOC'yi düzelt"""
    processed_file_path = os.path.join(BASE_DIR, "../data/processed/B0005_processed.csv")
    
    if not os.path.exists(processed_file_path):
        raise FileNotFoundError(f"İşlenmiş veri dosyası bulunamadı: {processed_file_path}")
    
    # İşlenmiş veriyi yükle
    df = pd.read_csv(processed_file_path)
    print(f"✓ İşlenmiş veri yüklendi: {len(df)} satır")
    
    # Mevcut SOC değerlerini göster
    print(f"\n⏳ Orijinal SOC istatistikleri:")
    print(f"Min: {df['estimated_soc'].min()}")
    print(f"Max: {df['estimated_soc'].max()}")
    print(f"Ortalama: {df['estimated_soc'].mean()}")
    
    # Voltaj değerlerini kontrol et
    print(f"\n📊 Voltaj istatistikleri:")
    print(f"Min: {df['voltage_mean'].min()}")
    print(f"Max: {df['voltage_mean'].max()}")
    print(f"Ortalama: {df['voltage_mean'].mean()}")
    
    # SOC'yi voltajdan YENİDEN HESAPLA
    print("\n🔧 SOC voltajdan yeniden hesaplanıyor...")
    df['estimated_soc'] = calculate_soc_from_voltage(df['voltage_mean'])
    
    # Yeni SOC değerlerini göster
    print(f"\n✅ Yeni SOC istatistikleri:")
    print(f"Min: {df['estimated_soc'].min()}")
    print(f"Max: {df['estimated_soc'].max()}")
    print(f"Ortalama: {df['estimated_soc'].mean()}")
    
    # İlk 5 satırı göster
    print(f"\n👀 İlk 5 satır (voltage_mean -> estimated_soc):")
    for i in range(min(5, len(df))):
        print(f"Voltaj: {df['voltage_mean'].iloc[i]:.3f}V -> SOC: {df['estimated_soc'].iloc[i]}%")
    
    return df

def train_model():
    print("=== 🔋 Model Eğitimi Başlıyor ===")
    
    # Veriyi yükle ve SOC'yi düzelt
    df = load_and_fix_data()
    
    # Özellikler ve hedef değişken
    X = df[["voltage_mean", "current_mean", "temperature_mean", "time_max"]]
    y = df["estimated_soc"]
    
    # Veriyi böl
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=True
    )

    print(f"\n📊 Veri boyutları:")
    print(f"Eğitim: {len(X_train)} örnek")
    print(f"Test: {len(X_test)} örnek")

    # Pipeline oluştur
    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="mean")),
        ("model", RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        ))
    ])

    # Modeli eğit
    print("\n🎯 Model eğitiliyor...")
    pipeline.fit(X_train, y_train)

    # Tahminler
    y_pred = pipeline.predict(X_test)

    # Metrikler
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    mae = np.mean(np.abs(y_test - y_pred))

    print(f"\n=== 📈 MODEL PERFORMANSI ===")
    print(f"Test MSE: {mse:.4f}")
    print(f"Test RMSE: {rmse:.4f}")
    print(f"Test MAE: {mae:.4f}")
    print(f"Test R² : {r2:.4f}")

    # Feature importance
    feature_importance = pipeline.named_steps['model'].feature_importances_
    features = X.columns
    print(f"\n=== 🎯 FEATURE IMPORTANCE ===")
    for feature, importance in zip(features, feature_importance):
        print(f"{feature}: {importance:.4f}")

    # Model kaydet
    model_dir = os.path.join(BASE_DIR, "../models")
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, "battery_soc_model.pkl")
    joblib.dump(pipeline, model_path)
    print(f"\n💾 Model kaydedildi: {model_path}")

    # Model info
    model_info = {
        "best_model_name": "RandomForest",
        "feature_names": list(X.columns),
        "feature_importances": dict(zip(features, [float(imp) for imp in feature_importance])),
        "metrics": {
            "r2": round(r2, 4),
            "rmse": round(rmse, 4),
            "mae": round(mae, 4)
        }
    }

    info_path = os.path.join(model_dir, "model_info.json")
    with open(info_path, "w") as f:
        json.dump(model_info, f, indent=4)
    print(f"📄 model_info.json oluşturuldu")

    print(f"\n✅ Eğitim tamamlandı!")
    print(f"📊 Final RMSE: {rmse:.2f}%")
    print(f"📊 Final R²: {r2:.4f}")

# model.py dosyasını AÇ ve EN SON kısmı şöyle değiştir:

if __name__ == "__main__":
    # Önce eski model dosyalarını sil
    import shutil
    model_dir = os.path.join(BASE_DIR, "../models")
    
    # Eski dosyaları sil
    for filename in ['battery_soc_model.pkl', 'model_info.json']:
        file_path = os.path.join(model_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️  Eski dosya silindi: {filename}")
    
    # Yeni modeli eğit
    train_model()