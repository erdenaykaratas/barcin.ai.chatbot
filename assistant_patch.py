# assistant_patch.py - Otomatik entegrasyon kodu
# Bu kodu assistant.py'e manuel olarak entegre edin

# 1. Import eklemeleri (dosya başına):

# Enhanced Data Processor import - YENİ EKLENEN
try:
    from enhanced_data_processor import EnhancedDataProcessor
    ENHANCED_PROCESSOR_AVAILABLE = True
except ImportError:
    ENHANCED_PROCESSOR_AVAILABLE = False
    logging.warning("Enhanced Data Processor bulunamadı, temel analiz kullanılacak")


# 2. AIAssistant.__init__ metoduna ekleyin:

        # Enhanced Data Processor - YENİ EKLENEN
        if ENHANCED_PROCESSOR_AVAILABLE:
            self.enhanced_processor = EnhancedDataProcessor()
            logging.info("Enhanced Data Processor başarıyla yüklendi")
        else:
            self.enhanced_processor = None


# 3. AIAssistant sınıfına yeni metodlar ekleyin:

    def _handle_sales_analysis(self, query: str, entities: Dict) -> Dict:
        """Satış verisi analizi için özel işleyici - YENİ EKLENEN"""
        
        if not self.enhanced_processor:
            return {"text": "Gelişmiş satış analizi şu anda kullanılamıyor.", "chart": None}
        
        # Sales.xlsx dosyasını bul
        sales_data = None
        sales_filename = None
        
        for filename, df in self.structured_data.items():
            if 'sales' in filename.lower() or 'satış' in filename.lower():
                sales_data = df
                sales_filename = filename
                break
        
        if sales_data is None:
            return {"text": "Satış verisi bulunamadı. Lütfen sales.xlsx dosyasının yüklendiğinden emin olun.", "chart": None}
        
        # Enhanced analysis
        analysis = self.enhanced_processor.analyze_excel_structure(sales_data, sales_filename)
        insights = self.enhanced_processor.generate_smart_insights(analysis)
        
        # Query'ye göre spesifik analiz
        query_lower = query.lower()
        
        if 'ortalama' in query_lower and 'ciro' in query_lower:
            if '2024' in query_lower:
                col_name = 'Ciro 2024 (TRY-KDV siz)'
            elif '2025' in query_lower:
                col_name = 'Ciro 2025 (TRY-KDV siz)'
            else:
                col_name = 'Ciro 2024 (TRY-KDV siz)'  # Default
            
            if col_name in sales_data.columns:
                avg_value = sales_data[col_name].mean()
                total_stores = len(sales_data)
                
                response = f"""
**📊 Ciro Analizi Sonuçları**

**Ortalama Ciro ({col_name.split('(')[0].strip()}):** {avg_value:,.2f} TL

**Detaylar:**
- Toplam mağaza sayısı: {total_stores}
- En yüksek ciro: {sales_data[col_name].max():,.2f} TL
- En düşük ciro: {sales_data[col_name].min():,.2f} TL
- Standart sapma: {sales_data[col_name].std():,.2f} TL

**En İyi Performans Gösteren 3 Mağaza:**
""".replace(',', '.')
                
                top_stores = sales_data.nlargest(3, col_name)
                for i, (_, row) in enumerate(top_stores.iterrows(), 1):
                    response += f"
{i}. {row['Mağaza Adı']}: {row[col_name]:,.2f} TL".replace(',', '.')
                
                return {"text": response, "chart": None}
        
        elif 'en yüksek' in query_lower or 'en iyi' in query_lower:
            # En yüksek ciro analizi
            if '2025' in query_lower:
                col_name = 'Ciro 2025 (TRY-KDV siz)'
            else:
                col_name = 'Ciro 2024 (TRY-KDV siz)'
            
            if col_name in sales_data.columns:
                max_idx = sales_data[col_name].idxmax()
                best_store = sales_data.loc[max_idx]
                
                response = f"""
**🏆 En Yüksek Ciro Analizi**

**En İyi Performans:** {best_store['Mağaza Adı']}
**Ciro Tutarı:** {best_store[col_name]:,.2f} TL

**Karşılaştırma:**
- Ortalamadan fark: +{(best_store[col_name] - sales_data[col_name].mean()):,.2f} TL
- Büyüme oranı: %{best_store['Ciro % Büyüme(24den25e)']:,.1f}

**Top 5 Mağaza:**
""".replace(',', '.')
                
                top5 = sales_data.nlargest(5, col_name)
                for i, (_, row) in enumerate(top5.iterrows(), 1):
                    response += f"
{i}. {row['Mağaza Adı']}: {row[col_name]:,.2f} TL".replace(',', '.')
                
                return {"text": response, "chart": None}
        
        elif 'büyüme' in query_lower or 'artış' in query_lower:
            # Büyüme analizi
            growth_col = 'Ciro % Büyüme(24den25e)'
            if growth_col in sales_data.columns:
                avg_growth = sales_data[growth_col].mean()
                positive_growth = (sales_data[growth_col] > 0).sum()
                negative_growth = (sales_data[growth_col] < 0).sum()
                
                response = f"""
**📈 Ciro Büyüme Analizi**

**Genel Büyüme:** %{avg_growth:.2f}

**Performans Dağılımı:**
- Pozitif büyüme gösteren: {positive_growth} mağaza
- Negatif büyüme gösteren: {negative_growth} mağaza
- Toplam mağaza sayısı: {len(sales_data)}

**En Yüksek Büyüme Gösteren 3 Mağaza:**
""".replace(',', '.')
                
                top_growth = sales_data.nlargest(3, growth_col)
                for i, (_, row) in enumerate(top_growth.iterrows(), 1):
                    response += f"
{i}. {row['Mağaza Adı']}: %{row[growth_col]:.2f}".replace(',', '.')
                
                response += f"

**En Düşük Performans Gösteren 3 Mağaza:**"
                bottom_growth = sales_data.nsmallest(3, growth_col)
                for i, (_, row) in enumerate(bottom_growth.iterrows(), 1):
                    response += f"
{i}. {row['Mağaza Adı']}: %{row[growth_col]:.2f}".replace(',', '.')
                
                return {"text": response, "chart": None}
        
        # Genel analiz
        response = f"""
**📊 Gelişmiş Satış Veri Analizi**

**Dosya:** {sales_filename}
**Veri Kalitesi:** {len(insights)} insight tespit edildi

**Akıllı Çıkarımlar:**
"""
        for insight in insights:
            response += f"
• {insight}"
        
        response += f"

**Önerilen Sorular:**"
        suggestions = self.enhanced_processor.create_query_suggestions(analysis)
        for suggestion in suggestions[:5]:
            response += f"
• {suggestion}"
        
        return {"text": response, "chart": None}
    
    def _needs_enhanced_analysis(self, query: str) -> bool:
        """Sorgunun gelişmiş analiz gerektirip gerektirmediğini kontrol eder - YENİ EKLENEN"""
        
        enhanced_keywords = [
            'analiz', 'karşılaştır', 'trend', 'performans', 'rapor',
            'dağılım', 'istatistik', 'insight', 'çıkarım'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in enhanced_keywords)
    
    def _is_sales_query(self, query: str) -> bool:
        """Satış sorgularını tespit eder - YENİ EKLENEN"""
        
        sales_keywords = [
            'ciro', 'satış', 'mağaza', 'büyüme', 'gelir', 'performans',
            'revenue', 'sales', 'store', 'growth'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in sales_keywords)


# 4. process_query metodunun başına ekleyin:

        # Enhanced Data Processor kontrolü - YENİ EKLENEN
        if self.enhanced_processor and self._is_sales_query(query):
            return self._handle_sales_analysis(query, entities)
        
        # Gelişmiş analiz gerekli mi kontrol et - YENİ EKLENEN
        if self.enhanced_processor and self._needs_enhanced_analysis(query):
            # Gelişmiş analiz mantığı burada implementasyonu geliştirilecek
            pass

