# assistant.py
"""
AI Assistant'ın tüm mantığını içeren ana sınıf.
Veri yükleme, işleme, sorgu anlama ve cevap üretme işlemlerini yönetir.
GÜNCELLEME: Mathematics Engine entegrasyonu eklendi.
"""
import logging
import re
import requests
from typing import Dict, List, Optional

import pandas as pd

from auth import User
from config import (DATA_DIRECTORY, GENERATIVE_MODEL_API_URL, SERPAPI_API_KEY,
                    CONTEXT_MAX_LENGTH, SIMILARITY_SEARCH_K)
from data_loader import UniversalDataLoader
from knowledge_processor import KnowledgeProcessor
from nlp_processor import SmartNLPProcessor
from mathematics_engine import MathematicsEngine  # YENİ EKLENEN


class AIAssistant:
    def __init__(self):
        logging.info(f"AI Assistant beyni başlatılıyor...")
        self.data_loader = UniversalDataLoader()
        self.knowledge_proc = KnowledgeProcessor()
        self.nlp_proc = SmartNLPProcessor()
        self.math_engine = MathematicsEngine()  # YENİ EKLENEN - Mathematics Engine
        
        self.knowledge_base: Dict[str, any] = {}
        self.structured_data: Dict[str, pd.DataFrame] = {}
        self.data_insights: Dict[str, Dict] = {}
        self._initialize_system()

    def _initialize_system(self):
        """Sistemi başlatır, tüm verileri yükler ve işler."""
        logging.info(f"'{DATA_DIRECTORY}' klasöründen veriler yükleniyor...")
        self.knowledge_base, self.structured_data, self.data_insights = self.data_loader.load_all_data(DATA_DIRECTORY)
        
        if not self.knowledge_base:
            logging.warning("Hiçbir veri yüklenemedi. Asistan sınırlı modda çalışacak.")
            return

        logging.info(f"Toplam {len(self.knowledge_base)} dosya yüklendi. AI hafızası oluşturuluyor...")
        self.knowledge_proc.process_knowledge_base(self.knowledge_base)

        all_store_names = set()
        all_employee_names = set()
        for df in self.structured_data.values():
            store_col = next((c for c in df.columns if any(k in c.lower() for k in ['mağaza', 'store', 'şube'])), None)
            emp_col = next((c for c in df.columns if any(k in c.lower() for k in ['ad soyad', 'çalışan'])), None)
            if store_col: all_store_names.update(df[store_col].dropna().unique())
            if emp_col: all_employee_names.update(df[emp_col].dropna().unique())

        self.nlp_proc.add_store_names(list(all_store_names))
        self.nlp_proc.add_employee_names(list(all_employee_names))
        logging.info("AI Assistant başlatma işlemi tamamlandı ve hazır.")

    def get_status(self):
        return { 
            'total_files': len(self.knowledge_base), 
            'ai_memory_ready': self.knowledge_proc.is_ready(),
            'math_engine_ready': True  # Mathematics Engine durumu
        }

    def process_query(self, query: str, user: User) -> Dict:
        try:
            logging.info(f"Kullanıcı '{user.id}' (Rol: {user.role}) sorgu yapıyor: '{query}'")
            
            # YENİ EKLENEN: Matematik sorgularını önce kontrol et - GÜVENLİ
            try:
                if self._is_math_query(query):
                    logging.info("Matematik sorgusu tespit edildi, Mathematics Engine'e yönlendiriliyor.")
                    math_result = self.math_engine.process_math_query(query, self.structured_data)
                    
                    # Sonuç kontrolü
                    if not isinstance(math_result, dict):
                        math_result = {"text": "Matematik hesaplama hatası oluştu.", "chart": None}
                    if 'text' not in math_result:
                        math_result['text'] = "Hesaplama tamamlanamadı."
                    if 'chart' not in math_result:
                        math_result['chart'] = None
                        
                    return math_result
                    
            except Exception as math_error:
                logging.error(f"Mathematics Engine hatası: {math_error}")
                # Matematik hatası durumunda normal flow'a devam et
            
            # Mevcut intent analizi
            entities = self.nlp_proc.predict_intent(query, self.data_insights)
            intent = entities.get('intent', 'unknown')
            logging.info(f"Tespit edilen niyet: {intent}, Varlıklar: {entities.get('entities')}")

            if intent in ['individual_salary', 'salary_analysis'] and user.role != 'admin':
                return {"text": "Maaş bilgilerine erişim yetkiniz bulunmamaktadır.", "chart": None}

            tool_to_use = self._select_tool(intent)
            if tool_to_use:
                return tool_to_use(query, entities)
            
            return self._tool_summarize_context(query, entities)
            
        except Exception as e:
            logging.error(f"Process query genel hatası: {e}", exc_info=True)
            return {"text": "Sorgu işlenirken bir hata oluştu. Lütfen daha basit bir soru deneyin.", "chart": None}

    def _is_math_query(self, query: str) -> bool:
        """
        Sorgunun matematik sorusu olup olmadığını kontrol eder.
        GÜNCELLENDİ: Daha güvenli ve spesifik kontroller
        """
        try:
            query_lower = query.lower()
            
            # Matematik anahtar kelimeleri
            math_keywords = [
                # Temel işlemler
                'kaç eder', 'hesapla', 'topla', 'çıkar', 'çarp', 'böl',
                '+', '-', '*', '/', 'toplam', 'fark', 'çarpım', 'bölüm',
                
                # İstatistik - DAHA SPESİFİK
                'ortalama maaş', 'medyan', 'maksimum', 'minimum', 'standart sapma',
                'mean', 'median', 'max', 'min', 'std', 'average',
                'en yüksek maaş', 'en düşük maaş', 'en büyük', 'en küçük',
                
                # Yüzde hesaplamaları
                'yüzde', '%', 'artış', 'azalış', 'büyüme oranı', 'yüzde kaç',
                'oranı', 'değişim', 'artış oranı', 'düşüş oranı',
                
                # Özel matematik sorguları
                'kaç kat', 'kat', 'misli', 'çalışan sayısı', 'toplam çalışan',
                'kaç çalışan', 'toplam.*çalışan'
            ]
            
            # Pattern kontrolü
            for keyword in math_keywords:
                if keyword in query_lower:
                    return True
            
            # Sayı + operatör kombinasyonu kontrolü (regex)
            import re
            math_patterns = [
                r'\d+\s*[+\-*/]\s*\d+',  # 5 + 3, 100 * 12 gibi
                r'\d+.*ile.*\d+',  # 5 ile 3 çarp gibi
                r'.*maaş.*kaç kat.*',  # maaş kaç kat sorguları
                r'toplam.*sayı.*'  # toplam sayı sorguları
            ]
            
            for pattern in math_patterns:
                if re.search(pattern, query_lower):
                    return True
            
            # Sayı + matematik context kontrolü
            has_numbers = bool(re.search(r'\d+', query))
            has_math_context = any(word in query_lower for word in [
                'maaş', 'ciro', 'satış', 'gelir', 'gider', 'kar', 'zarar',
                'çalışan sayısı', 'toplam', 'ortalama', 'hesapla'
            ])
            
            if has_numbers and has_math_context:
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Math query check hatası: {e}")
            return False

    def _select_tool(self, intent: str) -> Optional[callable]:
        tool_map = {
            "store_query": self._tool_get_store_data,
            "individual_salary": self._tool_get_employee_data,
            "list_all_employees": self._tool_get_employee_data,
            "count_department_employees": self._tool_count_department_employees,
            "web_search": self._tool_web_search
        }
        return tool_map.get(intent)

    # --- ARAÇLAR (TÜMÜ GÜNCELLENDİ) ---
    # Artık tüm araçlar ham DataFrame'ler (`self.structured_data`) üzerinden çalışır. Bu, tutarlılığı ve sağlamlığı artırır.
    
    def _tool_get_store_data(self, query: str, entities: Dict) -> Dict:
        store_name = entities['entities'].get('stores', [None])[0]
        if not store_name:
            return {"text": "Lütfen hangi mağaza hakkında bilgi istediğinizi belirtin.", "chart": None}
            
        for filename, df in self.structured_data.items():
            store_col = next((c for c in df.columns if any(k in c.lower() for k in ['mağaza', 'store', 'şube'])), None)
            if not store_col: continue

            # Harf büyüklüğüne ve baştaki/sondaki boşluklara duyarsız arama
            store_data_row = df[df[store_col].str.strip().str.lower() == store_name.lower()]
            
            if not store_data_row.empty:
                data = store_data_row.iloc[0].to_dict()
                text = f"**{store_name} Mağazası Verileri:**\n"
                chart_data = {'labels': [], 'data': []}
                for key, value in data.items():
                    text += f"- {str(key)}: {value}\n"
                    # Grafik verisi hazırlama (sağlamlaştırıldı)
                    if isinstance(key, str) and 'ciro' in key.lower():
                        try:
                            clean_value_str = re.sub(r'[^\d.]', '', str(value).replace(',', ''))
                            if clean_value_str:
                                chart_data['labels'].append(key)
                                chart_data['data'].append(float(clean_value_str))
                        except (ValueError, TypeError): continue
                
                chart = {'type': 'bar', 'title': f'{store_name} Ciro Bilgileri', 'data': chart_data} if chart_data['labels'] else None
                return {"text": text, "chart": chart}
                
        return {"text": f"'{store_name}' adlı mağaza için veri bulunamadı.", "chart": None}
    
    def _tool_count_department_employees(self, query: str, entities: Dict) -> Dict:
        department_name = entities['entities'].get('departments', [None])[0]
        if not department_name:
            return {"text": "Hangi departmanı saymamı istediğinizi anlayamadım.", "chart": None}
        
        total_employees = set()
        for df in self.structured_data.values():
            dept_col = next((c for c in df.columns if 'departman' in c.lower()), None)
            emp_col = next((c for c in df.columns if 'ad soyad' in c.lower()), None)
            if not (dept_col and emp_col): continue
            
            # GÜNCELLENDİ: Daha esnek arama. 'bilgi işlem' sorgusu, 'Bilgi İşlem Departmanı'nı bulur.
            dept_employees = df[df[dept_col].str.lower().str.contains(department_name.lower(), na=False)]
            if not dept_employees.empty:
                total_employees.update(dept_employees[emp_col].dropna().unique())

        count = len(total_employees)
        if count > 0:
            return {"text": f"**{department_name.title()}** departmanında toplam **{count}** kişi çalışmaktadır.", "chart": None}
        else:
            return {"text": f"**{department_name.title()}** departmanında çalışan bulunamadı veya bu veriyi içeren bir dosya yok.", "chart": None}

    def _tool_get_employee_data(self, query: str, entities: Dict) -> Dict:
        employee_name = entities['entities'].get('employees', [None])[0]
        if not employee_name:
            # Tüm çalışanları listeleme
            all_employees = set()
            for df in self.structured_data.values():
                emp_col = next((c for c in df.columns if 'ad soyad' in c.lower()), None)
                if emp_col: all_employees.update(df[emp_col].dropna().unique())
            if not all_employees: return {"text": "Sistemde çalışan verisi bulunamadı.", "chart": None}
            text = f"Toplam **{len(all_employees)}** çalışan bulundu:\n- " + "\n- ".join(sorted(list(all_employees)))
            return {"text": text, "chart": None}

        # Tek bir çalışanı arama
        for df in self.structured_data.values():
            emp_col = next((c for c in df.columns if 'ad soyad' in c.lower()), None)
            if not emp_col: continue
            
            emp_data_row = df[df[emp_col].str.strip().str.lower() == employee_name.lower()]
            if not emp_data_row.empty:
                data = emp_data_row.iloc[0].to_dict()
                text = f"**{employee_name} Çalışan Bilgileri:**\n"
                for key, value in data.items(): text += f"- {str(key)}: {value}\n"
                return {"text": text, "chart": None}
                
        return {"text": f"'{employee_name}' adlı çalışan için veri bulunamadı.", "chart": None}

    def _tool_summarize_context(self, query: str, entities: Dict) -> Dict:
        relevant_chunks = self.knowledge_proc.search(query, k=SIMILARITY_SEARCH_K)
        if not relevant_chunks or "henüz oluşturulmadı" in relevant_chunks[0]:
            return self._tool_web_search(query, entities)

        context = "\n\n".join(relevant_chunks)[:CONTEXT_MAX_LENGTH]
        prompt = f"Aşağıdaki bağlamı kullanarak soruya kısa ve net bir Türkçe cevap ver.\n\nBağlam:\n---\n{context}\n---\n\nSoru: {query}\n\nCevap:"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(GENERATIVE_MODEL_API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            answer = result['candidates'][0]['content']['parts'][0]['text'].strip()
            return {"text": answer, "chart": None}
        except Exception as e:
            logging.error(f"Gemini API hatası: {e}. Web aramasına yönlendiriliyor.")
            return self._tool_web_search(query, entities)

    def _tool_web_search(self, query: str, entities: Dict) -> Dict:
        if not SERPAPI_API_KEY:
            return {"text": "Web araması için API anahtarı yapılandırılmamış.", "chart": None}
        try:
            params = {"q": query, "api_key": SERPAPI_API_KEY, "hl": "tr", "gl": "tr"}
            response = requests.get("https://serpapi.com/search", params=params, timeout=10)
            response.raise_for_status()
            results = response.json().get("organic_results", [])
            if not results: return {"text": f"'{query}' için internette sonuç bulunamadı.", "chart": None}
            snippets = [f"**{r.get('title', '')}**\n{r.get('snippet', '')}" for r in results[:3] if r.get('snippet')]
            answer = "\n\n".join(snippets)
            return {"text": f"İnternetten bulunan sonuçlar:\n\n{answer}", "chart": None}
        except Exception as e:
            logging.error(f"Web arama hatası: {e}")
            return {"text": "Web araması sırasında bir hata oluştu.", "chart": None}