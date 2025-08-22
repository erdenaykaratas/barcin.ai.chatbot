
# quick_sales_analyzer.py - Hızlı satış analizi wrapper
from enhanced_data_processor import EnhancedDataProcessor
import pandas as pd
import os

class QuickSalesAnalyzer:
    def __init__(self):
        self.processor = EnhancedDataProcessor()
        self.sales_data = None
        self.load_sales_data()
    
    def load_sales_data(self):
        """Satış verilerini yükle"""
        possible_files = ['sales.xlsx', 'company_data/sales.xlsx', 'satış.xlsx']
        
        for filename in possible_files:
            if os.path.exists(filename):
                try:
                    self.sales_data = pd.read_excel(filename)
                    print(f"✅ {filename} başarıyla yüklendi")
                    return
                except Exception as e:
                    print(f"❌ {filename} yüklenemedi: {e}")
        
        print("❌ Satış verisi bulunamadı")
    
    def analyze_query(self, query: str) -> str:
        """Satış sorgularını analiz et"""
        
        if self.sales_data is None:
            return "❌ Satış verisi yüklü değil"
        
        query_lower = query.lower()
        
        # Ortalama ciro sorguları
        if 'ortalama' in query_lower and 'ciro' in query_lower:
            if '2024' in query_lower:
                col = 'Ciro 2024 (TRY-KDV siz)'
            elif '2025' in query_lower:
                col = 'Ciro 2025 (TRY-KDV siz)'
            else:
                col = 'Ciro 2024 (TRY-KDV siz)'
            
            if col in self.sales_data.columns:
                avg = self.sales_data[col].mean()
                return f"📊 {col.split('(')[0].strip()} ortalaması: {avg:,.2f} TL".replace(',', '.')
        
        # En yüksek ciro sorguları
        elif 'en yüksek' in query_lower or 'en iyi' in query_lower:
            if '2025' in query_lower:
                col = 'Ciro 2025 (TRY-KDV siz)'
            else:
                col = 'Ciro 2024 (TRY-KDV siz)'
            
            if col in self.sales_data.columns:
                max_idx = self.sales_data[col].idxmax()
                best_store = self.sales_data.loc[max_idx]
                return f"🏆 En yüksek ciro: {best_store['Mağaza Adı']} - {best_store[col]:,.2f} TL".replace(',', '.')
        
        # Büyüme analizi
        elif 'büyüme' in query_lower or 'artış' in query_lower:
            growth_col = 'Ciro % Büyüme(24den25e)'
            if growth_col in self.sales_data.columns:
                avg_growth = self.sales_data[growth_col].mean()
                return f"📈 Ortalama büyüme: %{avg_growth:.2f}"
        
        # Genel analiz
        else:
            analysis = self.processor.analyze_excel_structure(self.sales_data, 'sales.xlsx')
            insights = self.processor.generate_smart_insights(analysis)
            
            result = "📊 Satış Verisi Analizi:\n"
            for insight in insights:
                result += f"• {insight}\n"
            
            return result
    
# Test fonksiyonu
def test_quick_analyzer():
    analyzer = QuickSalesAnalyzer()
    
    test_queries = [
        "Ortalama ciro 2024 nedir?",
        "En yüksek ciro yapan mağaza hangisi?",
        "Büyüme oranı nedir?",
        "Genel analiz yap"
    ]
    
    for query in test_queries:
        print(f"\n❓ Soru: {query}")
        print(f"💡 Yanıt: {analyzer.analyze_query(query)}")

if __name__ == "__main__":
    test_quick_analyzer()
