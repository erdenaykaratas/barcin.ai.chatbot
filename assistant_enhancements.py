
# assistant.py Geliştirmeleri - MANUEL ENTEGRASYON

# 1. Import'lar (dosya başına ekle):
try:
    from new_data_processor import NewDataProcessor
    from advanced_analytics_engine import AdvancedAnalyticsEngine
    from smart_intent_engine import SmartIntentEngine
    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False
    logging.warning("Gelişmiş özellikler bulunamadı")

# 2. AIAssistant sınıfına ekle (__init__ metodunda):
        # Gelişmiş özellikler - YENİ EKLENEN
        if ADVANCED_FEATURES:
            self.new_processor = NewDataProcessor()
            self.analytics_engine = AdvancedAnalyticsEngine()
            self.smart_intent = SmartIntentEngine()
            logging.info("Tüm gelişmiş özellikler aktif")
        else:
            self.new_processor = None
            self.analytics_engine = None
            self.smart_intent = None

# 3. Yeni metodlar ekle (AIAssistant sınıfına):
    def _handle_advanced_analytics(self, query: str, entities: Dict) -> Dict:
        """Gelişmiş analitik sorgular - YENİ METOD"""
        
        if not self.analytics_engine:
            return {"text": "Gelişmiş analitik özellikler şu anda kullanılamıyor.", "chart": None}
        
        # Dosya seç
        target_file = None
        target_df = None
        
        # Sales verisi mi?
        if any(word in query.lower() for word in ['ciro', 'satış', 'mağaza', 'büyüme']):
            for filename, df in self.structured_data.items():
                if 'sales' in filename.lower():
                    target_file = filename
                    target_df = df
                    break
        
        # HR verisi mi?
        elif any(word in query.lower() for word in ['maaş', 'çalışan', 'departman']):
            for filename, df in self.structured_data.items():
                if 'calisanlar' in filename.lower() or 'hr' in filename.lower():
                    target_file = filename
                    target_df = df
                    break
        
        if target_df is None:
            return {"text": "İlgili veri dosyası bulunamadı.", "chart": None}
        
        # Gelişmiş analiz yap
        analysis = self.analytics_engine.comprehensive_analysis(target_df, target_file)
        
        # Sorgu tipine göre yanıt oluştur
        query_lower = query.lower()
        
        if 'anomali' in query_lower or 'aykırı' in query_lower:
            return self._format_anomaly_response(analysis)
        elif 'trend' in query_lower or 'tahmin' in query_lower:
            return self._format_trend_response(analysis)
        elif 'segmentasyon' in query_lower or 'segment' in query_lower:
            return self._format_segmentation_response(analysis)
        elif 'öneri' in query_lower or 'aksiyon' in query_lower:
            return self._format_recommendations_response(analysis)
        else:
            return self._format_comprehensive_response(analysis)
    
    def _format_comprehensive_response(self, analysis: Dict) -> Dict:
        """Kapsamlı analiz yanıtı formatla - YENİ METOD"""
        
        response = f"""
**🔍 Kapsamlı Veri Analizi Raporu**

**📊 Temel Metrikler:**
- Veri Kalitesi: %{analysis['basic_stats']['data_quality_score']:.1f}
- Toplam Kayıt: {analysis['basic_stats']['total_rows']}
- Sayısal Sütun: {len(analysis['basic_stats']['numeric_columns'])}

**💡 Kritik İçgörüler:**
"""
        
        # İş içgörüleri
        critical_insights = [i for i in analysis['business_insights'] if i.get('severity') == 'critical']
        warning_insights = [i for i in analysis['business_insights'] if i.get('severity') == 'warning']
        
        if critical_insights:
            response += f"\n🔴 **Kritik Durumlar:**\n"
            for insight in critical_insights[:3]:
                response += f"- {insight['title']}: {insight['value']}\n"
                response += f"  {insight['description']}\n"
        
        if warning_insights:
            response += f"\n🟡 **Dikkat Gereken Alanlar:**\n"
            for insight in warning_insights[:2]:
                response += f"- {insight['title']}: {insight['value']}\n"
        
        # Anomaliler
        if analysis['anomaly_detection']:
            response += f"\n🔍 **Tespit Edilen Anomaliler:**\n"
            for anomaly in analysis['anomaly_detection'][:3]:
                response += f"- {anomaly['column']}: {anomaly['count']} aykırı değer\n"
        
        # Tahminler
        if analysis['forecasting']['forecasts']:
            response += f"\n🔮 **Gelecek Projeksiyonları:**\n"
            for forecast in analysis['forecasting']['forecasts']:
                change = forecast['forecast_value'] - forecast['current_value']
                response += f"- {forecast['metric']}: {change:+,.0f} ({forecast['growth_rate']:+.1f}%)\n".replace(',', '.')
        
        # Öneriler
        if analysis['recommendations']:
            response += f"\n🎯 **Aksiyon Önerileri:**\n"
            for rec in analysis['recommendations'][:3]:
                response += f"- {rec['title']}: {rec['description']}\n"
        
        return {"text": response, "chart": None}
    
    def _needs_advanced_analytics(self, query: str) -> bool:
        """Gelişmiş analitik gerekli mi? - YENİ METOD"""
        
        advanced_keywords = [
            'anomali', 'aykırı', 'trend', 'tahmin', 'segmentasyon', 'segment',
            'korelasyon', 'analiz', 'rapor', 'öneri', 'aksiyon', 'insight',
            'kapsamlı', 'detaylı', 'gelişmiş'
        ]
        
        return any(keyword in query.lower() for keyword in advanced_keywords)

# 4. process_query metodunu güncelle (başına ekle):
        # Gelişmiş analitik kontrolü - YENİ EKLENEN
        if self.analytics_engine and self._needs_advanced_analytics(query):
            return self._handle_advanced_analytics(query, entities)
        
        # Smart intent kullanımı - YENİ EKLENEN
        if self.smart_intent:
            intent_result = self.smart_intent.analyze_intent(query)
            if intent_result.confidence > 0.7:
                # Yüksek confidence ile smart processing
                logging.info(f"Smart intent: {intent_result.name} (confidence: {intent_result.confidence:.2f})")
                # Burada smart intent sonuçlarını kullanabilirsiniz
