"""
Batarya Veri Ön İşleme Sınıfı (SOC Tahmini ve EDA uyumlu)
Bu dosya NASA batarya verilerini inceler ve modelleme / EDA için hazırlar
"""

import pandas as pd
import numpy as np
import scipy.io
from pathlib import Path

def safe_extract(array):
    """Nested numpy array'leri açar ve tüm elemanları döndürür"""
    while isinstance(array, np.ndarray) and array.size == 1:
        array = array[0]
    return array

class BatteryDataProcessor:
    def __init__(self):
        self.processed_data = []

    def load_nasa_battery_file(self, file_path):
        print(f"Dosya yükleniyor: {file_path}")
        try:
            mat_data = scipy.io.loadmat(file_path)
            file_name = Path(file_path).stem

            if file_name in mat_data:
                battery_data = mat_data[file_name]
                print(f"✓ {file_name} verisi bulundu")
                self._extract_cycle_data(battery_data)
            else:
                print(f"❌ {file_name} anahtarı bulunamadı")
                print("Mevcut anahtarlar:", [k for k in mat_data.keys() if not k.startswith('__')])
                return None

        except Exception as e:
            print(f"❌ Dosya yükleme hatası: {e}")
            return None

    def _extract_cycle_data(self, battery_struct):
        try:
            if hasattr(battery_struct, 'dtype') and battery_struct.dtype.names:
                if 'cycle' in battery_struct.dtype.names:
                    cycles = safe_extract(battery_struct['cycle'])
                    # Flatten tüm çevrimleri al
                    if isinstance(cycles, np.ndarray):
                        cycles = cycles.flatten()
                    print(f"Toplam çevrim sayısı: {len(cycles)}")

                    for i, cycle in enumerate(cycles):
                        cycle_data = self._process_single_cycle(cycle, i+1)
                        if cycle_data:
                            self.processed_data.append(cycle_data)

        except Exception as e:
            print(f"❌ Veri çıkarma hatası: {e}")

    def _process_single_cycle(self, cycle, cycle_number):
        try:
            cycle_data = {'cycle': cycle_number}

            if hasattr(cycle, 'dtype') and cycle.dtype.names:
                # type alanı
                if 'type' in cycle.dtype.names:
                    types = safe_extract(cycle['type'])
                    types_list = [str(t) for t in types.flatten()]
                    cycle_data['type_charge'] = 1 if 'charge' in types_list else 0
                    cycle_data['type_discharge'] = 1 if 'discharge' in types_list else 0

                # data alanındaki ölçümler
                if 'data' in cycle.dtype.names:
                    data = safe_extract(cycle['data'])
                    if hasattr(data, 'dtype') and data.dtype.names:
                        # Voltaj
                        if 'Voltage_measured' in data.dtype.names:
                            v = safe_extract(data['Voltage_measured']).flatten()
                            cycle_data['voltage_mean'] = np.mean(v)
                            cycle_data['voltage_min'] = np.min(v)
                            cycle_data['voltage_max'] = np.max(v)
                        # Akım
                        if 'Current_measured' in data.dtype.names:
                            c = safe_extract(data['Current_measured']).flatten()
                            cycle_data['current_mean'] = np.mean(c)
                        # Sıcaklık
                        if 'Temperature_measured' in data.dtype.names:
                            t = safe_extract(data['Temperature_measured']).flatten()
                            cycle_data['temperature_mean'] = np.mean(t)
                        # Zaman
                        if 'Time' in data.dtype.names:
                            tm = safe_extract(data['Time']).flatten()
                            cycle_data['time_max'] = np.max(tm)

            # SOC tahmini placeholder (0-100 arası)
            cycle_data['estimated_soc'] = 100 * (1 - (cycle_number-1)/len(cycle_data))

            return cycle_data

        except Exception as e:
            print(f"Çevrim {cycle_number} işlenirken hata: {e}")
            return None

    def save_to_csv(self, output_file):
        if self.processed_data:
            df = pd.DataFrame(self.processed_data)
            df.to_csv(output_file, index=False)
            print(f"✓ İşlenmiş veri kaydedildi: {output_file}")
            return df
        else:
            print("❌ Kaydedilecek veri yok")
            return None


if __name__ == "__main__":
    processor = BatteryDataProcessor()
    script_dir = Path(__file__).resolve().parent
    data_file = (script_dir / "../data/raw/B0005.mat").resolve()
    output_csv = (script_dir / "../data/processed/B0005_processed.csv").resolve()

    print(f"=== BATARYA VERİSİ İŞLEME BAŞLIYOR ===\nDosya yolu: {data_file}")

    if not data_file.exists():
        print(f"❌ Dosya bulunamadı: {data_file}")
    else:
        processor.load_nasa_battery_file(data_file)
        processor.save_to_csv(output_csv)
