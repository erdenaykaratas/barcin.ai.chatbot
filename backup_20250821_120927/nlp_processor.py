# nlp_processor.py
"""
SmartNLPProcessor - Kural tabanlı doğal dil işleme ve niyet tahmini sınıfı.
GÜNCELLEME: Matematik sorgularını tanıma özellikleri eklendi.
"""
import re
from thefuzz import fuzz
from typing import Dict, List

class SmartNLPProcessor:
    def __init__(self):
        self.synonyms = {
            'listele': ['göster', 'say', 'ver', 'getir', 'list', 'sırala'],
            'kaç': ['ne kadar', 'how many', 'count', 'sayısı', 'toplam'],
            'çalışan': ['personel', 'employee', 'kişi', 'kullanıcı'],
            'maaş': ['salary', 'ücret', 'gelir'],
            'mağaza': ['store', 'şube'],
            'satış': ['ciro', 'sales', 'revenue'],
            'internet': ['web', 'ağ', 'bağlantı'],
            'departman': ['birim', 'bölüm'],
            # YENİ EKLENEN - Matematik terimleri
            'hesapla': ['calculate', 'compute', 'işle', 'bul'],
            'ortalama': ['average', 'mean', 'ort'],
            'toplam': ['sum', 'total', 'toplam'],
            'maksimum': ['max', 'maximum', 'en yüksek', 'en büyük'],
            'minimum': ['min', 'minimum', 'en düşük', 'en küçük'],
            'yüzde': ['percent', '%', 'percentage']
        }
        
        self.intent_patterns = {
            "count_department_employees": [['kaç', 'çalışan', 'departman'], ['departman', 'çalışan', 'sayısı']],
            "list_department_employees": [['listele', 'çalışan', 'departman']],
            "store_query": [['mağaza'], ['satış'], ['ciro']],
            "individual_salary": [['maaş', 'çalışan']],
            "list_all_employees": [['listele', 'çalışan'], ['tüm çalışanlar'], ['herkesi göster']],
            "salary_analysis": [['ortalama', 'maaş']],
            "web_search": [['internet'], ['hava durumu'], ['dolar kuru'], ['google\'da ara']],
            
            # YENİ EKLENEN - Matematik intent'leri
            "mathematical_calculation": [
                ['hesapla'], ['kaç eder'], ['toplam'], ['çarp'], ['böl'], ['çıkar'], ['topla'],
                ['ortalama'], ['medyan'], ['maksimum'], ['minimum'], ['standart sapma'],
                ['yüzde'], ['artış'], ['büyüme oranı'], ['kar oranı']
            ],
            "data_statistics": [
                ['ortalama', 'maaş'], ['ortalama', 'ciro'], ['ortalama', 'satış'],
                ['toplam', 'çalışan'], ['maksimum', 'maaş'], ['minimum', 'ciro'],
                ['en yüksek'], ['en düşük'], ['istatistik']
            ],
            "percentage_calculation": [
                ['yüzde', 'kaç'], ['artış', 'oranı'], ['büyüme', 'oranı'], 
                ['azalış', 'oranı'], ['değişim', 'oranı']
            ]
        }
        
        self.store_names: Dict[str, str] = {}
        self.employee_names: Dict[str, str] = {}
        self.department_names: List[str] = ['bilgi işlem', 'muhasebe', 'yönetim', 'ürün yönetimi', 'insan kaynakları', 'web']

        # YENİ EKLENEN - Matematik anahtar kelimeleri
        self.math_keywords = {
            'calculation': ['hesapla', 'calculate', 'kaç eder', '+', '-', '*', '/', 'çarp', 'böl', 'topla', 'çıkar'],
            'statistics': ['ortalama', 'average', 'mean', 'medyan', 'median', 'maksimum', 'max', 'minimum', 'min', 
                          'standart sapma', 'std', 'varyans', 'variance'],
            'aggregation': ['toplam', 'sum', 'total', 'sayı', 'count', 'adet'],
            'percentage': ['yüzde', 'percent', '%', 'oran', 'rate', 'artış', 'büyüme', 'azalış', 'değişim'],
            'comparison': ['karşılaştır', 'compare', 'fark', 'difference', 'hangi daha', 'en iyi', 'en kötü']
        }

    def add_store_names(self, store_names: List[str]):
        for name in store_names:
            if name and isinstance(name, str): self.store_names[name.lower()] = name

    def add_employee_names(self, employee_names: List[str]):
        for name in employee_names:
            if name and isinstance(name, str): self.employee_names[name.lower()] = name

    def _normalize_text(self, text: str) -> List[str]:
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.split()

    def _find_entities(self, text: str) -> Dict:
        entities = {'stores': [], 'employees': [], 'departments': [], 'numbers': [], 'math_operations': []}
        text_lower = text.lower()
        
        # Mağaza isimleri
        for store_lower, store_original in self.store_names.items():
            if store_lower in text_lower:
                entities['stores'].append(store_original)
        
        # YENİ EKLENEN - Sayıları çıkar
        number_pattern = r'\d+\.?\d*'
        numbers = [float(match) for match in re.findall(number_pattern, text)]
        entities['numbers'] = numbers
        
        # YENİ EKLENEN - Matematik operasyonlarını tespit et
        for operation_type, keywords in self.math_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    entities['math_operations'].append(operation_type)
                    break
        
        # Çalışan isimleri (iyileştirildi)
        if len(text_lower.split()) < 4: # Kısa sorgularda isim arama
            best_match_score = 0
            best_match_name = None
            for emp_lower, emp_original in self.employee_names.items():
                score = fuzz.token_set_ratio(text_lower, emp_lower)
                if score > best_match_score:
                    best_match_score = score
                    best_match_name = emp_original
            
            if best_match_score > 80: # Yüksek bir eşik belirle
                entities['employees'].append(best_match_name)

        # Departmanlar
        for dept_name in self.department_names:
            if dept_name in text_lower:
                entities['departments'].append(dept_name.title())
                
        return entities

    def predict_intent(self, text: str, data_insights: Dict) -> Dict:
        words = self._normalize_text(text)
        expanded_words = set(words)
        for word in words:
            for key, values in self.synonyms.items():
                if word in values:
                    expanded_words.add(key)
        
        scores = {intent: 0 for intent in self.intent_patterns}
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if all(p in expanded_words for p in pattern):
                    scores[intent] += len(pattern) * 2

        entities = self._find_entities(text)
        
        # YENİ EKLENEN - Özel durum kontrolü
        text_lower = text.lower()
        
        # "Toplam çalışan sayısı" sorgularını matematik olarak işaretle
        if any(phrase in text_lower for phrase in ['toplam çalışan', 'kaç çalışan', 'çalışan sayısı']):
            scores['data_statistics'] = scores.get('data_statistics', 0) + 20
        
        # "En yüksek maaşlı" vs "en düşük maaşlı" karşılaştırma sorgularını işaretle
        if 'kat' in text_lower and ('maaş' in text_lower or 'salary' in text_lower):
            scores['mathematical_calculation'] = scores.get('mathematical_calculation', 0) + 25
        
        # YENİ EKLENEN - Matematik sorguları için özel puanlama
        if entities['numbers'] and entities['math_operations']:
            # Sayılar ve matematik operasyonları varsa matematik intent'ine yüksek puan ver
            if 'calculation' in entities['math_operations']:
                scores['mathematical_calculation'] = scores.get('mathematical_calculation', 0) + 15
            if 'statistics' in entities['math_operations']:
                scores['data_statistics'] = scores.get('data_statistics', 0) + 15
            if 'percentage' in entities['math_operations']:
                scores['percentage_calculation'] = scores.get('percentage_calculation', 0) + 15

        # Mevcut entity-based puanlama
        if entities['stores']: scores['store_query'] = scores.get('store_query', 0) + 10
        if entities['employees']: scores['individual_salary'] = scores.get('individual_salary', 0) + 10
        if entities['departments'] and 'kaç' in expanded_words:
            scores['count_department_employees'] = scores.get('count_department_employees', 0) + 10
        elif entities['departments'] and 'listele' in expanded_words:
            scores['list_department_employees'] = scores.get('list_department_employees', 0) + 10

        best_intent = max(scores, key=scores.get) if any(s > 0 for s in scores.values()) else 'unknown'
        
        if best_intent == 'unknown':
            if any(w in expanded_words for w in ['internet', 'google', 'hava', 'dolar']):
                best_intent = 'web_search'
            else:
                best_intent = 'summarize_context'

        return {'intent': best_intent, 'entities': entities}

    def is_math_query(self, text: str) -> bool:
        """
        Verilen metnin matematik sorgusu olup olmadığını kontrol eder.
        
        Args:
            text: Analiz edilecek metin
            
        Returns:
            bool: Matematik sorgusu ise True
        """
        entities = self._find_entities(text)
        
        # Sayı + matematik operasyonu kombinasyonu
        if entities['numbers'] and entities['math_operations']:
            return True
            
        # Belirli matematik pattern'ları
        math_patterns = [
            r'\d+\s*[+\-*/]\s*\d+',  # 5 + 3, 100 * 12 gibi
            r'kaç eder',
            r'hesapla',
            r'ortalama.*(?:maaş|ciro|satış)',
            r'toplam.*(?:çalışan|mağaza)',
            r'yüzde.*(?:kaç|artış|büyüme)'
        ]
        
        text_lower = text.lower()
        for pattern in math_patterns:
            if re.search(pattern, text_lower):
                return True
                
        return False

    def extract_math_context(self, text: str) -> Dict:
        """
        Matematik sorgusu için bağlamsal bilgileri çıkarır.
        
        Args:
            text: Analiz edilecek metin
            
        Returns:
            Dict: Çıkarılan bağlamsal bilgiler
        """
        entities = self._find_entities(text)
        
        context = {
            'numbers': entities['numbers'],
            'operations': entities['math_operations'],
            'data_columns': [],
            'calculation_type': None
        }
        
        text_lower = text.lower()
        
        # Veri sütunlarını belirle
        if any(word in text_lower for word in ['maaş', 'salary', 'ücret']):
            context['data_columns'].append('maaş')
        if any(word in text_lower for word in ['ciro', 'satış', 'sales', 'revenue']):
            context['data_columns'].append('ciro')
        if any(word in text_lower for word in ['çalışan', 'employee', 'personel']):
            context['data_columns'].append('çalışan')
            
        # Hesaplama tipini belirle
        if any(word in text_lower for word in ['ortalama', 'average', 'mean']):
            context['calculation_type'] = 'average'
        elif any(word in text_lower for word in ['toplam', 'sum', 'total']):
            context['calculation_type'] = 'sum'
        elif any(word in text_lower for word in ['maksimum', 'max', 'en yüksek']):
            context['calculation_type'] = 'max'
        elif any(word in text_lower for word in ['minimum', 'min', 'en düşük']):
            context['calculation_type'] = 'min'
        elif any(word in text_lower for word in ['yüzde', 'percent', 'oran']):
            context['calculation_type'] = 'percentage'
            
        return context