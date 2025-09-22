🔋 Battery SOC Prediction System
https://img.shields.io/badge/Python-3.9+-blue.svg
https://img.shields.io/badge/Flask-2.3.3-green.svg
https://img.shields.io/badge/Docker-Ready-blue.svg
https://img.shields.io/badge/Machine-Learning-orange.svg

📖 Proje Özeti
Elektrikli araç bataryalarının Şarj Durumu (State of Charge - SOC) tahminini yapan makine öğrenmesi tabanlı bir sistem. NASA'nın lityum iyon batarya veri setleri kullanılarak geliştirilmiştir.
🔋 Elektrikli Araç SOC Tahmin Sistemi
Bu proje, NASA batarya veri setlerini kullanarak elektrikli araç bataryalarının State of Charge (SOC) tahminini yapan kapsamlı bir makine öğrenmesi sistemidir.
🎯 Proje Amacı

NASA'nın B0005, B0006, B0018 batarya veri setlerini analiz etme
Batarya SOC değerini yüksek doğrulukla tahmin eden modeller geliştirme
REST API ile tahmin servisini sunma
Kullanıcı dostu web arayüzü ile demo sağlama
Docker ile kolay dağıtım
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

1. Gereksinimler

Python 3.9+
Node.js 18+
Docker & Docker Compose
4GB+ RAM

2. Veri Setini İndirin
NASA Prognostics Center'dan B0005, B0006, B0018 dosyalarını indirin:

https://ti.arc.nasa.gov/tech/dash/groups/pcoe/prognostic-data-repository/

Dosyaları data/raw/ klasörüne koyun.
3. Python Ortamı Kurulumu
bash# Sanal ortam oluştur
python -m venv venv

# Aktif et
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Gereksinimler yükle
pip install -r requirements.txt
4. Veri İşleme ve Model Eğitimi
bash# Veri ön işleme
cd src
python data_preprocessing.py

# Keşifsel veri analizi
python eda.py

# Model eğitimi
python model.py
5. API ve Frontend Başlatma
bash# API başlat (terminal 1)
python api.py

# Frontend başlat (terminal 2)
cd ../frontend
npm install
npm start
6. Docker ile Çalıştırma
bash# Tüm servisleri başlat
docker-compose up --build

# Sadece belirli servisleri başlat
docker-compose up soc-api soc-frontend
🌐 Servis URL'leri

Frontend Demo: http://localhost:3000
REST API: http://localhost:5000
API Dokümantasyon: http://localhost:5000
MQTT Broker: localhost:1883

📊 API Kullanımı
SOC Tahmini
bashcurl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [2.100, 3.800, 25.5, -1.500, 4.100, 2.500]
  }'
Toplu Tahmin
bashcurl -X POST http://localhost:5000/batch-predict \
  -H "Content-Type: application/json" \
  -d '{
    "batch_features": [
      [2.100, 3.800, 25.5, -1.500, 4.100, 2.500],
      [2.050, 3.750, 24.8, -1.450, 4.050, 2.450]
    ]
  }'
Sağlık Kontrolü
bashcurl http://localhost:5000/health


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
