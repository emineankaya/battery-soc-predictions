🔋 Battery SOC Prediction System
https://img.shields.io/badge/Python-3.9+-blue.svg
https://img.shields.io/badge/Flask-2.3.3-green.svg
https://img.shields.io/badge/Docker-Ready-blue.svg
https://img.shields.io/badge/Machine-Learning-orange.svg

📖 Proje Özeti
Elektrikli araç bataryalarının Şarj Durumu (State of Charge - SOC) tahminini yapan makine öğrenmesi tabanlı bir sistem. NASA'nın lityum iyon batarya veri setleri kullanılarak geliştirilmiştir.

🎯 Özellikler
🤖 ML Modeli: RandomForest ile SOC tahmini

🌐 REST API: Flask tabanlı RESTful API

💻 Frontend: Node.js web arayüzü

🐳 Dockerized: Tam containerize çözüm

📊 Gerçek Zamanlı: Anlık tahmin ve toplu işlem

⚡ Yüksek Doğruluk: R²: 1.0, RMSE: 0.0539

🏗️ Sistem Mimarisi
text
battery_soc_project/
├── 📁 src/
│   └── api.py              # Flask REST API
├── 📁 frontend/
│   ├── app.js              # Node.js sunucu
│   └── index.html          # Web arayüzü
├── 📁 models/
│   ├── battery_soc_model.pkl      # Eğitilmiş model
│   └── model_info.json            # Model metadata
├── 📁 data/processed/
│   └── B0005_processed.csv        # NASA batarya verisi
├── 🐳 Dockerfile                 # API container
├── 🐳 Dockerfile.frontend        # Frontend container
├── 🐳 docker-compose.yml         # Orchestration
└── 📄 requirements.txt           Python bağımlılıkları
🚀 Kurulum ve Çalıştırma
1. Docker ile (Önerilen)
bash
# Tüm servisleri başlat
docker-compose up -d

# Tarayıcıda aç: http://localhost:3001
2. Manuel Çalıştırma
bash
# API
cd src
python api.py

# Frontend (yeni terminal)
cd frontend
node app.js
📊 API Endpoints
Endpoint	Method	Açıklama
/health	GET	Sistem durumu
/model-info	GET	Model bilgileri
/predict	POST	Tekli tahmin
/batch-predict	POST	Toplu tahmin
Örnek Kullanım
bash
# Health check
curl http://localhost:5000/health

# Tahmin yapma
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [3.8, 1.5, 25, 1800]}'
🎯 Model Performansı
Eğitim Metrikleri
R² Score: 1.0000

RMSE: 0.0539

MAE: 0.0048

Feature Importance
current_mean: 43.10%

voltage_mean: 36.04%

time_max: 13.90%

temperature_mean: 6.95%

🧪 Veri Seti
NASA Lithium-Ion Battery Aging Dataset

Batarya: B0005

Özellikler: voltage_mean, current_mean, temperature_mean, time_max

Hedef: estimated_soc (0-100%)

🔧 Geliştirme
Model Eğitimi
bash
python src/model.py
Yeni Özellikler Ekleme
Veri ön işleme iyileştirmeleri

Yeni ML algoritmaları deneme

Cross-validation ekleme

Hyperparameter tuning

📈 Proje Geliştirme Aşamaları
1. Veri Hazırlama ✅
NASA veri setinin temizlenmesi

Feature engineering

SOC değerlerinin normalize edilmesi

2. Model Eğitimi ✅
RandomForest regresyon modeli

Cross-validation

Model persistency

3. API Geliştirme ✅
RESTful endpoint'ler

Hata yönetimi

Input validation

4. Frontend ✅
Kullanıcı arayüzü

Gerçek zamanlı tahmin

Toplu işlem desteği

5. Deployment ✅
Docker containerization

Multi-container orchestration

Production ready

🐛 Sorun Giderme
"Failed to fetch" Hatası
bash
# API URL'ini kontrol et
docker-compose logs soc-frontend
Port Çakışması
bash
# Mevcut process'leri temizle
npx kill-port 3001
npx kill-port 5000
Model Yükleme Hatası
bash
# Model dosyalarını kontrol et
ls -la models/
📝 Lisans
Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için LICENSE dosyasına bakın.

👥 Katkıda Bulunma
Fork edin

Feature branch'i oluşturun (git checkout -b feature/AmazingFeature)

Commit edin (git commit -m 'Add AmazingFeature')

Push edin (git push origin feature/AmazingFeature)

Pull Request oluşturun
