# app.py
"""
Flask web uygulamasını çalıştıran ana dosya.
Route'ları, kullanıcı oturumlarını ve API isteklerini yönetir.
"""
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from auth import User, load_user, verify_user
from config import APP_NAME, FLASK_SECRET_KEY, LOG_LEVEL
from assistant import AIAssistant

# --- Loglama Kurulumu ---
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Flask Uygulaması ve Eklentilerin Kurulumu ---
app = Flask(__name__)
if not FLASK_SECRET_KEY:
    raise ValueError("FLASK_SECRET_KEY yapılandırma dosyasında ayarlanmamış!")
app.secret_key = FLASK_SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Bu sayfayı görüntülemek için lütfen giriş yapın."
login_manager.login_message_category = "info"

@login_manager.user_loader
def user_loader(user_id: str) -> User:
    """Flask-Login için kullanıcıyı session'dan yükler."""
    return load_user(user_id)

# --- AI Assistant'ı Başlatma ---
# Uygulama başlatıldığında sadece bir tane AI Assistant nesnesi oluşturulur.
ai_assistant = AIAssistant()

# --- Route Tanımları ---
@app.route('/')
@login_required
def index():
    """Ana sohbet sayfasını render eder."""
    return render_template('index.html', app_name=APP_NAME, user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Kullanıcı giriş sayfasını yönetir."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = verify_user(username, password)
        if user:
            login_user(user, remember=True)
            logging.info(f"Kullanıcı '{username}' başarıyla giriş yaptı.")
            return redirect(url_for('index'))
        else:
            logging.warning(f"Başarısız giriş denemesi: Kullanıcı '{username}'")
            return render_template('login.html', app_name=APP_NAME, error="Geçersiz kullanıcı adı veya şifre.")
            
    return render_template('login.html', app_name=APP_NAME)

@app.route('/logout')
@login_required
def logout():
    """Kullanıcı çıkış işlemini yapar."""
    logging.info(f"Kullanıcı '{current_user.id}' çıkış yaptı.")
    logout_user()
    return redirect(url_for('login'))

# --- API Endpoints ---
# app.py - handle_query fonksiyonunu güncelleyin

@app.route('/api/query', methods=['POST'])
@login_required
def handle_query():
    """Kullanıcı sorgularını alır ve AI'ya işlettirir - GELİŞTİRİLDİ"""
    try:
        if not request.is_json:
            return jsonify({"error": "Geçersiz istek: JSON bekleniyordu."}), 400
            
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({"error": "Sorgu boş olamaz."}), 400
        
        # Query uzunluğu kontrolü
        if len(user_query) > 1000:
            return jsonify({"error": "Sorgu çok uzun. Lütfen daha kısa bir soru sorun."}), 400
        
        logging.info(f"Kullanıcı '{current_user.id}' sorgu gönderdi: '{user_query[:100]}{'...' if len(user_query) > 100 else ''}'")
        
        try:
            result = ai_assistant.process_query(user_query, current_user)
            
            # Sonuç kontrolü
            if not isinstance(result, dict):
                logging.error(f"AI assistant beklenmedik sonuç döndürdü: {type(result)}")
                return jsonify({"error": "AI sisteminden geçersiz yanıt alındı."}), 500
            
            if 'text' not in result:
                logging.error(f"AI assistant sonucunda 'text' anahtarı bulunamadı: {result}")
                result['text'] = "Yanıt oluşturulamadı."
            
            if 'chart' not in result:
                result['chart'] = None
                
            logging.info(f"Sorgu başarıyla işlendi. Yanıt uzunluğu: {len(result.get('text', ''))}")
            return jsonify(result)
            
        except MemoryError:
            logging.error("Bellek yetersizliği hatası")
            return jsonify({"error": "Sorgu çok büyük veri gerektirir. Lütfen daha spesifik bir soru sorun."}), 500
            
        except TimeoutError:
            logging.error("Zaman aşımı hatası")
            return jsonify({"error": "Sorgu çok uzun sürdü. Lütfen daha basit bir soru deneyin."}), 500
            
        except ValueError as ve:
            logging.error(f"Değer hatası: {ve}")
            return jsonify({"error": f"Geçersiz veri: {str(ve)}"}), 400
            
        except KeyError as ke:
            logging.error(f"Anahtar hatası: {ke}")
            return jsonify({"error": "Gerekli veri bulunamadı. Veri formatınızı kontrol edin."}), 400
            
        except Exception as processing_error:
            logging.error(f"Sorgu işleme hatası: {processing_error}", exc_info=True)
            
            # Hata tipine göre özel mesajlar
            error_message = "Beklenmedik bir hata oluştu."
            
            if "numpy" in str(processing_error).lower():
                error_message = "Sayısal hesaplama hatası. Veri formatınızı kontrol edin."
            elif "pandas" in str(processing_error).lower():
                error_message = "Veri işleme hatası. Excel/CSV dosyalarınızı kontrol edin."
            elif "sympy" in str(processing_error).lower():
                error_message = "Matematik hesaplama hatası. Sorgunuzu daha basit hale getirin."
            elif "empty" in str(processing_error).lower():
                error_message = "İlgili veri bulunamadı. Farklı bir soru deneyin."
            elif "connection" in str(processing_error).lower():
                error_message = "Dış API bağlantı hatası. Lütfen tekrar deneyin."
            
            return jsonify({"error": error_message}), 500
            
    except Exception as outer_error:
        logging.critical(f"API endpoint kritik hatası: {outer_error}", exc_info=True)
        return jsonify({"error": "Sunucu hatası. Lütfen yöneticiye bildirin."}), 500

@app.route('/api/status')
@login_required
def get_status():
    """AI sisteminin durumunu döndürür."""
    return jsonify(ai_assistant.get_status())

if __name__ == '__main__':
    logging.info(f"'{APP_NAME}' başlatılıyor... Sunucu http://127.0.0.1:5000 adresinde çalışacak.")
    app.run(host='0.0.0.0', port=5000, debug=(LOG_LEVEL == 'DEBUG'))