# data_loader.py
"""
Farklı dosya formatlarındaki (Excel, CSV, PDF, Word) verileri okumak,
işlemek ve standart bir yapıda döndürmekle sorumludur.
"""
import os
import logging
import pandas as pd
from typing import Tuple, Dict, List, Any

# Gerekli kütüphaneler: pip install pandas openpyxl pypdf python-docx

class UniversalDataLoader:
    def _load_excel(self, file_path: str) -> pd.DataFrame:
        return pd.read_excel(file_path, engine='openpyxl')

    def _load_csv(self, file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except UnicodeDecodeError:
            logging.warning(f"'{file_path}' için UTF-8 denendi, olmadı. 'latin1' ile deneniyor.")
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
        """DataFrame'i analiz eder ve mağaza, çalışan gibi özel bilgileri çıkarır."""
        insights = {'store_rows': {}, 'employee_rows': {}}
        df = df.fillna('').apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        store_col = next((c for c in df.columns if any(k in c.lower() for k in ['mağaza', 'store', 'şube'])), None)
        emp_col = next((c for c in df.columns if any(k in c.lower() for k in ['ad soyad', 'çalışan', 'personel'])), None)
        
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
        """Atlanması gereken dosyaları kontrol eder."""
        skip_patterns = [
            '~$',  # Excel geçici dosyaları
            '.tmp',  # Geçici dosyalar
            '.temp',  # Geçici dosyalar
            '__pycache__',  # Python cache
            '.DS_Store',  # macOS sistem dosyası
            'Thumbs.db',  # Windows thumbnail cache
        ]
        
        for pattern in skip_patterns:
            if pattern in filename:
                return True
        return False

    def load_all_data(self, data_directory: str) -> Tuple[Dict, Dict, Dict]:
        """
        Verilen dizindeki tüm desteklenen dosyaları yükler ve işler.
        Returns:
            knowledge_base: Dosya adı -> içerik (DataFrame veya metin)
            structured_data: Dosya adı -> DataFrame
            data_insights: Dosya adı -> çıkarımlar (mağaza/çalışan bilgileri vb.)
        """
        knowledge_base = {}
        structured_data = {}
        data_insights = {}

        if not os.path.isdir(data_directory):
            logging.error(f"Veri dizini bulunamadı: '{data_directory}'")
            return knowledge_base, structured_data, data_insights

        for filename in os.listdir(data_directory):
            file_path = os.path.join(data_directory, filename)
            
            # Dosya kontrolü
            if not os.path.isfile(file_path):
                continue
                
            # Atlanması gereken dosyaları kontrol et
            if self._should_skip_file(filename):
                logging.info(f"'{filename}' dosyası atlandı (geçici/sistem dosyası).")
                continue

            file_ext = os.path.splitext(filename)[1].lower()
            content = None
            insights = {}
            
            try:
                logging.info(f"'{filename}' dosyası işleniyor...")
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
                    logging.info(f"'{filename}' desteklenmeyen dosya formatı, atlandı.")
                    continue
                
                if content is not None:
                    knowledge_base[filename] = content
                    data_insights[filename] = insights
                    logging.info(f"'{filename}' başarıyla yüklendi.")
                
            except Exception as e:
                logging.error(f"'{filename}' dosyası yüklenirken hata oluştu: {e}")
                # Dosya yükleme hatası durumunda devam et, uygulamayı durdurma

        logging.info(f"Toplam {len(knowledge_base)} dosya başarıyla yüklendi.")
        return knowledge_base, structured_data, data_insights