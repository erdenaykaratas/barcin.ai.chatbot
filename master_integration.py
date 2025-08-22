# master_integration.py
"""
Tüm gelişmiş özellikleri ana sisteme entegre eden master script
"""

import os
import shutil
from datetime import datetime

def backup_current_system():
    """Mevcut sistemi yedekle"""
    
    print("🔄 Sistem Yedekleme...")
    
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Ana dosyaları yedekle
    critical_files = [
        'assistant.py',
        'app.py', 
        'data_loader.py',
        'nlp_processor.py'
    ]
    
    for file in critical_files:
        if os.path.exists(file):
            shutil.copy2(file, backup_dir)
            print(f"   ✅ {file} yedeklendi")
    
    print(f"📁 Yedek klasörü: {backup_dir}")
    return backup_dir

def integrate_new_data_processor():
    """Yeni data processor'ı entegre et"""
    
    print("\n📊 New Data Processor Entegrasyonu...")
    
    # data_loader.py'yi güncelle
    data_loader_patch = '''
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
'''
    
    with open('data_loader_patch.py', 'w', encoding='utf-8') as f:
        f.write(data_loader_patch)
    
    print("   ✅ data_loader_patch.py oluşturuldu")

def integrate_assistant_enhancements():
    """Assistant'a gelişmiş özellikler ekle"""
    
    print("\n🤖 Assistant Geliştirmeleri...")
    
    assistant_enhancements = '''
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
            response += f"\\n🔴 **Kritik Durumlar:**\\n"
            for insight in critical_insights[:3]:
                response += f"- {insight['title']}: {insight['value']}\\n"
                response += f"  {insight['description']}\\n"
        
        if warning_insights:
            response += f"\\n🟡 **Dikkat Gereken Alanlar:**\\n"
            for insight in warning_insights[:2]:
                response += f"- {insight['title']}: {insight['value']}\\n"
        
        # Anomaliler
        if analysis['anomaly_detection']:
            response += f"\\n🔍 **Tespit Edilen Anomaliler:**\\n"
            for anomaly in analysis['anomaly_detection'][:3]:
                response += f"- {anomaly['column']}: {anomaly['count']} aykırı değer\\n"
        
        # Tahminler
        if analysis['forecasting']['forecasts']:
            response += f"\\n🔮 **Gelecek Projeksiyonları:**\\n"
            for forecast in analysis['forecasting']['forecasts']:
                change = forecast['forecast_value'] - forecast['current_value']
                response += f"- {forecast['metric']}: {change:+,.0f} ({forecast['growth_rate']:+.1f}%)\\n".replace(',', '.')
        
        # Öneriler
        if analysis['recommendations']:
            response += f"\\n🎯 **Aksiyon Önerileri:**\\n"
            for rec in analysis['recommendations'][:3]:
                response += f"- {rec['title']}: {rec['description']}\\n"
        
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
'''
    
    with open('assistant_enhancements.py', 'w', encoding='utf-8') as f:
        f.write(assistant_enhancements)
    
    print("   ✅ assistant_enhancements.py oluşturuldu")

def create_web_api_enhancements():
    """Web API geliştirmeleri"""
    
    print("\n🌐 Web API Geliştirmeleri...")
    
    api_enhancements = '''
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
'''
    
    with open('api_enhancements.py', 'w', encoding='utf-8') as f:
        f.write(api_enhancements)
    
    print("   ✅ api_enhancements.py oluşturuldu")

def create_frontend_enhancements():
    """Frontend geliştirmeleri"""
    
    print("\n💻 Frontend Geliştirmeleri...")
    
    frontend_js = '''
// Frontend Geliştirmeleri - index.html'e eklenecek JavaScript

// Gelişmiş analitik butonları ekle
function addAdvancedButtons() {
    const inputArea = document.querySelector('.input-area');
    
    const advancedPanel = document.createElement('div');
    advancedPanel.className = 'advanced-panel';
    advancedPanel.innerHTML = `
        <div class="advanced-buttons">
            <button onclick="requestAdvancedAnalysis()" class="advanced-btn analytics">
                📊 Gelişmiş Analiz
            </button>
            <button onclick="requestInsights()" class="advanced-btn insights">
                💡 Akıllı İçgörüler
            </button>
            <button onclick="requestForecast()" class="advanced-btn forecast">
                🔮 Tahmin
            </button>
            <button onclick="requestRecommendations()" class="advanced-btn recommendations">
                🎯 Öneriler
            </button>
        </div>
    `;
    
    inputArea.parentNode.insertBefore(advancedPanel, inputArea);
}

// Gelişmiş analiz istekleri
async function requestAdvancedAnalysis() {
    const query = "Kapsamlı veri analizi yap";
    await sendAdvancedQuery(query, 'comprehensive');
}

async function requestInsights() {
    const query = "Anomali tespiti ve kritik içgörüler";
    await sendAdvancedQuery(query, 'insights');
}

async function requestForecast() {
    const query = "Trend analizi ve gelecek tahminleri";
    await sendAdvancedQuery(query, 'forecast');
}

async function requestRecommendations() {
    const query = "Aksiyon önerileri ve iyileştirme planı";
    await sendAdvancedQuery(query, 'recommendations');
}

async function sendAdvancedQuery(query, type) {
    try {
        addMessage(query, 'user');
        
        const thinkingDiv = document.createElement('div');
        thinkingDiv.classList.add('message', 'ai', 'thinking');
        thinkingDiv.textContent = 'Gelişmiş analiz yapılıyor...';
        document.getElementById('chat-container').appendChild(thinkingDiv);
        
        const response = await fetch('/api/advanced-analytics', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: query, analysis_type: type})
        });
        
        thinkingDiv.remove();
        
        if (response.ok) {
            const result = await response.json();
            addMessage(result.text, 'ai', result.chart);
        } else {
            addMessage('Gelişmiş analiz sırasında bir hata oluştu.', 'ai');
        }
        
    } catch (error) {
        console.error('Advanced analytics error:', error);
        addMessage('Bağlantı hatası oluştu.', 'ai');
    }
}

// Sistem durumu kontrolü
async function checkSystemStatus() {
    try {
        const response = await fetch('/api/system-status');
        if (response.ok) {
            const status = await response.json();
            updateSystemStatusIndicator(status);
        }
    } catch (error) {
        console.error('System status error:', error);
    }
}

function updateSystemStatusIndicator(status) {
    const header = document.querySelector('.header');
    const statusIndicator = document.createElement('div');
    statusIndicator.className = 'system-status';
    
    const activeFeatures = Object.keys(status).filter(key => 
        status[key] === true && key !== 'last_updated'
    ).length;
    
    statusIndicator.innerHTML = `
        <span class="status-badge ${activeFeatures >= 3 ? 'advanced' : 'basic'}">
            ${activeFeatures >= 3 ? '🚀 Gelişmiş' : '📊 Temel'} Mod
        </span>
    `;
    
    header.appendChild(statusIndicator);
}

// CSS Stilleri
const advancedStyles = `
.advanced-panel {
    padding: 1rem 2rem;
    background: rgba(26, 27, 35, 0.6);
    border-bottom: 1px solid var(--border);
}

.advanced-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}

.advanced-btn {
    padding: 0.5rem 1rem;
    border: 1px solid var(--primary);
    background: rgba(0, 212, 255, 0.1);
    color: var(--primary);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 0.9rem;
}

.advanced-btn:hover {
    background: rgba(0, 212, 255, 0.2);
    transform: translateY(-1px);
}

.system-status {
    display: flex;
    align-items: center;
}

.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
}

.status-badge.advanced {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
    border: 1px solid rgba(34, 197, 94, 0.3);
}

.status-badge.basic {
    background: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.3);
}
`;

// Stilleri sayfaya ekle
const styleSheet = document.createElement('style');
styleSheet.textContent = advancedStyles;
document.head.appendChild(styleSheet);

// Sayfa yüklendiğinde çalıştır
document.addEventListener('DOMContentLoaded', function() {
    addAdvancedButtons();
    checkSystemStatus();
});
'''
    
    with open('frontend_enhancements.js', 'w', encoding='utf-8') as f:
        f.write(frontend_js)
    
    print("   ✅ frontend_enhancements.js oluşturuldu")

def generate_integration_guide():
    """Entegrasyon rehberi oluştur"""
    
    print("\n📋 Entegrasyon Rehberi...")
    
    guide = '''
# 🚀 Tam Sistem Entegrasyonu Rehberi

## ✅ Entegrasyon Adımları

### 1. Yedek Kontrol
- [x] Sistem yedeklendi
- [ ] Yedek klasörü kontrol edildi

### 2. Data Loader Güncellemesi
```bash
# data_loader.py dosyasını yedekle
cp data_loader.py data_loader_backup.py

# data_loader_patch.py içeriğini data_loader.py'ye manuel ekle
```

### 3. Assistant Geliştirmeleri
```bash
# assistant.py dosyasını yedekle  
cp assistant.py assistant_backup.py

# assistant_enhancements.py içeriğini assistant.py'ye manuel ekle
```

### 4. API Geliştirmeleri
```bash
# app.py dosyasını yedekle
cp app.py app_backup.py

# api_enhancements.py içeriğini app.py'ye manuel ekle
```

### 5. Frontend Geliştirmeleri
```bash
# templates/index.html dosyasını yedekle
cp templates/index.html templates/index_backup.html

# frontend_enhancements.js içeriğini index.html'in script bölümüne ekle
```

## 🧪 Test Adımları

### 1. Sistem Başlatma
```bash
python app.py
```

### 2. Test Sorguları
- "Kapsamlı veri analizi yap"
- "Anomali tespiti ve kritik içgörüler"  
- "Trend analizi ve gelecek tahminleri"
- "Aksiyon önerileri ver"

### 3. API Test
```bash
curl -X GET http://localhost:5000/api/system-status
```

## 🔧 Sorun Giderme

### Hata: Import Error
```python
# requirements.txt'e ekle:
scikit-learn>=1.3.0
scipy>=1.11.0
```

### Hata: Module Not Found
```bash
# Eksik dosyaları kontrol et:
ls -la new_data_processor.py
ls -la advanced_analytics_engine.py
ls -la smart_intent_engine.py
```

## 📊 Beklenen Sonuçlar

Entegrasyon sonrası sistem şunları yapabilecek:

✅ **Temel Özellikler:**
- Excel/CSV dosya okuma
- Temel sorgu yanıtlama
- Matematik hesaplamaları

🚀 **Gelişmiş Özellikler:**
- Anomali tespiti
- Trend analizi ve tahmin
- Segmentasyon
- Akıllı içgörüler
- Aksiyon önerileri

💡 **AI Yetenekleri:**
- Smart intent recognition
- Context-aware responses
- Business intelligence
- Predictive analytics

## 🎯 Sonraki Adımlar

1. **Performans Optimizasyonu**
2. **Real-time Analytics** 
3. **Database Integration**
4. **Advanced Visualizations**
5. **Mobile Support**
'''
    
    with open('INTEGRATION_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("   ✅ INTEGRATION_GUIDE.md oluşturuldu")

def cleanup_old_files():
    """Eski dosyaları temizle"""
    
    print("\n🧹 Dosya Temizliği...")
    
    files_to_remove = [
        'enhanced_data_processor.py',  # JSON hatası vardı
        'file_analyzer.py',           # Analiz tamamlandı
        'integration_patch.py'        # Artık gerek yok
    ]
    
    removed_count = 0
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"   🗑️ {file} silindi")
                removed_count += 1
            except Exception as e:
                print(f"   ❌ {file} silinemedi: {e}")
    
    print(f"   ✅ {removed_count} dosya temizlendi")

def main():
    """Ana entegrasyon süreci"""
    
    print("🚀 MASTER INTEGRATION - Tam Sistem Entegrasyonu")
    print("=" * 60)
    
    try:
        # 1. Yedekleme
        backup_dir = backup_current_system()
        
        # 2. Entegrasyon dosyaları oluştur
        integrate_new_data_processor()
        integrate_assistant_enhancements() 
        create_web_api_enhancements()
        create_frontend_enhancements()
        
        # 3. Rehber oluştur
        generate_integration_guide()
        
        # 4. Temizlik
        cleanup_old_files()
        
        print(f"\n🎉 ENTEGRASYON TAMAMLANDI!")
        print("=" * 40)
        print(f"📁 Yedek: {backup_dir}")
        print(f"📋 Rehber: INTEGRATION_GUIDE.md")
        print(f"🔧 Durum: Manuel entegrasyon gerekli")
        
        print(f"\n📝 SONRAKİ ADIMLAR:")
        print(f"1. INTEGRATION_GUIDE.md dosyasını okuyun")
        print(f"2. Manuel entegrasyon adımlarını uygulayın")
        print(f"3. python app.py ile sistemi test edin")
        print(f"4. Gelişmiş analiz özelliklerini deneyin")
        
        print(f"\n💡 TEST SORGULARİ:")
        print(f'- "Kapsamlı veri analizi yap"')
        print(f'- "Anomali tespiti yap"') 
        print(f'- "Gelecek tahminleri ver"')
        print(f'- "Aksiyon önerileri sun"')
        
    except Exception as e:
        print(f"\n❌ Entegrasyon hatası: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()