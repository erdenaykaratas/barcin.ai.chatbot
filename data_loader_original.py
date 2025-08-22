# data_loader.py - GÜNCELLENMIŞ VERSİYON
"""
FarklÄ± dosya formatlarÄ±ndaki (Excel, CSV, PDF, Word) verileri okumak,
iÅŸlemek ve standart bir yapÄ±da dÃ¶ndÃ¼rmekle sorumludur.
"""
import os
import logging
import pandas as pd
from typing import Tuple, Dict, List, Any

# Enhanced Data Processor import - YENİ EKLENEN
try:
    from new_data_processor import NewDataProcessor
    from advanced_analytics_engine import AdvancedAnalyticsEngine
    ENHANCED_PROCESSING = True
except ImportError:
    ENHANCED_PROCESSING = False
    logging.warning("Gelişmiş data processor bulunamadı")

# Gerekli kÃ¼tÃ¼phaneler: pip install pandas openpyxl pypdf python-docx

class UniversalDataLoader:
    def __init__(self):
        # YENİ EKLENEN - Gelişmiş işlemciler
        if ENHANCED_PROCESSING:
            self.new_processor = NewDataProcessor()
            self.analytics_engine = AdvancedAnalyticsEngine()
            logging.info("Gelişmiş veri işleme sistemi aktif")
        else:
            self.new_processor = None
            self.analytics_engine = None
            
    def _load_excel(self, file_path: str) -> pd.DataFrame:
        return pd.read_excel(file_path, engine='openpyxl')

    def _load_csv(self, file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except UnicodeDecodeError:
            logging.warning(f"'{file_path}' iÃ§in UTF-8 denendi, olmadÄ±. 'latin1' ile deneniyor.")
            return pd.read_csv(file_path, encoding='latin1')

    def _load_pdf(self, file_path: str) -> str:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    def _load_docx(self, file_path: str) -> str:
        from docx import Document
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    def _process_structured_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """DataFrame'i analiz eder ve maÄŸaza, Ã§alÄ±ÅŸan gibi Ã¶zel bilgileri Ã§Ä±karÄ±r."""
        insights = {'store_rows': {}, 'employee_rows': {}}
        df = df.fillna('').apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        store_col = next((c for c in df.columns if any(k in c.lower() for k in ['maÄŸaza', 'store', 'ÅŸube'])), None)
        emp_col = next((c for c in df.columns if any(k in c.lower() for k in ['ad soyad', 'Ã§alÄ±ÅŸan', 'personel'])), None)
        
        if store_col:
            for _, row in df.iterrows():
                name = row[store_col]
                if name: insights['store_rows'][name] = row.to_dict()
        if emp_col:
            for _, row in df.iterrows():
                name = row[emp_col]
                if name: insights['employee_rows'][name] = row.to_dict()
        
        return insights

    def _should_skip_file(self, filename: str) -> bool:
        """AtlanmasÄ± gereken dosyalarÄ± kontrol eder."""
        skip_patterns = [
            '~$',  # Excel geÃ§ici dosyalarÄ±
            '.tmp',  # GeÃ§ici dosyalar
            '.temp',  # GeÃ§ici dosyalar
            '__pycache__',  # Python cache
            '.DS_Store',  # macOS sistem dosyasÄ±
            'Thumbs.db',  # Windows thumbnail cache
        ]
        
        for pattern in skip_patterns:
            if pattern in filename:
                return True
        return False

    def load_all_data(self, data_directory: str) -> Tuple[Dict, Dict, Dict]:
        """
        Verilen dizindeki tÃ¼m desteklenen dosyalarÄ± yÃ¼kler ve iÅŸler.
        Returns:
            knowledge_base: Dosya adÄ± -> iÃ§erik (DataFrame veya metin)
            structured_data: Dosya adÄ± -> DataFrame
            data_insights: Dosya adÄ± -> Ã§Ä±karÄ±mlar (maÄŸaza/Ã§alÄ±ÅŸan bilgileri vb.)
        """
        knowledge_base = {}
        structured_data = {}
        data_insights = {}

        if not os.path.isdir(data_directory):
            logging.error(f"Veri dizini bulunamadÄ±: '{data_directory}'")
            return knowledge_base, structured_data, data_insights

        for filename in os.listdir(data_directory):
            file_path = os.path.join(data_directory, filename)
            
            # Dosya kontrolÃ¼
            if not os.path.isfile(file_path):
                continue
                
            # AtlanmasÄ± gereken dosyalarÄ± kontrol et
            if self._should_skip_file(filename):
                logging.info(f"'{filename}' dosyasÄ± atlandÄ± (geÃ§ici/sistem dosyasÄ±).")
                continue

            file_ext = os.path.splitext(filename)[1].lower()
            content = None
            insights = {}
            
            try:
                logging.info(f"'{filename}' dosyasÄ± iÅŸleniyor...")
                if file_ext in ['.xlsx', '.xls']:
                    content = self._load_excel(file_path)
                    insights = self._process_structured_data(content)
                    insights['type'] = 'excel'
                    structured_data[filename] = content
                elif file_ext == '.csv':
                    content = self._load_csv(file_path)
                    insights = self._process_structured_data(content)
                    insights['type'] = 'csv'
                    structured_data[filename] = content
                elif file_ext == '.pdf':
                    content = self._load_pdf(file_path)
                    insights['type'] = 'pdf'
                elif file_ext == '.docx':
                    content = self._load_docx(file_path)
                    insights['type'] = 'word'
                else:
                    logging.info(f"'{filename}' desteklenmeyen dosya formatÄ±, atlandÄ±.")
                    continue
                
                if content is not None:
                    knowledge_base[filename] = content
                    data_insights[filename] = insights
                    
                    # YENİ EKLENEN - Gelişmiş analiz
                    if self.new_processor and self.analytics_engine and isinstance(content, pd.DataFrame):
                        try:
                            # Temel analiz
                            basic_analysis = self.new_processor.analyze_file(content, filename)
                            
                            # Gelişmiş analiz  
                            advanced_analysis = self.analytics_engine.comprehensive_analysis(content, filename)
                            
                            # Sonuçları birleştir
                            data_insights[filename].update({
                                'basic_analysis': basic_analysis,
                                'advanced_analysis': advanced_analysis,
                                'smart_insights': self.new_processor.generate_insights(basic_analysis),
                                'query_suggestions': self.new_processor.suggest_queries(basic_analysis)
                            })
                            
                            logging.info(f"Gelişmiş analiz tamamlandı: {filename}")
                        except Exception as e:
                            logging.warning(f"Gelişmiş analiz hatası {filename}: {e}")
                    
                    logging.info(f"'{filename}' baÅŸarÄ±yla yÃ¼klendi.")
                
            except Exception as e:
                logging.error(f"'{filename}' dosyasÄ± yÃ¼klenirken hata oluÅŸtu: {e}")
                # Dosya yÃ¼kleme hatasÄ± durumunda devam et, uygulamayÄ± durdurma

        logging.info(f"Toplam {len(knowledge_base)} dosya baÅŸarÄ±yla yÃ¼klendi.")
        return knowledge_base, structured_data, data_insights