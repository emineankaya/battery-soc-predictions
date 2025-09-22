"""
Keşifsel Veri Analizi (EDA) Sınıfı
Batarya verilerini analiz eder ve görselleştirmeleri oluşturur
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class BatteryEDA:
    def __init__(self):
        """
        EDA sınıfını başlat
        """
        # Görsel tema ayarları
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Plotly tema
        self.plotly_theme = 'plotly_white'
        
    def load_processed_data(self, file_path):
        """
        İşlenmiş veriyi yükle
        
        Args:
            file_path (str): CSV dosya yolu
            
        Returns:
            DataFrame: Yüklenen veri
        """
        try:
            df = pd.read_csv(file_path)
            print(f"✓ Veri yüklendi: {file_path}")
            print(f"  - Boyut: {df.shape}")
            print(f"  - Sütunlar: {len(df.columns)}")
            return df
        except Exception as e:
            print(f"❌ Veri yükleme hatası: {e}")
            return None
    
    def basic_statistics(self, df):
        """
        Temel istatistikleri göster
        
        Args:
            df (DataFrame): Veri
        """
        print("=== TEMEL İSTATİSTİKLER ===")
        print(f"Veri boyutu: {df.shape}")
        print(f"Toplam çevrim sayısı: {df['cycle'].max() if 'cycle' in df.columns else 'Bilinmiyor'}")
        
        # Sayısal sütunlar için özet istatistik
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        print(f"\nSayısal sütun sayısı: {len(numeric_cols)}")
        
        # Özet istatistik tablosu
        summary_stats = df[numeric_cols].describe()
        print("\nÖzet İstatistikler:")
        print(summary_stats.round(3))
        
        # Eksik değer analizi
        missing_values = df.isnull().sum()
        if missing_values.any():
            print("\nEksik Değerler:")
            for col, count in missing_values.items():
                if count > 0:
                    print(f"  {col}: {count} ({count/len(df)*100:.1f}%)")
        else:
            print("\n✓ Eksik değer bulunmuyor")
    
    def correlation_analysis(self, df, save_path=None):
        """
        Korelasyon analizi ve heatmap
        
        Args:
            df (DataFrame): Veri
            save_path (str): Kayıt yolu (opsiyonel)
        """
        print("\n=== KORELASYON ANALİZİ ===")
        
        # Sadece sayısal sütunlar
        numeric_df = df.select_dtypes(include=[np.number])
        
        # Korelasyon matrisi
        correlation_matrix = numeric_df.corr()
        
        # Yüksek korelasyonları bul (0.7'den yüksek)
        high_corr_pairs = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_val = correlation_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    high_corr_pairs.append({
                        'var1': correlation_matrix.columns[i],
                        'var2': correlation_matrix.columns[j],
                        'correlation': corr_val
                    })
        
        if high_corr_pairs:
            print("Yüksek Korelasyonlar (>0.7):")
            for pair in sorted(high_corr_pairs, key=lambda x: abs(x['correlation']), reverse=True):
                print(f"  {pair['var1']} - {pair['var2']}: {pair['correlation']:.3f}")
        
        # Heatmap oluştur
        plt.figure(figsize=(12, 10))
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        
        sns.heatmap(correlation_matrix, 
                   mask=mask,
                   annot=True, 
                   cmap='coolwarm', 
                   center=0,
                   square=True,
                   linewidths=0.5,
                   cbar_kws={"shrink": .5},
                   fmt='.2f')
        
        plt.title('Korelasyon Matrisi', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(f"{save_path}/correlation_heatmap.png", dpi=300, bbox_inches='tight')
            print(f"✓ Korelasyon heatmap kaydedildi: {save_path}/correlation_heatmap.png")
        
        plt.show()
        
        return correlation_matrix
    
    def capacity_degradation_analysis(self, df, save_path=None):
        """
        Kapasite azalma analizi
        
        Args:
            df (DataFrame): Veri
            save_path (str): Kayıt yolu (opsiyonel)
        """
        print("\n=== KAPASİTE AZALMA ANALİZİ ===")
        
        if 'capacity' not in df.columns or 'cycle' not in df.columns:
            print("❌ Kapasite veya çevrim verisi bulunamadı")
            return
        
        # Kapasite trendi
        initial_capacity = df['capacity'].iloc[0]
        final_capacity = df['capacity'].iloc[-1]
        total_degradation = ((initial_capacity - final_capacity) / initial_capacity) * 100
        
        print(f"Başlangıç kapasitesi: {initial_capacity:.3f} Ah")
        print(f"Son kapasite: {final_capacity:.3f} Ah")
        print(f"Toplam kapasite kaybı: {total_degradation:.2f}%")
        
        # Görselleştirme
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Kapasite-Çevrim grafiği
        axes[0, 0].plot(df['cycle'], df['capacity'], 'b-', linewidth=2, alpha=0.8)
        axes[0, 0].set_xlabel('Çevrim Sayısı')
        axes[0, 0].set_ylabel('Kapasite (Ah)')
        axes[0, 0].set_title('Kapasite vs Çevrim')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Kapasite tutma oranı (eğer varsa)
        if 'capacity_retention' in df.columns:
            axes[0, 1].plot(df['cycle'], df['capacity_retention']*100, 'r-', linewidth=2, alpha=0.8)
            axes[0, 1].set_xlabel('Çevrim Sayısı')
            axes[0, 1].set_ylabel('Kapasite Tutma Oranı (%)')
            axes[0, 1].set_title('Kapasite Tutma Oranı')
            axes[0, 1].grid(True, alpha=0.3)
        else:
            # Manuel hesapla
            retention = (df['capacity'] / initial_capacity) * 100
            axes[0, 1].plot(df['cycle'], retention, 'r-', linewidth=2, alpha=0.8)
            axes[0, 1].set_xlabel('Çevrim Sayısı')
            axes[0, 1].set_ylabel('Kapasite Tutma Oranı (%)')
            axes[0, 1].set_title('Kapasite Tutma Oranı')
            axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Kapasite değişim oranı
        if 'capacity_change' in df.columns:
            axes[1, 0].plot(df['cycle'][1:], df['capacity_change'][1:], 'g-', alpha=0.7)
            axes[1, 0].set_xlabel('Çevrim Sayısı')
            axes[1, 0].set_ylabel('Kapasite Değişimi (Ah)')
            axes[1, 0].set_title('Çevrim Bazında Kapasite Değişimi')
            axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Kapasite histogramı
        axes[1, 1].hist(df['capacity'], bins=30, alpha=0.7, color='purple', edgecolor='black')
        axes[1, 1].set_xlabel('Kapasite (Ah)')
        axes[1, 1].set_ylabel('Frekans')
        axes[1, 1].set_title('Kapasite Dağılımı')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(f"{save_path}/capacity_analysis.png", dpi=300, bbox_inches='tight')
            print(f"✓ Kapasite analiz grafiği kaydedildi: {save_path}/capacity_analysis.png")
        
        plt.show()
    
    def voltage_analysis(self, df, save_path=None):
        """
        Voltaj analizi
        
        Args:
            df (DataFrame): Veri
            save_path (str): Kayıt yolu (opsiyonel)
        """
        print("\n=== VOLTAJ ANALİZİ ===")
        
        voltage_cols = [col for col in df.columns if 'voltage' in col.lower()]
        
        if not voltage_cols:
            print("❌ Voltaj verisi bulunamadı")
            return
        
        print(f"Voltaj sütunları: {voltage_cols}")
        
        # Voltaj istatistikleri
        for col in voltage_cols:
            if col in df.columns:
                print(f"\n{col}:")
                print(f"  Min: {df[col].min():.3f} V")
                print(f"  Max: {df[col].max():.3f} V")
                print(f"  Ortalama: {df[col].mean():.3f} V")
                print(f"  Std: {df[col].std():.3f} V")
        
        # Görselleştirme
        n_voltage_cols = len(voltage_cols)
        if n_voltage_cols > 0:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            axes = axes.flatten()
            
            # Voltaj-çevrim grafikleri
            for i, col in enumerate(voltage_cols[:4]):  # En fazla 4 grafik
                if i < 4:
                    axes[i].plot(df['cycle'], df[col], linewidth=1.5, alpha=0.8)
                    axes[i].set_xlabel('Çevrim Sayısı')
                    axes[i].set_ylabel(f'{col} (V)')
                    axes[i].set_title(f'{col} vs Çevrim')
                    axes[i].grid(True, alpha=0.3)
            
            # Kullanılmayan subplot'ları gizle
            for i in range(len(voltage_cols), 4):
                axes[i].set_visible(False)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(f"{save_path}/voltage_analysis.png", dpi=300, bbox_inches='tight')
                print(f"✓ Voltaj analiz grafiği kaydedildi: {save_path}/voltage_analysis.png")
            
            plt.show()
    
    def temperature_analysis(self, df, save_path=None):
        """
        Sıcaklık analizi
        
        Args:
            df (DataFrame): Veri
            save_path (str): Kayıt yolu (opsiyonel)
        """
        print("\n=== SICAKLIK ANALİZİ ===")
        
        temp_cols = [col for col in df.columns if 'temperature' in col.lower()]
        
        if not temp_cols:
            print("❌ Sıcaklık verisi bulunamadı")
            return
        
        print(f"Sıcaklık sütunları: {temp_cols}")
        
        # Sıcaklık istatistikleri
        for col in temp_cols:
            if col in df.columns:
                print(f"\n{col}:")
                print(f"  Min: {df[col].min():.1f} °C")
                print(f"  Max: {df[col].max():.1f} °C")
                print(f"  Ortalama: {df[col].mean():.1f} °C")
        
        # Sıcaklık artışı analizi
        if 'temperature_rise' in df.columns:
            avg_rise = df['temperature_rise'].mean()
            max_rise = df['temperature_rise'].max()
            print(f"\nSıcaklık Artışı:")
            print(f"  Ortalama: {avg_rise:.1f} °C")
            print(f"  Maksimum: {max_rise:.1f} °C")
        
        # Görselleştirme
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Sıcaklık trend grafiği
        for col in temp_cols:
            if 'mean' in col.lower():
                axes[0].plot(df['cycle'], df[col], label=col, linewidth=2, alpha=0.8)
        
        axes[0].set_xlabel('Çevrim Sayısı')
        axes[0].set_ylabel('Sıcaklık (°C)')
        axes[0].set_title('Sıcaklık Trendi')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Sıcaklık dağılımı
        if temp_cols:
            main_temp_col = [col for col in temp_cols if 'mean' in col.lower()]
            if main_temp_col:
                axes[1].hist(df[main_temp_col[0]], bins=30, alpha=0.7, 
                           color='orange', edgecolor='black')
                axes[1].set_xlabel('Sıcaklık (°C)')
                axes[1].set_ylabel('Frekans')
                axes[1].set_title('Sıcaklık Dağılımı')
                axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(f"{save_path}/temperature_analysis.png", dpi=300, bbox_inches='tight')
            print(f"✓ Sıcaklık analiz grafiği kaydedildi: {save_path}/temperature_analysis.png")
        
        plt.show()
    
    def interactive_dashboard(self, df, save_path=None):
        """
        Etkileşimli dashboard oluştur
        
        Args:
            df (DataFrame): Veri
            save_path (str): Kayıt yolu (opsiyonel)
        """
        print("\n=== ETKİLEŞİMLİ DASHBOARD ===")
        
        # Alt grafikler oluştur
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Kapasite Trendi', 'Voltaj Analizi', 
                          'Sıcaklık Analizi', 'SOC Tahmini'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. Kapasite trendi
        if 'capacity' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['cycle'], y=df['capacity'],
                          mode='lines', name='Kapasite',
                          line=dict(color='blue', width=2)),
                row=1, col=1
            )
        
        # 2. Voltaj analizi
        voltage_cols = [col for col in df.columns if 'voltage' in col.lower() and 'mean' in col.lower()]
        if voltage_cols:
            fig.add_trace(
                go.Scatter(x=df['cycle'], y=df[voltage_cols[0]],
                          mode='lines', name='Voltaj Ortalama',
                          line=dict(color='red', width=2)),
                row=1, col=2
            )
        
        # 3. Sıcaklık analizi
        temp_cols = [col for col in df.columns if 'temperature' in col.lower() and 'mean' in col.lower()]
        if temp_cols:
            fig.add_trace(
                go.Scatter(x=df['cycle'], y=df[temp_cols[0]],
                          mode='lines', name='Sıcaklık',
                          line=dict(color='green', width=2)),
                row=2, col=1
            )
        
        # 4. SOC tahmini
        if 'estimated_soc' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['cycle'], y=df['estimated_soc'],
                          mode='lines', name='Tahmini SOC',
                          line=dict(color='purple', width=2)),
                row=2, col=2
            )
        
        # Layout güncelle
        fig.update_layout(
            height=600,
            showlegend=True,
            title_text="Batarya Performans Dashboard",
            title_x=0.5
        )
        
        # Eksenleri güncelle
        fig.update_xaxes(title_text="Çevrim", row=1, col=1)
        fig.update_xaxes(title_text="Çevrim", row=1, col=2)
        fig.update_xaxes(title_text="Çevrim", row=2, col=1)
        fig.update_xaxes(title_text="Çevrim", row=2, col=2)
        
        fig.update_yaxes(title_text="Kapasite (Ah)", row=1, col=1)
        fig.update_yaxes(title_text="Voltaj (V)", row=1, col=2)
        fig.update_yaxes(title_text="Sıcaklık (°C)", row=2, col=1)
        fig.update_yaxes(title_text="SOC (%)", row=2, col=2)
        
        # Göster
        fig.show()
        
        if save_path:
            fig.write_html(f"{save_path}/interactive_dashboard.html")
            print(f"✓ Etkileşimli dashboard kaydedildi: {save_path}/interactive_dashboard.html")
    
    def generate_eda_report(self, df, output_dir="../reports"):
        """
        Kapsamlı EDA raporu oluştur
        
        Args:
            df (DataFrame): Veri
            output_dir (str): Çıktı klasörü
        """
        import os
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print("=== EDA RAPORU OLUŞTURULUYOR ===")
        
        # Tüm analizleri çalıştır
        self.basic_statistics(df)
        correlation_matrix = self.correlation_analysis(df, output_dir)
        self.capacity_degradation_analysis(df, output_dir)
        self.voltage_analysis(df, output_dir)
        self.temperature_analysis(df, output_dir)
        self.interactive_dashboard(df, output_dir)
        
        # Özet rapor dosyası oluştur
        report_path = f"{output_dir}/eda_summary_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("BATARYA VERİSİ KEŞİFSEL ANALİZ RAPORU\n")
            f.write("="*50 + "\n\n")
            
            f.write(f"Veri Boyutu: {df.shape}\n")
            f.write(f"Toplam Çevrim: {df['cycle'].max() if 'cycle' in df.columns else 'Bilinmiyor'}\n")
            f.write(f"Analiz Tarihi: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            # Özet istatistikler
            f.write("ÖZET İSTATİSTİKLER:\n")
            f.write("-"*30 + "\n")
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols[:10]:  # İlk 10 sütun
                f.write(f"{col}:\n")
                f.write(f"  Ortalama: {df[col].mean():.3f}\n")
                f.write(f"  Std: {df[col].std():.3f}\n")
                f.write(f"  Min: {df[col].min():.3f}\n")
                f.write(f"  Max: {df[col].max():.3f}\n\n")
            
            # Yüksek korelasyonlar
            f.write("YÜKSEK KORELASYONLAR (>0.7):\n")
            f.write("-"*30 + "\n")
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_val = correlation_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        f.write(f"{correlation_matrix.columns[i]} - {correlation_matrix.columns[j]}: {corr_val:.3f}\n")
        
        print(f"✓ EDA raporu tamamlandı: {report_path}")
        print(f"✓ Grafikler kaydedildi: {output_dir}")

from pathlib import Path

if __name__ == "__main__":
    # EDA sınıfı oluştur
    eda = BatteryEDA()
    
    # İşlenmiş veriyi yükle (mutlak yol ile)
    script_dir = Path(__file__).resolve().parent
    data_path = (script_dir / "../data/processed/B0005_processed.csv").resolve()
    
    df = eda.load_processed_data(data_path)
    
    if df is not None:
        # Kapsamlı EDA raporu oluştur
        eda.generate_eda_report(df)
    else:
        print("❌ Önce veri işleme scriptini çalıştırın!")
