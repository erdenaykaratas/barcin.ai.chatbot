# new_data_processor.py - Sıfırdan yeni, temiz kod
"""
Tamamen yeni Enhanced Data Processor - JSON hatası olmadan
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Any
import logging

class NewDataProcessor:
    def __init__(self):
        """Yeni veri işleyici"""
        self.analysis_results = {}
        
    def analyze_file(self, df: pd.DataFrame, filename: str) -> Dict:
        """Dosyayı analiz et - JSON safe"""
        
        # Temel bilgiler - sadece Python native tiplerle
        basic_info = {
            'filename': str(filename),
            'rows': int(len(df)),
            'columns': int(len(df.columns)),
            'column_names': [str(col) for col in df.columns]
        }
        
        # Her sütunu analiz et
        column_info = {}
        for col in df.columns:
            col_str = str(col)
            col_data = df[col]
            
            # Sütun analizi - sadece temel Python tipleri
            col_info = {
                'type': str(col_data.dtype),
                'unique_count': int(col_data.nunique()),
                'missing_count': int(col_data.isnull().sum()),
                'sample_values': [str(x) for x in col_data.dropna().head(3).tolist()]
            }
            
            # Sayısal sütunlar için istatistikler
            if pd.api.types.is_numeric_dtype(col_data):
                try:
                    col_info['stats'] = {
                        'mean': float(col_data.mean()),
                        'min': float(col_data.min()),
                        'max': float(col_data.max())
                    }
                except:
                    col_info['stats'] = {'mean': 0.0, 'min': 0.0, 'max': 0.0}
            
            column_info[col_str] = col_info
        
        # İş bağlamı tespit et
        business_context = self._detect_context(df.columns)
        
        # Sonuç - tamamen JSON safe
        result = {
            'basic_info': basic_info,
            'columns': column_info,
            'business_context': business_context
        }
        
        return result
    
    def _detect_context(self, columns) -> str:
        """İş bağlamını tespit et"""
        
        columns_text = ' '.join([str(col).lower() for col in columns])
        
        if any(word in columns_text for word in ['maaş', 'çalışan', 'departman', 'employee']):
            return 'hr_data'
        elif any(word in columns_text for word in ['ciro', 'satış', 'mağaza', 'sales']):
            return 'sales_data'
        else:
            return 'general_data'
    
    def generate_insights(self, analysis: Dict) -> List[str]:
        """Akıllı çıkarımlar üret"""
        
        insights = []
        basic = analysis['basic_info']
        columns = analysis['columns']
        context = analysis['business_context']
        
        # Veri büyüklüğü
        if basic['rows'] > 100:
            insights.append(f"✅ Büyük veri seti: {basic['rows']} satır")
        else:
            insights.append(f"📊 Orta boy veri seti: {basic['rows']} satır")
        
        # Veri kalitesi
        total_missing = sum([col['missing_count'] for col in columns.values()])
        if total_missing == 0:
            insights.append("🌟 Mükemmel veri kalitesi - eksik veri yok")
        elif total_missing < basic['rows'] * 0.1:
            insights.append("✅ İyi veri kalitesi - az eksik veri")
        else:
            insights.append("⚠️ Veri kalitesi iyileştirme gerekli")
        
        # İş bağlamı önerileri
        if context == 'sales_data':
            insights.append("💰 Satış verisi tespit edildi - ciro analizi yapılabilir")
        elif context == 'hr_data':
            insights.append("👥 İK verisi tespit edildi - maaş analizi yapılabilir")
        
        return insights
    
    def suggest_queries(self, analysis: Dict) -> List[str]:
        """Sorgu önerileri"""
        
        suggestions = []
        columns = analysis['columns']
        context = analysis['business_context']
        
        # Sayısal sütunlar için öneriler
        numeric_columns = [name for name, info in columns.items() 
                          if 'stats' in info]
        
        for col in numeric_columns[:3]:  # İlk 3 sayısal sütun
            suggestions.append(f"{col} sütunundaki ortalama değer nedir?")
            suggestions.append(f"{col} sütunundaki en yüksek değer kaçtır?")
        
        # Bağlam bazlı öneriler
        if context == 'sales_data':
            suggestions.extend([
                "Hangi mağaza en yüksek ciro yapmış?",
                "Toplam ciro ne kadar?",
                "Ortalama büyüme oranı nedir?"
            ])
        elif context == 'hr_data':
            suggestions.extend([
                "Departman bazında ortalama maaş nedir?",
                "En yüksek maaşlı çalışan kimdir?",
                "Toplam çalışan sayısı kaç?"
            ])
        
        return suggestions[:8]  # Max 8 öneri


def test_new_processor():
    """Yeni processor'ı test et"""
    
    print("🆕 Yeni Data Processor Test Başlıyor...")
    
    processor = NewDataProcessor()
    
    # Test verisi oluştur
    test_data = pd.DataFrame({
        'Ad Soyad': ['Ahmet Yılmaz', 'Fatma Kaya', 'Mehmet Demir'],
        'Departman': ['Bilgi İşlem', 'Muhasebe', 'Satış'],
        'Maaş': [15000, 12000, 18000],
        'Başlama Tarihi': ['2020-01-01', '2019-06-15', '2021-03-10']
    })
    
    print("📊 Test verisi hazırlandı")
    
    try:
        # Analiz yap
        print("1️⃣ Analiz başlatılıyor...")
        analysis = processor.analyze_file(test_data, 'test.xlsx')
        print("✅ Analiz tamamlandı")
        
        # Sonuçları yazdır
        basic = analysis['basic_info']
        print(f"\n📋 Temel Bilgiler:")
        print(f"   Dosya: {basic['filename']}")
        print(f"   Satır sayısı: {basic['rows']}")
        print(f"   Sütun sayısı: {basic['columns']}")
        print(f"   İş bağlamı: {analysis['business_context']}")
        
        print(f"\n📊 Sütun Detayları:")
        for col_name, col_info in analysis['columns'].items():
            print(f"   {col_name}:")
            print(f"      - Tip: {col_info['type']}")
            print(f"      - Unique: {col_info['unique_count']}")
            print(f"      - Eksik: {col_info['missing_count']}")
            print(f"      - Örnek: {col_info['sample_values']}")
            
            if 'stats' in col_info:
                stats = col_info['stats']
                print(f"      - Ortalama: {stats['mean']:.2f}")
                print(f"      - Min-Max: {stats['min']:.2f} - {stats['max']:.2f}")
        
        # Insights
        print("\n💡 Akıllı Çıkarımlar:")
        insights = processor.generate_insights(analysis)
        for i, insight in enumerate(insights, 1):
            print(f"   {i}. {insight}")
        
        # Öneriler
        print("\n❓ Önerilen Sorular:")
        suggestions = processor.suggest_queries(analysis)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
        
        print("\n🎉 Test başarıyla tamamlandı!")
        
        # Gerçek dosya testi
        print(f"\n{'='*50}")
        print("📁 Gerçek Dosya Testi:")
        
        import os
        real_files = ['sales.xlsx', 'company_data/sales.xlsx', 'calisanlar.xlsx', 'company_data/calisanlar.xlsx']
        
        for filename in real_files:
            if os.path.exists(filename):
                print(f"\n📊 {filename} analiz ediliyor...")
                try:
                    real_df = pd.read_excel(filename)
                    real_analysis = processor.analyze_file(real_df, filename)
                    
                    basic = real_analysis['basic_info']
                    print(f"✅ Başarıyla analiz edildi:")
                    print(f"   - {basic['rows']} satır, {basic['columns']} sütun")
                    print(f"   - İş bağlamı: {real_analysis['business_context']}")
                    
                    # Insights
                    real_insights = processor.generate_insights(real_analysis)
                    print(f"   - {len(real_insights)} insight bulundu")
                    
                    # İlk 3 insight'ı göster
                    for insight in real_insights[:3]:
                        print(f"     • {insight}")
                    
                    # İlk 3 önerilen soruyu göster
                    real_suggestions = processor.suggest_queries(real_analysis)
                    print(f"   - Önerilen sorular:")
                    for suggestion in real_suggestions[:3]:
                        print(f"     • {suggestion}")
                    
                    break
                    
                except Exception as e:
                    print(f"❌ {filename} okunamadı: {e}")
        
        print(f"\n🚀 Tüm testler tamamlandı!")
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_new_processor()