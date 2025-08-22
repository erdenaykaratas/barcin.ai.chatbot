# knowledge_processor.py
"""
Metin ve tablo verilerini işler, anlamsal vektörler oluşturur (embedding)
ve aranabilir bir FAISS indeksi (AI hafızası) inşa eder.
"""
import os
import pickle
import logging
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL, INDEX_PATH, CHUNKS_PATH

class KnowledgeProcessor:
    def __init__(self):
        logging.info(f"Embedding modeli '{EMBEDDING_MODEL}' yükleniyor...")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.index = None
        self.chunks: List[str] = []
        logging.info("Model başarıyla yüklendi.")

    def is_ready(self) -> bool:
        """AI hafızasının (index) kullanıma hazır olup olmadığını kontrol eder."""
        return self.index is not None

    def get_chunk_count(self) -> int:
        """Hafızadaki toplam chunk sayısını döndürür."""
        return len(self.chunks)

    def _chunk_text(self, text: str, source: str, chunk_size=512, overlap=50) -> list[str]:
        """Metni daha küçük, yönetilebilir parçalara (chunk) böler."""
        if not isinstance(text, str): return []
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_content = text[start:end]
            chunks.append(f"Kaynak: {source}\nİçerik: {chunk_content}")
            start += chunk_size - overlap
        return chunks

    def process_knowledge_base(self, knowledge_base: dict):
        """
        Verilen bilgi tabanını işler, chunk'lara ayırır, vektörlere dönüştürür
        ve FAISS indeksini oluşturur ya da yükler.
        """
        if os.path.exists(INDEX_PATH) and os.path.exists(CHUNKS_PATH):
            try:
                logging.info("Kayıtlı AI hafızası (FAISS index ve chunks) yükleniyor...")
                self.index = faiss.read_index(INDEX_PATH)
                with open(CHUNKS_PATH, 'rb') as f:
                    self.chunks = pickle.load(f)
                logging.info(f"AI hafızası başarıyla yüklendi. {self.index.ntotal} vektör bulundu.")
                return
            except Exception as e:
                logging.warning(f"Kayıtlı hafıza yüklenemedi: {e}. Hafıza yeniden oluşturulacak.")

        logging.info("Yeni bir AI hafızası oluşturuluyor...")
        all_chunks = []
        for filename, content in knowledge_base.items():
            if isinstance(content, str):
                all_chunks.extend(self._chunk_text(content, filename))
            elif isinstance(content, pd.DataFrame):
                for _, row in content.iterrows():
                    row_text = ", ".join([f"{col}: {val}" for col, val in row.items() if str(val).strip()])
                    all_chunks.append(f"Kaynak: {filename} (Satır Verisi)\nİçerik: {row_text}")
        
        if not all_chunks:
            logging.warning("İşlenecek veri bulunamadı. AI hafızası oluşturulamadı.")
            return

        self.chunks = all_chunks
        logging.info(f"Toplam {len(self.chunks)} metin parçası (chunk) oluşturuldu. Vektörler hesaplanıyor...")
        
        embeddings = self.model.encode(self.chunks, show_progress_bar=True, batch_size=64)
        
        logging.info("FAISS vektör indeksi oluşturuluyor...")
        d = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(d)
        self.index.add(np.array(embeddings, dtype='float32'))
        
        try:
            faiss.write_index(self.index, INDEX_PATH)
            with open(CHUNKS_PATH, 'wb') as f:
                pickle.dump(self.chunks, f)
            logging.info(f"AI hafızası başarıyla oluşturuldu ve '{INDEX_PATH}' dosyasına kaydedildi.")
        except Exception as e:
            logging.error(f"AI hafızası diske kaydedilirken hata oluştu: {e}")

    def search(self, query: str, k=5) -> list[str]:
        """Verilen sorgu için anlamsal olarak en alakalı metin parçalarını bulur."""
        if not self.is_ready():
            return ["AI hafızası henüz oluşturulmadı."]
        
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding, dtype='float32'), k)
        
        return [self.chunks[i] for i in indices[0] if i < len(self.chunks)]