# assistant.py - GÜNCELLENMIŞ VERSİYON
"""
AI Assistant'Ä±n tÃ¼m mantÄ±ÄŸÄ±nÄ± iÃ§eren ana sÄ±nÄ±f.
Veri yÃ¼kleme, iÅŸleme, sorgu anlama ve cevap Ã¼retme iÅŸlemlerini yÃ¶netir.
GÃœNCELLEME: Mathematics Engine entegrasyonu eklendi.
YENİ: Advanced Analytics ve Smart Intent entegrasyonu
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
from mathematics_engine import MathematicsEngine

# Gelişmiş özellikler import - YENİ EKLENEN
try:
    from new_data_processor import NewDataProcessor
    from advanced_analytics_engine import AdvancedAnalyticsEngine
    from smart_intent_engine import SmartIntentEngine
    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False
    logging.warning("Gelişmiş özellikler bulunamadı")

class AIAssistant:
    def __init__(self):
        logging.info(f"AI Assistant beyni baÅŸlatÄ±lÄ±yor...")
        self.data_loader = UniversalDataLoader()
        self.knowledge_proc = KnowledgeProcessor()
        self.nlp_proc = SmartNLPProcessor()
        self.math_engine = MathematicsEngine()
        
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
        
        self.knowledge_base: Dict[str, any] = {}
        self.structured_data: Dict[str, pd.DataFrame] = {}
        self.data_insights: Dict[str, Dict] = {}
        self._initialize_system()

    def _initialize_system(self):
        """Sistemi baÅŸlatÄ±r, tÃ¼m verileri yÃ¼kler ve iÅŸler."""
        logging.info(f"'{DATA_DIRECTORY}' klasÃ¶rÃ¼nden veriler yÃ¼kleniyor...")
        self.knowledge_base, self.structured_data, self.data_insights = self.data_loader.load_all_data(DATA_DIRECTORY)
        
        if not self.knowledge_base:
            logging.warning("HiÃ§bir veri yÃ¼klenemedi. Asistan sÄ±nÄ±rlÄ± modda Ã§alÄ±ÅŸacak.")
            return

        logging.info(f"Toplam {len(self.knowledge_base)} dosya yÃ¼klendi. AI hafÄ±zasÄ± oluÅŸturuluyor...")
        self.knowledge_proc.process_knowledge_base(self.knowledge_base)

        all_store_names = set()
        all_employee_names = set()
        for df in self.structured_data.values():
            store_col = next((c for c in df.columns if any(k in c.lower() for k in ['maÄŸaza', 'store', 'ÅŸube'])), None)
            emp_col = next((c for c in df.columns if any(k in c.lower() for k in ['ad soyad', 'Ã§alÄ±ÅŸan'])), None)
            if store_col: all_store_names.update(df[store_col].dropna().unique())
            if emp_col: all_employee_names.update(df[emp_col].dropna().unique())

        self.nlp_proc.add_store_names(list(all_store_names))
        self.nlp_proc.add_employee_names(list(all_employee_names))
        logging.info("AI Assistant baÅŸlatma iÅŸlemi tamamlandÄ± ve hazÄ±r.")

    def get_status(self):
        """Sistem durumu - YENİ EKLENEN"""
        return { 
            'total_files': len(self.knowledge_base), 
            'ai_memory_ready': self.knowledge_proc.is_ready(),
            'math_engine_ready': True,
            'enhanced_processor': self.new_processor is not None,
            'analytics_engine': self.analytics_engine is not None,
            'smart_intent': self.smart_intent is not None,
            'advanced_features_active': ADVANCED_FEATURES
        }

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
    
    def _format_anomaly_response(self, analysis: Dict) -> Dict:
        """Anomali analiz yanıtı - YENİ METOD"""
        
        anomalies = analysis['anomaly_detection']
        
        if not anomalies:
            return {"text": "🟢 Verilerde önemli anomali tespit edilmedi.", "chart": None}
        
        response = "🔍 **Anomali Tespiti Raporu**\n\n"
        
        for anomaly in anomalies:
            severity_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(anomaly['severity'], '⚪')
            response += f"{severity_emoji} **{anomaly['column']}**\n"
            response += f"- Aykırı değer sayısı: {anomaly['count']}\n"
            response += f"- Toplam verinin %{anomaly['percentage']:.1f}'si\n"
            response += f"- Örnek değerler: {anomaly['values'][:3]}\n\n"
        
        return {"text": response, "chart": None}
    
    def _format_trend_response(self, analysis: Dict) -> Dict:
        """Trend analiz yanıtı - YENİ METOD"""
        
        trends = analysis['trend_analysis']['trends']
        forecasts = analysis['forecasting']['forecasts']
        
        response = "📈 **Trend ve Tahmin Analizi**\n\n"
        
        if trends:
            for trend in trends:
                direction_emoji = {'upward': '📈', 'downward': '📉', 'stable': '➡️'}.get(trend['direction'], '📊')
                response += f"{direction_emoji} **{trend['metric']}**\n"
                response += f"- Yön: {trend['direction']}\n"
                response += f"- Değişim: {trend['change_amount']:+,.0f}\n"
                response += f"- Yüzde: {trend['change_percentage']:+.1f}%\n\n".replace(',', '.')
        
        if forecasts:
            response += "🔮 **Gelecek Tahminleri:**\n"
            for forecast in forecasts:
                response += f"- Mevcut: {forecast['current_value']:,.0f}\n".replace(',', '.')
                response += f"- Tahmin: {forecast['forecast_value']:,.0f}\n".replace(',', '.')
                response += f"- Büyüme: %{forecast['growth_rate']:+.1f}\n"
        
        return {"text": response, "chart": None}
    
    def _format_recommendations_response(self, analysis: Dict) -> Dict:
        """Öneri yanıtı - YENİ METOD"""
        
        recommendations = analysis['recommendations']
        
        if not recommendations:
            return {"text": "✅ Şu anda özel aksiyon gerektirecek durum tespit edilmedi.", "chart": None}
        
        response = "🎯 **Aksiyon Önerileri Raporu**\n\n"
        
        for rec in recommendations:
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(rec['priority'], '⚪')
            response += f"{priority_emoji} **{rec['title']}** (Öncelik: {rec['priority']})\n"
            response += f"{rec['description']}\n\n"
            response += "**Aksiyon Adımları:**\n"
            for i, action in enumerate(rec['action_items'], 1):
                response += f"{i}. {action}\n"
            response += "\n"
        
        return {"text": response, "chart": None}
    
    def _format_segmentation_response(self, analysis: Dict) -> Dict:
        """Segmentasyon yanıtı - YENİ METOD"""
        
        segmentation = analysis['segmentation']
        
        if not segmentation['segments']:
            return {"text": "📊 Anlamlı segment oluşturmak için yeterli veri yok.", "chart": None}
        
        response = f"🎯 **Segmentasyon Analizi** ({segmentation['method']})\n\n"
        
        for segment in segmentation['segments']:
            response += f"**Segment {segment['segment_id'] + 1}** ({segment['size']} kayıt, %{segment['percentage']:.1f})\n"
            
            # Segment özelliklerini göster
            for metric, values in segment['characteristics'].items():
                response += f"- {metric}: Ort. {values['mean']:.0f}\n"
            response += "\n"
        
        return {"text": response, "chart": None}
    
    def _needs_advanced_analytics(self, query: str) -> bool:
        """Gelişmiş analitik gerekli mi? - YENİ METOD"""
        
        advanced_keywords = [
            'anomali', 'aykırı', 'trend', 'tahmin', 'segmentasyon', 'segment',
            'korelasyon', 'analiz', 'rapor', 'öneri', 'aksiyon', 'insight',
            'kapsamlı', 'detaylı', 'gelişmiş'
        ]
        
        return any(keyword in query.lower() for keyword in advanced_keywords)

    def process_query(self, query: str, user: User) -> Dict:
        try:
            logging.info(f"KullanÄ±cÄ± '{user.id}' (Rol: {user.role}) sorgu yapÄ±yor: '{query}'")
            
            # Gelişmiş analitik kontrolü - YENİ EKLENEN
            if self.analytics_engine and self._needs_advanced_analytics(query):
                return self._handle_advanced_analytics(query, {})
            
            # Smart intent kullanımı - YENİ EKLENEN
            if self.smart_intent:
                intent_result = self.smart_intent.analyze_intent(query)
                if intent_result.confidence > 0.7:
                    # Yüksek confidence ile smart processing
                    logging.info(f"Smart intent: {intent_result.name} (confidence: {intent_result.confidence:.2f})")
            
            # YENÄ° EKLENEN: Matematik sorgularÄ±nÄ± Ã¶nce kontrol et - GÃœVENLÄ°
            try:
                if self._is_math_query(query):
                    logging.info("Matematik sorgusu tespit edildi, Mathematics Engine'e yÃ¶nlendiriliyor.")
                    math_result = self.math_engine.process_math_query(query, self.structured_data)
                    
                    # SonuÃ§ kontrolÃ¼
                    if not isinstance(math_result, dict):
                        math_result = {"text": "Matematik hesaplama hatasÄ± oluÅŸtu.", "chart": None}
                    if 'text' not in math_result:
                        math_result['text'] = "Hesaplama tamamlanamadÄ±."
                    if 'chart' not in math_result:
                        math_result['chart'] = None
                        
                    return math_result
                    
            except Exception as math_error:
                logging.error(f"Mathematics Engine hatasÄ±: {math_error}")
                # Matematik hatasÄ± durumunda normal flow'a devam et
            
            # Mevcut intent analizi
            entities = self.nlp_proc.predict_intent(query, self.data_insights)
            intent = entities.get('intent', 'unknown')
            logging.info(f"Tespit edilen niyet: {intent}, VarlÄ±klar: {entities.get('entities')}")

            if intent in ['individual_salary', 'salary_analysis'] and user.role != 'admin':
                return {"text": "MaaÅŸ bilgilerine eriÅŸim yetkiniz bulunmamaktadÄ±r.", "chart": None}

            tool_to_use = self._select_tool(intent)
            if tool_to_use:
                return tool_to_use(query, entities)
            
            return self._tool_summarize_context(query, entities)
            
        except Exception as e:
            logging.error(f"Process query genel hatasÄ±: {e}", exc_info=True)
            return {"text": "Sorgu iÅŸlenirken bir hata oluÅŸtu. LÃ¼tfen daha basit bir soru deneyin.", "chart": None}

    # Mevcut metodların devamı...
    def _is_math_query(self, query: str) -> bool:
        """Matematik sorgusu kontrolü"""
        # Mevcut kod...
        return False  # Basitleştirme için
    
    def _select_tool(self, intent: str) -> Optional[callable]:
        """Tool seçici"""  
        # Mevcut kod...
        return None
    
    def _tool_summarize_context(self, query: str, entities: Dict) -> Dict:
        """Bağlam özetleyici"""
        # Mevcut kod...
        return {"text": "Genel yanıt", "chart": None}