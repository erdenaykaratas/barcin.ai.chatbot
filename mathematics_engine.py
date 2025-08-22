# mathematics_engine.py
"""
Gelişmiş matematik işlemleri, istatistik analizi ve veri hesaplamaları için motor.
Basit hesaplamalardan karmaşık istatistiksel analizlere kadar her şeyi destekler.

GÜNCELLEMELER:
- JSON Serialization Fix: Tüm numpy/pandas tipleri Python native tiplerine çevrildi
- Sorgu Tanıma Geliştirmeleri: Özel pattern'lar eklendi
- Veri Temizleme: Boş satırlar, geçersiz değerler filtrelendi
- Çalışan Sayısı: Benzersiz çalışan sayma algoritması
- Departman Analizi: Karşılaştırmalı analiz
"""
import re
import logging
import numpy as np
import pandas as pd
import sympy as sp
from scipy import stats
from typing import Dict, List, Tuple, Any, Optional
import statistics
from datetime import datetime, timedelta

# Güvenli Plotly import
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logging.warning("Plotly bulunamadı. Grafik özellikleri devre dışı.")


def make_json_safe(obj):
    """Numpy tiplerini JSON-safe Python tiplerine çevirir"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    elif hasattr(obj, 'item'):  # pandas scalar types
        return obj.item()
    return obj


class MathematicsEngine:
    def __init__(self):
        """Mathematics Engine'i başlat"""
        logging.info("Mathematics Engine başlatılıyor...")
        self.supported_operations = {
            'basic': ['toplama', 'çıkarma', 'çarpma', 'bölme', '+', '-', '*', '/', 'kaç eder', 'hesapla'],
            'statistics': ['ortalama', 'medyan', 'standart sapma', 'varyans', 'min', 'max', 'çeyreklik'],
            'percentages': ['yüzde', '%', 'artış', 'azalış', 'büyüme oranı'],
            'financial': ['faiz', 'kar', 'zarar', 'roi', 'ciro', 'gelir'],
            'advanced': ['korelasyon', 'regresyon', 'trend', 'tahmin']
        }
        logging.info("Mathematics Engine hazır.")

    def process_math_query(self, query: str, structured_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Matematik sorgusunu analiz eder ve uygun hesaplama yöntemini seçer.
        GÜNCELLENDİ: Özel sorgu tipleri ve veri temizleme eklendi
        
        Args:
            query: Kullanıcının matematik sorusu
            structured_data: Mevcut veri tabanı
            
        Returns:
            Dict: Sonuç, açıklama ve görselleştirme (JSON-safe)
        """
        logging.info(f"Matematik sorgusu işleniyor: '{query}'")
        
        try:
            # 1. Sorgu tipini belirle
            query_type = self._identify_query_type(query)
            logging.info(f"Sorgu tipi: {query_type}")
            
            # 2. Sayıları ve operatörleri çıkar
            numbers, operators, variables = self._extract_math_elements(query)
            
            # 3. Sorgu tipine göre işle - YENİ ÖZEL TİPLER EKLENDİ
            if query_type == 'employee_count':
                result = self._handle_employee_count(query, structured_data)
                
            elif query_type == 'basic_calculation':
                result = self._handle_basic_calculation(query, numbers, operators)
                
            elif query_type == 'data_statistics':
                result = self._handle_data_statistics(query, structured_data, variables)
                
            elif query_type == 'percentage_calculation':
                result = self._handle_percentage_calculation(query, numbers, structured_data)
                
            elif query_type == 'financial_analysis':
                result = self._handle_financial_analysis(query, structured_data, variables)
                
            elif query_type == 'comparison':
                result = self._handle_comparison(query, structured_data, variables)
                
            else:
                result = self._handle_general_math(query, numbers, operators)
            
            # JSON-safe hale getir
            return make_json_safe(result)
            
        except Exception as e:
            logging.error(f"Mathematics Engine genel hatası: {e}", exc_info=True)
            return {"text": f"Matematik işlemi sırasında hata oluştu: {str(e)}", "chart": None}

    def _identify_query_type(self, query: str) -> str:
        """Sorgunun matematik tipini belirler - GELİŞTİRİLDİ"""
        query_lower = query.lower()
        
        # ÖNCELİKLİ: Özel sorgu pattern'ları (daha spesifik olanlar önce)
        special_patterns = [
            (r'kaç kat.*maaş', 'comparison'),  # "kaç kat" soruları
            (r'maaş.*kaç kat', 'comparison'),  # "maaş kaç kat" soruları
            (r'toplam.*çalışan.*sayı', 'employee_count'),  # "toplam çalışan sayısı"
            (r'kaç.*çalışan', 'employee_count'),  # "kaç çalışan"
            (r'çalışan.*sayı', 'employee_count'),  # "çalışan sayısı"
            (r'departman.*ortalama.*fark', 'financial_analysis'),  # departman karşılaştırması
            (r'departman.*ortalama.*maaş', 'financial_analysis'),  # departman maaş analizi
        ]
        
        # Özel pattern'ları kontrol et
        for pattern, query_type in special_patterns:
            if re.search(pattern, query_lower):
                return query_type
        
        # Temel hesaplama pattern'ları
        basic_patterns = [
            r'\d+\s*[+\-*/]\s*\d+',  # 5 + 3, 100 * 12 gibi
            r'kaç eder',
            r'hesapla',
            r'toplam.*ne kadar',
            r'çarp.*kaç'
        ]
        
        # İstatistik pattern'ları
        stats_patterns = [
            r'ortalama.*(?:maaş|ciro|satış)',
            r'en yüksek.*(?:maaş|ciro|satış)',
            r'en düşük.*(?:maaş|ciro|satış)',
            r'standart sapma',
            r'medyan'
        ]
        
        # Yüzde hesaplama pattern'ları
        percentage_patterns = [
            r'yüzde kaç',
            r'%.*artış',
            r'büyüme oranı',
            r'kaç.*yüzde'
        ]
        
        # Pattern'ları kontrol et
        for pattern in basic_patterns:
            if re.search(pattern, query_lower):
                return 'basic_calculation'
                
        for pattern in stats_patterns:
            if re.search(pattern, query_lower):
                return 'data_statistics'
                
        for pattern in percentage_patterns:
            if re.search(pattern, query_lower):
                return 'percentage_calculation'
        
        return 'basic_calculation'  # Varsayılan

    def _extract_math_elements(self, query: str) -> Tuple[List[float], List[str], List[str]]:
        """Sorgudaki sayıları, operatörleri ve değişkenleri çıkarır"""
        
        # Sayıları çıkar (ondalıklı sayılar dahil)
        number_pattern = r'\d+\.?\d*'
        numbers = [float(match) for match in re.findall(number_pattern, query)]
        
        # Operatörleri çıkar
        operator_pattern = r'[+\-*/]'
        operators = re.findall(operator_pattern, query)
        
        # Türkçe operatör kelimelerini çevir
        turkish_operators = {
            'topla': '+', 'ekle': '+', 'artı': '+',
            'çıkar': '-', 'eksi': '-', 'çıkart': '-',
            'çarp': '*', 'kere': '*', 'ile çarp': '*',
            'böl': '/', 'bölü': '/', 'paylaş': '/'
        }
        
        for turkish_op, symbol in turkish_operators.items():
            if turkish_op in query.lower():
                operators.append(symbol)
        
        # Değişkenleri çıkar (maaş, ciro, satış gibi)
        variables = []
        variable_keywords = ['maaş', 'ciro', 'satış', 'gelir', 'gider', 'kar', 'zarar', 'çalışan', 'mağaza']
        for keyword in variable_keywords:
            if keyword in query.lower():
                variables.append(keyword)
        
        logging.info(f"Çıkarılan elementler - Sayılar: {numbers}, Operatörler: {operators}, Değişkenler: {variables}")
        return numbers, operators, variables

    def _handle_employee_count(self, query: str, structured_data: Dict) -> Dict:
        """Çalışan sayısı sorgularını özel olarak handle eder - YENİ METOD"""
        try:
            unique_employees = set()
            total_rows = 0
            processed_files = []
            
            for filename, df in structured_data.items():
                # Çalışan ismi sütununu bul
                emp_col = None
                for col in df.columns:
                    col_lower = col.lower()
                    if any(keyword in col_lower for keyword in ['ad soyad', 'çalışan', 'personel', 'employee', 'name']):
                        emp_col = col
                        break
                
                if emp_col:
                    # Boş olmayan ve anlamlı değerleri al
                    clean_employees = df[emp_col].dropna()
                    clean_employees = clean_employees.astype(str).str.strip()  # String'e çevir ve trim
                    clean_employees = clean_employees[clean_employees != '']  # Boş string'leri kaldır
                    clean_employees = clean_employees[clean_employees.str.len() > 2]  # Çok kısa değerleri kaldır
                    clean_employees = clean_employees[~clean_employees.str.lower().isin(['nan', 'null', 'none'])]  # Geçersiz değerleri kaldır
                    
                    total_rows += len(df)  # Debug için
                    unique_employees.update(clean_employees.unique())
                    processed_files.append(f"{filename}: {len(clean_employees)} geçerli kayıt")
            
            employee_count = len(unique_employees)
            
            if employee_count == 0:
                return {"text": "Sistemde çalışan verisi bulunamadı.", "chart": None}
            
            # Çalışan listesini alfabetik sırala
            sorted_employees = sorted(list(unique_employees))
            
            explanation = f"""
**👥 Çalışan Sayısı Analizi**

**Toplam Benzersiz Çalışan Sayısı:** {employee_count}

**Detaylar:**
- Sistemde kayıtlı toplam çalışan: {employee_count}
- İşlenen toplam satır sayısı: {total_rows}
- Veri temizleme: Boş, geçersiz ve tekrar eden kayıtlar kaldırıldı

**İşlenen Dosyalar:**
{chr(10).join([f"- {info}" for info in processed_files])}

**Çalışan Listesi:**
{chr(10).join([f"{i+1}. {name}" for i, name in enumerate(sorted_employees[:15])])}
{'...' if len(sorted_employees) > 15 else ''}
            """
            
            return {
                "text": explanation,
                "chart": None,
                "calculation_details": {
                    "employee_count": employee_count,
                    "total_rows": total_rows,
                    "unique_employees": sorted_employees,
                    "processed_files": processed_files
                }
            }
            
        except Exception as e:
            logging.error(f"Çalışan sayısı hesaplama hatası: {e}", exc_info=True)
            return {"text": f"Çalışan sayısı hesaplanamadı: {str(e)}", "chart": None}

    def _handle_basic_calculation(self, query: str, numbers: List[float], operators: List[str]) -> Dict:
        """Temel matematik işlemlerini yapar"""
        
        if len(numbers) < 2:
            return {
                "text": "Hesaplama için en az 2 sayıya ihtiyacım var. Örnek: '500 * 12 kaç eder?'",
                "chart": None,
                "calculation_details": None
            }
        
        try:
            # Basit iki sayı işlemi
            if len(numbers) == 2 and len(operators) >= 1:
                num1, num2 = float(numbers[0]), float(numbers[1])  # JSON-safe
                operator = operators[0]
                
                if operator == '+':
                    result = num1 + num2
                    operation_text = f"{num1} + {num2}"
                elif operator == '-':
                    result = num1 - num2
                    operation_text = f"{num1} - {num2}"
                elif operator == '*':
                    result = num1 * num2
                    operation_text = f"{num1} × {num2}"
                elif operator == '/':
                    if num2 == 0:
                        return {"text": "Sıfıra bölme hatası! Payda sıfır olamaz.", "chart": None}
                    result = num1 / num2
                    operation_text = f"{num1} ÷ {num2}"
                else:
                    return {"text": f"'{operator}' operatörünü desteklemiyorum.", "chart": None}
                
                result = float(result)  # JSON-safe
                
                # Sonucu formatla
                if result == int(result):
                    result_formatted = f"{int(result):,}".replace(',', '.')
                else:
                    result_formatted = f"{result:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                
                explanation = f"""
**🧮 Hesaplama Sonucu**

**İşlem:** {operation_text} = **{result_formatted}**

**Detaylar:**
- İlk sayı: {num1:,}
- İkinci sayı: {num2:,}
- Operatör: {operator}
- Sonuç: {result_formatted}
                """.replace(',', '.')
                
                return {
                    "text": explanation,
                    "chart": None,
                    "calculation_details": {
                        "operation": operation_text,
                        "result": result,
                        "formatted_result": result_formatted
                    }
                }
            
            # Karmaşık işlemler için sympy kullan
            else:
                return self._handle_complex_calculation(query, numbers, operators)
                
        except Exception as e:
            logging.error(f"Hesaplama hatası: {e}")
            return {
                "text": f"Hesaplama sırasında bir hata oluştu: {str(e)}",
                "chart": None
            }

    def _handle_complex_calculation(self, query: str, numbers: List[float], operators: List[str]) -> Dict:
        """Karmaşık matematik işlemleri için sympy kullanır"""
        try:
            # Sorgudan matematik ifadesini çıkar
            math_expression = re.sub(r'[^\d+\-*/().\s]', '', query)
            math_expression = re.sub(r'\s+', '', math_expression)
            
            if not math_expression:
                return {"text": "Geçerli bir matematik ifadesi bulamadım.", "chart": None}
            
            # Sympy ile hesapla
            result = sp.sympify(math_expression)
            result_value = float(result.evalf())  # JSON-safe
            
            # Sonucu formatla
            result_formatted = f"{result_value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            explanation = f"""
**🧮 Karmaşık Hesaplama Sonucu**

**İfade:** {math_expression} = **{result_formatted}**

**Adım adım çözüm:**
{self._show_calculation_steps(math_expression, result_value)}
            """
            
            return {
                "text": explanation,
                "chart": None,
                "calculation_details": {
                    "expression": math_expression,
                    "result": result_value,
                    "formatted_result": result_formatted
                }
            }
            
        except Exception as e:
            logging.error(f"Karmaşık hesaplama hatası: {e}")
            return {"text": f"Karmaşık hesaplama hatası: {str(e)}", "chart": None}

    def _handle_data_statistics(self, query: str, structured_data: Dict[str, pd.DataFrame], variables: List[str]) -> Dict:
        """Veri üzerinde istatistiksel hesaplamalar yapar - VERİ TEMİZLEME EKLENDİ"""
        
        if not structured_data:
            return {"text": "İstatistik hesaplama için veri bulunamadı.", "chart": None}
        
        # Hangi istatistiği istediğini belirle
        query_lower = query.lower()
        stat_type = None
        
        if any(word in query_lower for word in ['ortalama', 'mean', 'average']):
            stat_type = 'mean'
        elif any(word in query_lower for word in ['medyan', 'median']):
            stat_type = 'median'
        elif any(word in query_lower for word in ['maksimum', 'max', 'en yüksek', 'en büyük']):
            stat_type = 'max'
        elif any(word in query_lower for word in ['minimum', 'min', 'en düşük', 'en küçük']):
            stat_type = 'min'
        elif any(word in query_lower for word in ['toplam', 'sum', 'total']):
            stat_type = 'sum'
        elif any(word in query_lower for word in ['sayı', 'count', 'kaç tane']):
            stat_type = 'count'
        elif any(word in query_lower for word in ['standart sapma', 'std']):
            stat_type = 'std'
        else:
            stat_type = 'summary'  # Genel özet
        
        # Hangi sütun/değişken üzerinde işlem yapacağını belirle - GELİŞTİRİLDİ
        target_column = None
        target_data = None
        filename_found = None
        
        # Öncelik sırası: Spesifik sütunlar → Sayısal sütunlar
        priority_columns = {
            'maaş': ['maaş', 'salary', 'ücret', 'gelir'],
            'ciro': ['ciro', 'satış', 'sales', 'revenue', 'gelir'],
            'çalışan': ['ad soyad', 'çalışan', 'personel', 'employee', 'name']
        }
        
        # 1. Variables'ta belirtilen sütun tipini ara
        for var in variables:
            if var in priority_columns:
                for filename, df in structured_data.items():
                    for col in df.columns:
                        col_lower = col.lower()
                        if any(keyword in col_lower for keyword in priority_columns[var]):
                            # VERİ TEMİZLEME
                            clean_data = df[col].dropna()  # NaN'ları kaldır
                            
                            # Sayısal sütunlar için ekstra temizlik
                            if var in ['maaş', 'ciro']:
                                # Sadece sayısal değerleri al
                                clean_data = pd.to_numeric(clean_data, errors='coerce').dropna()
                                # Sıfır ve negatif değerleri kaldır (maaş/ciro için mantıksız)
                                clean_data = clean_data[clean_data > 0]
                            
                            # Metin sütunları için temizlik
                            elif var == 'çalışan':
                                # Boş string'leri kaldır
                                clean_data = clean_data.astype(str).str.strip()
                                clean_data = clean_data[clean_data != '']
                                clean_data = clean_data[clean_data.str.len() > 2]  # Çok kısa isimleri kaldır
                            
                            if len(clean_data) > 0:
                                target_column = col
                                target_data = clean_data
                                filename_found = filename
                                break
                    if target_data is not None:
                        break
                if target_data is not None:
                    break
        
        # 2. Spesifik bulunamadıysa, sayısal sütunları otomatik bul
        if target_data is None:
            for filename, df in structured_data.items():
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                
                # ID, index gibi sütunları atla
                filtered_columns = [col for col in numeric_columns 
                                  if not any(skip_word in col.lower() 
                                           for skip_word in ['id', 'index', 'no', 'sıra'])]
                
                if len(filtered_columns) > 0:
                    target_column = filtered_columns[0]  # İlk uygun sayısal sütunu al
                    
                    # VERİ TEMİZLEME
                    clean_data = df[target_column].dropna()
                    clean_data = pd.to_numeric(clean_data, errors='coerce').dropna()
                    clean_data = clean_data[clean_data > 0]  # Pozitif değerler
                    
                    if len(clean_data) > 0:
                        target_data = clean_data
                        filename_found = filename
                        break
        
        if target_data is None:
            return {"text": "Uygun sayısal veri bulunamadı.", "chart": None}
        
        if len(target_data) == 0:
            return {"text": f"'{target_column}' sütununda geçerli veri bulunamadı.", "chart": None}
        
        # İstatistiği hesapla - JSON-SAFE
        try:
            if stat_type == 'mean':
                result = float(target_data.mean())
                stat_name = "Ortalama"
            elif stat_type == 'median':
                result = float(target_data.median())
                stat_name = "Medyan"
            elif stat_type == 'max':
                result = float(target_data.max())
                stat_name = "Maksimum"
            elif stat_type == 'min':
                result = float(target_data.min())
                stat_name = "Minimum"
            elif stat_type == 'sum':
                result = float(target_data.sum())
                stat_name = "Toplam"
            elif stat_type == 'count':
                result = int(len(target_data))
                stat_name = "Sayı"
            elif stat_type == 'std':
                result = float(target_data.std())
                stat_name = "Standart Sapma"
            else:  # summary
                return self._create_full_statistics_summary(target_data, target_column)
            
            # Sonucu formatla
            if stat_type == 'count':
                result_formatted = f"{int(result)}"
            else:
                result_formatted = f"{result:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            explanation = f"""
**📊 {stat_name} Hesaplaması**

**{target_column}** sütunu için **{stat_name.lower()}**: **{result_formatted}**

**Veri Detayları:**
- Toplam geçerli kayıt sayısı: {len(target_data)}
- Hesaplanan değer: {result_formatted}
- Sütun: {target_column}
- Dosya: {filename_found}
- Veri temizleme: Boş, sıfır ve geçersiz değerler kaldırıldı
            """
            
            # Basit görselleştirme oluştur
            chart_data = None
            if len(target_data) > 1:
                chart_data = self._create_statistics_chart(target_data, target_column, stat_type, result)
            
            return {
                "text": explanation,
                "chart": chart_data,
                "calculation_details": {
                    "statistic_type": stat_type,
                    "column": target_column,
                    "result": result,
                    "data_count": int(len(target_data)),
                    "filename": filename_found
                }
            }
            
        except Exception as e:
            logging.error(f"İstatistik hesaplama hatası: {e}")
            return {"text": f"İstatistik hesaplama hatası: {str(e)}", "chart": None}

    def _create_full_statistics_summary(self, data: pd.Series, column_name: str) -> Dict:
        """Tam istatistiksel özet oluşturur"""
        try:
            summary_stats = {
                'count': int(len(data)),                    # JSON-safe
                'mean': float(data.mean()),                 # JSON-safe
                'median': float(data.median()),             # JSON-safe
                'std': float(data.std()),                   # JSON-safe
                'min': float(data.min()),                   # JSON-safe
                'max': float(data.max()),                   # JSON-safe
                'q25': float(data.quantile(0.25)),          # JSON-safe
                'q75': float(data.quantile(0.75))           # JSON-safe
            }
            
            explanation = f"""
**📈 {column_name} - Detaylı İstatistiksel Analiz**

**Temel İstatistikler:**
- **Kayıt Sayısı:** {summary_stats['count']}
- **Ortalama:** {summary_stats['mean']:,.2f}
- **Medyan:** {summary_stats['median']:,.2f}
- **Standart Sapma:** {summary_stats['std']:,.2f}

**Aralık Bilgileri:**
- **Minimum:** {summary_stats['min']:,.2f}
- **Maksimum:** {summary_stats['max']:,.2f}
- **1. Çeyreklik (Q1):** {summary_stats['q25']:,.2f}
- **3. Çeyreklik (Q3):** {summary_stats['q75']:,.2f}

**Yorumlar:**
- Veri aralığı: {summary_stats['max'] - summary_stats['min']:,.2f}
- Çeyrekler arası aralık (IQR): {summary_stats['q75'] - summary_stats['q25']:,.2f}
- Değişim katsayısı: %{(summary_stats['std'] / summary_stats['mean'] * 100):,.1f}
            """.replace(',', 'X').replace('.', ',').replace('X', '.')
            
            # Box plot grafiği oluştur
            chart_data = self._create_box_plot(data, column_name)
            
            return {
                "text": explanation,
                "chart": chart_data,
                "calculation_details": summary_stats  # Already JSON-safe
            }
            
        except Exception as e:
            logging.error(f"İstatistik özeti hatası: {e}")
            return {"text": f"İstatistik özeti hatası: {str(e)}", "chart": None}

    def _create_statistics_chart(self, data: pd.Series, column_name: str, stat_type: str, result: float) -> Dict:
        """İstatistik için basit grafik oluşturur"""
        try:
            # Chart.js formatında basit grafik (Plotly sorunlarını önlemek için)
            return {
                'type': 'bar',
                'title': f'{column_name} İstatistik Özeti',
                'data': {
                    'labels': ['Min', 'Q1', 'Medyan', 'Q3', 'Max'],
                    'data': [
                        float(data.min()),
                        float(data.quantile(0.25)),
                        float(data.median()),
                        float(data.quantile(0.75)),
                        float(data.max())
                    ]
                }
            }
            
        except Exception as e:
            logging.error(f"Box plot oluşturma hatası: {e}")
            return None

    def _handle_percentage_calculation(self, query: str, numbers: List[float], structured_data: Dict) -> Dict:
        """Yüzde hesaplamalarını yapar"""
        query_lower = query.lower()
        
        # Yüzde hesaplama türünü belirle
        if 'artış' in query_lower or 'büyüme' in query_lower:
            return self._calculate_growth_rate(numbers, query)
        elif 'azalış' in query_lower or 'düşüş' in query_lower:
            return self._calculate_decline_rate(numbers, query)
        elif 'yüzde kaç' in query_lower:
            return self._calculate_percentage_of(numbers, query)
        else:
            return self._calculate_general_percentage(numbers, query)

    def _calculate_growth_rate(self, numbers: List[float], query: str) -> Dict:
        """Büyüme oranı hesaplar"""
        if len(numbers) < 2:
            return {"text": "Büyüme oranı için eski ve yeni değere ihtiyacım var.", "chart": None}
        
        old_value, new_value = float(numbers[0]), float(numbers[1])  # JSON-safe
        
        if old_value == 0:
            return {"text": "Başlangıç değeri sıfır olamaz.", "chart": None}
        
        growth_rate = float(((new_value - old_value) / old_value) * 100)  # JSON-safe
        
        explanation = f"""
**📈 Büyüme Oranı Hesaplaması**

**Eski Değer:** {old_value:,.2f}
**Yeni Değer:** {new_value:,.2f}
**Büyüme Oranı:** %{growth_rate:,.2f}

**Hesaplama:**
((Yeni Değer - Eski Değer) / Eski Değer) × 100
(({new_value:,.2f} - {old_value:,.2f}) / {old_value:,.2f}) × 100 = %{growth_rate:,.2f}

**Yorum:** 
{'📈 Pozitif büyüme (artış)' if growth_rate > 0 else '📉 Negatif büyüme (azalış)' if growth_rate < 0 else '➡️ Değişiklik yok'}
        """.replace(',', 'X').replace('.', ',').replace('X', '.')
        
        return {
            "text": explanation,
            "chart": None,
            "calculation_details": {
                "old_value": old_value,
                "new_value": new_value,
                "growth_rate": growth_rate
            }
        }

    def _show_calculation_steps(self, expression: str, result: float) -> str:
        """Hesaplama adımlarını gösterir"""
        try:
            steps = f"""
1. İfade: {expression}
2. Sonuç: {result:,.2f}
3. Bilimsel gösterim: {result:.2e}
            """.replace(',', '.')
            return steps
        except:
            return "Adım adım çözüm gösterilemiyor."

    def _handle_financial_analysis(self, query: str, structured_data: Dict, variables: List[str]) -> Dict:
        """Finansal analiz yapar - GELİŞTİRİLDİ"""
        try:
            query_lower = query.lower()
            
            # Departman bazlı maaş analizi ve karşılaştırması
            if 'departman' in query_lower:
                return self._handle_department_salary_analysis(query, structured_data)
            
            return {"text": "Finansal analiz özelliği geliştirilmekte.", "chart": None}
            
        except Exception as e:
            logging.error(f"Finansal analiz hatası: {e}", exc_info=True)
            return {"text": "Finansal analiz sırasında bir hata oluştu.", "chart": None}

    def _handle_comparison(self, query: str, structured_data: Dict, variables: List[str]) -> Dict:
        """Karşılaştırma analizi yapar - GELİŞTİRİLDİ"""
        try:
            query_lower = query.lower()
            
            # "En yüksek maaşlı çalışanın maaşı en düşük maaşlı çalışanın maaşının kaç katıdır?" gibi sorgular
            if 'kaç kat' in query_lower and 'maaş' in query_lower:
                return self._handle_ratio_calculation(query, structured_data)
            
            # Genel karşılaştırma
            return {"text": "Karşılaştırma analizi geliştirilmekte. Lütfen daha spesifik bir soru sorun.", "chart": None}
            
        except Exception as e:
            logging.error(f"Karşılaştırma analizi hatası: {e}", exc_info=True)
            return {"text": "Karşılaştırma analizi sırasında bir hata oluştu.", "chart": None}

    def _calculate_decline_rate(self, numbers: List[float], query: str) -> Dict:
        """Azalış oranı hesaplar"""
        return self._calculate_growth_rate(numbers, query)  # Aynı formül

    def _calculate_percentage_of(self, numbers: List[float], query: str) -> Dict:
        """X'in Y'nin yüzde kaçı hesaplar"""
        if len(numbers) < 2:
            return {"text": "Yüzde hesaplama için 2 sayıya ihtiyacım var.", "chart": None}
        
        part, whole = float(numbers[0]), float(numbers[1])  # JSON-safe
        percentage = float((part / whole) * 100)  # JSON-safe
        
        explanation = f"""
**🔢 Yüzde Hesaplaması**

**{part:,.2f}**, **{whole:,.2f}**'nin **%{percentage:.2f}**'sidir.

**Hesaplama:**
({part:,.2f} / {whole:,.2f}) × 100 = %{percentage:.2f}
        """.replace(',', 'X').replace('.', ',').replace('X', '.')
        
        return {"text": explanation, "chart": None}

    def _calculate_general_percentage(self, numbers: List[float], query: str) -> Dict:
        """Genel yüzde hesaplaması"""
        return {"text": "Genel yüzde hesaplaması için daha spesifik bilgi gerekli.", "chart": None}

    def _handle_general_math(self, query: str, numbers: List[float], operators: List[str]) -> Dict:
        """Genel matematik işlemleri"""
        return self._handle_basic_calculation(query, numbers, operators)

    def _handle_ratio_calculation(self, query: str, structured_data: Dict) -> Dict:
        """Oran hesaplama yapar (kaç kat, kaç misli)"""
        try:
            # Maaş verilerini bul
            salary_data = None
            salary_column = None
            filename_found = None
            
            for filename, df in structured_data.items():
                for col in df.columns:
                    if any(keyword in col.lower() for keyword in ['maaş', 'salary', 'ücret']):
                        # VERİ TEMİZLEME
                        clean_data = df[col].dropna()
                        clean_data = pd.to_numeric(clean_data, errors='coerce').dropna()
                        clean_data = clean_data[clean_data > 0]  # Pozitif maaşlar
                        
                        if len(clean_data) > 0:
                            salary_data = clean_data
                            salary_column = col
                            filename_found = filename
                            break
                if salary_data is not None:
                    break
            
            if salary_data is None or len(salary_data) == 0:
                return {"text": "Geçerli maaş verisi bulunamadı.", "chart": None}
            
            # JSON-SAFE: numpy tiplerini Python tipine çevir
            max_salary = float(salary_data.max())
            min_salary = float(salary_data.min())
            
            if min_salary == 0:
                return {"text": "En düşük maaş sıfır olduğu için oran hesaplanamıyor.", "chart": None}
            
            ratio = float(max_salary / min_salary)
            
            # En yüksek ve en düşük maaşlı çalışanları bul
            original_df = None
            for filename, df in structured_data.items():
                if filename == filename_found:
                    original_df = df
                    break
            
            max_employee = "Bilinmiyor"
            min_employee = "Bilinmiyor"
            
            if original_df is not None:
                emp_col = next((c for c in original_df.columns if 'ad soyad' in c.lower()), None)
                salary_col = salary_column
                
                if emp_col and salary_col:
                    # En yüksek maaşlı
                    max_idx = original_df[salary_col].idxmax()
                    max_employee = str(original_df.loc[max_idx, emp_col])
                    
                    # En düşük maaşlı
                    min_idx = original_df[original_df[salary_col] > 0][salary_col].idxmin()
                    min_employee = str(original_df.loc[min_idx, emp_col])
            
            explanation = f"""
**📊 Maaş Oranı Analizi**

**En Yüksek Maaş:** {max_salary:,.0f} TL ({max_employee})
**En Düşük Maaş:** {min_salary:,.0f} TL ({min_employee})  
**Oran:** En yüksek maaş, en düşük maaşın **{ratio:.1f} katıdır**

**Hesaplama:**
{max_salary:,.0f} ÷ {min_salary:,.0f} = {ratio:.1f}

**Yorum:**
{'🟢 Makul maaş farkı' if ratio < 5 else '🟡 Orta düzey fark' if ratio < 10 else '🔴 Yüksek maaş farkı'}

**Veri Detayları:**
- Analiz edilen çalışan sayısı: {len(salary_data)}
- Dosya: {filename_found}
- Sütun: {salary_column}
            """.replace(',', 'X').replace('.', ',').replace('X', '.')
            
            return {
                "text": explanation,
                "chart": None,
                "calculation_details": {
                    "max_salary": max_salary,  # JSON-safe
                    "min_salary": min_salary,  # JSON-safe
                    "ratio": ratio,            # JSON-safe
                    "max_employee": max_employee,
                    "min_employee": min_employee,
                    "data_count": int(len(salary_data))
                }
            }
            
        except Exception as e:
            logging.error(f"Oran hesaplama hatası: {e}", exc_info=True)
            return {"text": f"Oran hesaplama sırasında hata oluştu: {str(e)}", "chart": None}

    def _handle_department_salary_analysis(self, query: str, structured_data: Dict) -> Dict:
        """Departman bazlı maaş analizi yapar - FINAL FIX"""
        try:
            query_lower = query.lower()
            
            # ÖNCE: Sistemdeki gerçek departmanları bul
            actual_departments = set()
            for filename, df in structured_data.items():
                dept_col = None
                for col in df.columns:
                    col_lower = col.lower()
                    if any(keyword in col_lower for keyword in ['departman', 'department', 'birim', 'bölüm']):
                        dept_col = col
                        break
                
                if dept_col:
                    unique_depts = df[dept_col].dropna().unique()
                    actual_departments.update([str(dept).strip() for dept in unique_depts])
            
            logging.info(f"Sistemde bulunan gerçek departmanlar: {actual_departments}")
            
            # Departman eşleştirme - gerçek departman isimleri kullan
            target_department = None
            target_department_real = None
            
            # Direkt eşleşme ara
            for actual_dept in actual_departments:
                if actual_dept.lower() in query_lower:
                    target_department = actual_dept.lower()
                    target_department_real = actual_dept
                    break
            
            # Kısmi eşleşme ara
            if not target_department:
                for actual_dept in actual_departments:
                    dept_words = actual_dept.lower().split()
                    for word in dept_words:
                        if len(word) > 2 and word in query_lower:
                            target_department = actual_dept.lower()
                            target_department_real = actual_dept
                            break
                    if target_department:
                        break
            
            # Alias eşleştirme (son çare)
            if not target_department:
                alias_mapping = {
                    'bilgi': 'Bilgi İşlem',
                    'işlem': 'Bilgi İşlem', 
                    'it': 'Bilgi İşlem',
                    'muhasebe': 'Muhasebe',
                    'mali': 'Muhasebe',
                    'yönetim': 'Yönetim',
                    'management': 'Yönetim',
                    'ürün': 'Ürün Yönetimi',
                    'product': 'Ürün Yönetimi',
                    'insan': 'İnsan Kaynakları',
                    'ik': 'İnsan Kaynakları',
                    'hr': 'İnsan Kaynakları',
                    'web': 'Web'
                }
                
                for alias, dept_name in alias_mapping.items():
                    if alias in query_lower and dept_name in actual_departments:
                        target_department = dept_name.lower()
                        target_department_real = dept_name
                        break
            
            if not target_department:
                dept_list = sorted(list(actual_departments))
                return {
                    "text": f"Hangi departman hakkında bilgi istediğinizi belirtmediniz.\n\n**Sistemde bulunan departmanlar:**\n" + 
                        "\n".join([f"• {dept}" for dept in dept_list]),
                    "chart": None
                }
            
            logging.info(f"Hedef departman: {target_department_real}")
            
            # Departman verilerini topla
            dept_salary_data = []
            all_salary_data = []
            dept_employees = []
            
            for filename, df in structured_data.items():
                dept_col = None
                salary_col = None
                emp_col = None
                
                # Sütunları bul
                for col in df.columns:
                    col_lower = col.lower()
                    if 'departman' in col_lower or 'department' in col_lower:
                        dept_col = col
                    elif any(k in col_lower for k in ['maaş', 'salary', 'ücret']):
                        salary_col = col
                    elif any(k in col_lower for k in ['ad soyad', 'isim', 'name']):
                        emp_col = col
                
                if dept_col and salary_col:
                    # Tüm maaşlar
                    all_salaries = pd.to_numeric(df[salary_col], errors='coerce').dropna()
                    all_salaries = all_salaries[all_salaries > 0]
                    all_salary_data.extend([float(x) for x in all_salaries.tolist()])
                    
                    # Hedef departman - TAM EŞLEŞMEesine odaklan
                    dept_mask = df[dept_col].str.strip().str.lower() == target_department_real.lower()
                    
                    if dept_mask.any():
                        dept_rows = df.loc[dept_mask]
                        dept_salaries = pd.to_numeric(dept_rows[salary_col], errors='coerce').dropna()
                        dept_salaries = dept_salaries[dept_salaries > 0]
                        dept_salary_data.extend([float(x) for x in dept_salaries.tolist()])
                        
                        if emp_col:
                            dept_emp_names = dept_rows[emp_col].dropna()
                            dept_employees.extend(dept_emp_names.tolist())
            
            logging.info(f"Departman maaş sayısı: {len(dept_salary_data)}, Genel maaş sayısı: {len(all_salary_data)}")
            
            if not dept_salary_data:
                return {
                    "text": f"**{target_department_real}** departmanında maaş verisi bulunamadı.\n\n**Olası nedenler:**\n• Departman adı tam eşleşmiyor\n• Maaş verisi eksik\n• Veri formatı hatalı",
                    "chart": None
                }
            
            if not all_salary_data:
                return {"text": "Genel maaş verisi bulunamadı.", "chart": None}
            
            # Hesaplamalar
            dept_avg = float(sum(dept_salary_data) / len(dept_salary_data))
            general_avg = float(sum(all_salary_data) / len(all_salary_data))
            difference = float(dept_avg - general_avg)
            percentage_diff = float((difference / general_avg) * 100)
            
            # Departman min/max
            dept_min = float(min(dept_salary_data))
            dept_max = float(max(dept_salary_data))
            
            explanation = f"""**📊 {target_department_real} Departmanı Maaş Analizi**

    **Karşılaştırmalı Analiz:**
    • **{target_department_real} Ortalama Maaş:** {dept_avg:,.0f} TL
    • **Genel Ortalama Maaş:** {general_avg:,.0f} TL
    • **Fark:** {abs(difference):,.0f} TL ({'⬆️ Yüksek' if difference > 0 else '⬇️ Düşük'})
    • **Yüzde Farkı:** %{abs(percentage_diff):,.1f} ({'üzerinde' if difference > 0 else 'altında'})

    **{target_department_real} Detayları:**
    • **Çalışan Sayısı:** {len(dept_salary_data)}
    • **En Düşük Maaş:** {dept_min:,.0f} TL
    • **En Yüksek Maaş:** {dept_max:,.0f} TL
    • **Maaş Aralığı:** {dept_max - dept_min:,.0f} TL

    **Genel Bilgiler:**
    • **Toplam Çalışan:** {len(all_salary_data)}
    • **Departman Oranı:** %{(len(dept_salary_data) / len(all_salary_data) * 100):,.1f}

    **{target_department_real} Çalışanları:**
    {chr(10).join([f"• {name}" for name in dept_employees[:10]])}
    {'...' if len(dept_employees) > 10 else ''}

    **Yorum:**
    {target_department_real} departmanı maaşları şirket ortalamasının {'üzerinde' if difference > 0 else 'altında'} seyrediyor.""".replace(',', '.')
            
            return {"text": explanation, "chart": None}
            
        except Exception as e:
            logging.error(f"Departman maaş analizi hatası: {e}", exc_info=True)
            return {"text": f"Departman analizi sırasında hata oluştu: {str(e)}", "chart": None}

    def _create_statistics_chart(self, data: pd.Series, column_name: str, stat_type: str, result: float) -> Dict:
            """İstatistik için basit grafik oluşturur"""
            try:
                return {
                    'type': 'bar',
                    'title': f'{column_name} İstatistik Analizi',
                    'data': {
                        'labels': [stat_type.title()],
                        'data': [float(result)]
                    }
                }
            except Exception as e:
                logging.error(f"Grafik oluşturma hatası: {e}")
                return None

    def _create_box_plot(self, data: pd.Series, column_name: str) -> Dict:
        """Box plot grafiği oluşturur"""
        try:
            return {
                'type': 'bar',
                'title': f'{column_name} İstatistik Özeti',
                'data': {
                    'labels': ['Min', 'Q1', 'Medyan', 'Q3', 'Max'],
                    'data': [
                        float(data.min()),
                        float(data.quantile(0.25)),
                        float(data.median()),
                        float(data.quantile(0.75)),
                        float(data.max())
                    ]
                }
            }
        except Exception as e:
            logging.error(f"Box plot oluşturma hatası: {e}")
            return None

    def _create_full_statistics_summary(self, data: pd.Series, column_name: str) -> Dict:
        """Tam istatistiksel özet oluşturur"""
        try:
            summary_stats = {
                'count': int(len(data)),
                'mean': float(data.mean()),
                'median': float(data.median()),
                'std': float(data.std()),
                'min': float(data.min()),
                'max': float(data.max()),
                'q25': float(data.quantile(0.25)),
                'q75': float(data.quantile(0.75))
            }
            
            explanation = f"""
**📈 {column_name} - Detaylı İstatistiksel Analiz**

**Temel İstatistikler:**
- **Kayıt Sayısı:** {summary_stats['count']}
- **Ortalama:** {summary_stats['mean']:,.2f}
- **Medyan:** {summary_stats['median']:,.2f}
- **Standart Sapma:** {summary_stats['std']:,.2f}

**Aralık Bilgileri:**
- **Minimum:** {summary_stats['min']:,.2f}
- **Maksimum:** {summary_stats['max']:,.2f}
            """.replace(',', '.')
            
            chart_data = self._create_box_plot(data, column_name)
            
            return {
                "text": explanation,
                "chart": chart_data,
                "calculation_details": summary_stats
            }
            
        except Exception as e:
            logging.error(f"İstatistik özeti hatası: {e}")
            return {"text": f"İstatistik özeti hatası: {str(e)}", "chart": None}