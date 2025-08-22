
# app.py API Geliştirmeleri - MANUEL ENTEGRASYON

# Yeni endpoint'ler ekle:

@app.route('/api/advanced-analytics', methods=['POST'])
@login_required
def advanced_analytics():
    """Gelişmiş analitik endpoint - YENİ"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        file_type = data.get('file_type', 'auto')  # sales, hr, auto
        
        if not query:
            return jsonify({"error": "Sorgu boş olamaz"}), 400
        
        # Analytics engine kullan
        if hasattr(ai_assistant, 'analytics_engine') and ai_assistant.analytics_engine:
            result = ai_assistant._handle_advanced_analytics(query, {})
            return jsonify(result)
        else:
            return jsonify({"error": "Gelişmiş analitik sistemi aktif değil"}), 503
            
    except Exception as e:
        logging.error(f"Advanced analytics hatası: {e}")
        return jsonify({"error": "Analiz sırasında hata oluştu"}), 500

@app.route('/api/data-insights/<filename>')
@login_required  
def get_data_insights(filename):
    """Dosya insights'ları getir - YENİ"""
    try:
        # Veri insights'ları döndür
        if filename in ai_assistant.data_insights:
            insights = ai_assistant.data_insights[filename]
            return jsonify({
                "filename": filename,
                "insights": insights.get('smart_insights', []),
                "suggestions": insights.get('query_suggestions', []),
                "analysis_summary": insights.get('basic_analysis', {})
            })
        else:
            return jsonify({"error": "Dosya bulunamadı"}), 404
            
    except Exception as e:
        logging.error(f"Data insights hatası: {e}")
        return jsonify({"error": "Insights alınamadı"}), 500

@app.route('/api/system-status')
@login_required
def system_status():
    """Sistem durumu - YENİ"""
    try:
        status = {
            "core_system": True,
            "enhanced_processor": hasattr(ai_assistant, 'new_processor') and ai_assistant.new_processor is not None,
            "analytics_engine": hasattr(ai_assistant, 'analytics_engine') and ai_assistant.analytics_engine is not None,
            "smart_intent": hasattr(ai_assistant, 'smart_intent') and ai_assistant.smart_intent is not None,
            "data_files": list(ai_assistant.structured_data.keys()),
            "last_updated": datetime.now().isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        logging.error(f"System status hatası: {e}")
        return jsonify({"error": "Sistem durumu alınamadı"}), 500
