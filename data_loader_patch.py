
# Enhanced Data Processor import - YENİ EKLENEN
try:
    from new_data_processor import NewDataProcessor
    from advanced_analytics_engine import AdvancedAnalyticsEngine
    ENHANCED_PROCESSING = True
except ImportError:
    ENHANCED_PROCESSING = False
    logging.warning("Gelişmiş data processor bulunamadı")

class UniversalDataLoader:
    def __init__(self):
        # ... mevcut kod ...
        
        # YENİ EKLENEN - Gelişmiş işlemciler
        if ENHANCED_PROCESSING:
            self.new_processor = NewDataProcessor()
            self.analytics_engine = AdvancedAnalyticsEngine()
            logging.info("Gelişmiş veri işleme sistemi aktif")
        else:
            self.new_processor = None
            self.analytics_engine = None
    
    def load_all_data(self, data_directory: str):
        # ... mevcut kod ...
        
        # YENİ EKLENEN - Gelişmiş analiz
        if self.new_processor and self.analytics_engine:
            for filename, content in knowledge_base.items():
                if isinstance(content, pd.DataFrame):
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
        
        return knowledge_base, structured_data, data_insights
