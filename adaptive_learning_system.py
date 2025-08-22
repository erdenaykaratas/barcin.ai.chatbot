# adaptive_learning_system.py
"""
Adaptif Öğrenme Sistemi - AI'nın kullanıcı etkileşimlerinden öğrenmesini sağlar
"""

import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import pickle
import hashlib

@dataclass
class UserInteraction:
    """Kullanıcı etkileşim verisi"""
    user_id: str
    query: str
    intent: str
    confidence: float
    response_type: str
    user_feedback: Optional[str] = None
    response_time: float = 0.0
    timestamp: datetime = datetime.now()
    session_id: str = ""
    context: Dict = None

@dataclass
class LearningPattern:
    """Öğrenilen pattern"""
    pattern_id: str
    pattern_type: str
    pattern_data: Dict
    frequency: int
    success_rate: float
    last_updated: datetime
    confidence: float

class AdaptiveLearningSystem:
    """Adaptif öğrenme ve iyileştirme sistemi"""
    
    def __init__(self, db_path: str = "learning_data.db"):
        self.db_path = db_path
        self.interaction_history = []
        self.learned_patterns = {}
        self.user_preferences = defaultdict(dict)
        self.query_improvements = {}
        self.context_memory = {}
        
        # Veritabanını başlat
        self._init_database()
        
        # Performans metrikleri
        self.performance_metrics = {
            'total_queries': 0,
            'successful_responses': 0,
            'user_satisfaction': 0.0,
            'response_time_avg': 0.0,
            'common_intents': Counter(),
            'error_patterns': Counter()
        }
        
        # Öğrenme parametreleri
        self.learning_config = {
            'min_pattern_frequency': 3,
            'confidence_threshold': 0.7,
            'adaptation_rate': 0.1,
            'memory_window_days': 30,
            'feedback_weight': 2.0
        }
    
    def _init_database(self):
        """Öğrenme veritabanını başlatır"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Etkileşim tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    query TEXT,
                    intent TEXT,
                    confidence REAL,
                    response_type TEXT,
                    user_feedback TEXT,
                    response_time REAL,
                    timestamp DATETIME,
                    session_id TEXT,
                    context TEXT
                )
            ''')
            
            # Pattern tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learned_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    frequency INTEGER,
                    success_rate REAL,
                    last_updated DATETIME,
                    confidence REAL
                )
            ''')
            
            # Kullanıcı tercihleri
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT,
                    preference_type TEXT,
                    preference_data TEXT,
                    weight REAL,
                    updated_at DATETIME,
                    PRIMARY KEY (user_id, preference_type)
                )
            ''')
            
            conn.commit()
    
    def record_interaction(self, interaction: UserInteraction):
        """Kullanıcı etkileşimini kaydet"""
        
        # Hafızada tut
        self.interaction_history.append(interaction)
        
        # Veritabanına kaydet
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO interactions 
                (user_id, query, intent, confidence, response_type, user_feedback, 
                 response_time, timestamp, session_id, context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                interaction.user_id, interaction.query, interaction.intent,
                interaction.confidence, interaction.response_type, 
                interaction.user_feedback, interaction.response_time,
                interaction.timestamp, interaction.session_id,
                json.dumps(interaction.context) if interaction.context else None
            ))
            conn.commit()
        
        # Performans metriklerini güncelle
        self._update_performance_metrics(interaction)
        
        # Pattern öğrenmeyi tetikle
        self._trigger_pattern_learning(interaction)
    
    def _update_performance_metrics(self, interaction: UserInteraction):
        """Performans metriklerini günceller"""
        
        self.performance_metrics['total_queries'] += 1
        
        # Başarılı yanıt kontrolü
        if (interaction.confidence > 0.7 and 
            interaction.user_feedback in [None, 'positive', 'helpful']):
            self.performance_metrics['successful_responses'] += 1
        
        # Intent dağılımı
        self.performance_metrics['common_intents'][interaction.intent] += 1
        
        # Yanıt süresi ortalaması
        total_time = self.performance_metrics['response_time_avg'] * (self.performance_metrics['total_queries'] - 1)
        self.performance_metrics['response_time_avg'] = (total_time + interaction.response_time) / self.performance_metrics['total_queries']
        
        # Hata pattern'ları
        if interaction.confidence < 0.5 or interaction.user_feedback == 'negative':
            error_signature = f"{interaction.intent}:{interaction.response_type}"
            self.performance_metrics['error_patterns'][error_signature] += 1
    
    def _trigger_pattern_learning(self, interaction: UserInteraction):
        """Pattern öğrenmeyi tetikler"""
        
        # Query pattern'ı öğren
        self._learn_query_pattern(interaction)
        
        # Context pattern'ı öğren
        self._learn_context_pattern(interaction)
        
        # User preference'ı öğren
        self._learn_user_preference(interaction)
        
        # Intent improvement öğren
        self._learn_intent_improvement(interaction)
    
    def _learn_query_pattern(self, interaction: UserInteraction):
        """Sorgu pattern'larını öğrenir"""
        
        # Sorguyu normalize et
        normalized_query = self._normalize_query(interaction.query)
        
        # Pattern ID oluştur
        pattern_id = f"query_{hashlib.md5(normalized_query.encode()).hexdigest()[:8]}"
        
        # Mevcut pattern'ı güncelle veya yeni oluştur
        if pattern_id in self.learned_patterns:
            pattern = self.learned_patterns[pattern_id]
            pattern.frequency += 1
            
            # Başarı oranını güncelle
            success = 1 if interaction.confidence > 0.7 else 0
            pattern.success_rate = (pattern.success_rate * (pattern.frequency - 1) + success) / pattern.frequency
            pattern.last_updated = datetime.now()
            
        else:
            # Yeni pattern oluştur
            success_rate = 1.0 if interaction.confidence > 0.7 else 0.0
            pattern = LearningPattern(
                pattern_id=pattern_id,
                pattern_type="query_pattern",
                pattern_data={
                    'normalized_query': normalized_query,
                    'original_query': interaction.query,
                    'best_intent': interaction.intent,
                    'query_length': len(interaction.query),
                    'word_count': len(interaction.query.split())
                },
                frequency=1,
                success_rate=success_rate,
                last_updated=datetime.now(),
                confidence=interaction.confidence
            )
            self.learned_patterns[pattern_id] = pattern
        
        # Veritabanına kaydet
        self._save_pattern_to_db(pattern)
    
    def _learn_context_pattern(self, interaction: UserInteraction):
        """Context pattern'larını öğrenir"""
        
        if not interaction.context:
            return
        
        # Context signature oluştur
        context_keys = sorted(interaction.context.keys())
        context_signature = "_".join(context_keys)
        pattern_id = f"context_{hashlib.md5(context_signature.encode()).hexdigest()[:8]}"
        
        if pattern_id in self.learned_patterns:
            self.learned_patterns[pattern_id].frequency += 1
        else:
            pattern = LearningPattern(
                pattern_id=pattern_id,
                pattern_type="context_pattern",
                pattern_data={
                    'context_keys': context_keys,
                    'example_context': interaction.context,
                    'associated_intent': interaction.intent
                },
                frequency=1,
                success_rate=1.0 if interaction.confidence > 0.7 else 0.0,
                last_updated=datetime.now(),
                confidence=interaction.confidence
            )
            self.learned_patterns[pattern_id] = pattern
            self._save_pattern_to_db(pattern)
    
    def _learn_user_preference(self, interaction: UserInteraction):
        """Kullanıcı tercihlerini öğrenir"""
        
        user_id = interaction.user_id
        
        # Intent tercihi
        if interaction.confidence > 0.8:
            intent_prefs = self.user_preferences[user_id].get('intent_preferences', Counter())
            intent_prefs[interaction.intent] += 1
            self.user_preferences[user_id]['intent_preferences'] = intent_prefs
        
        # Response type tercihi
        if interaction.user_feedback == 'positive':
            response_prefs = self.user_preferences[user_id].get('response_preferences', Counter())
            response_prefs[interaction.response_type] += 1
            self.user_preferences[user_id]['response_preferences'] = response_prefs
        
        # Veritabanına kaydet
        self._save_user_preferences(user_id)
    
    def _learn_intent_improvement(self, interaction: UserInteraction):
        """Intent tanıma iyileştirmelerini öğrenir"""
        
        # Düşük confidence'lı sorguları kaydet
        if interaction.confidence < 0.6:
            improvement_key = f"low_confidence_{interaction.intent}"
            
            if improvement_key not in self.query_improvements:
                self.query_improvements[improvement_key] = {
                    'queries': [],
                    'average_confidence': 0.0,
                    'improvement_suggestions': []
                }
            
            self.query_improvements[improvement_key]['queries'].append({
                'query': interaction.query,
                'confidence': interaction.confidence,
                'timestamp': interaction.timestamp
            })
    
    def _normalize_query(self, query: str) -> str:
        """Sorguyu normalize eder"""
        import re
        
        # Küçük harfe çevir
        normalized = query.lower()
        
        # Noktalama işaretlerini kaldır
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        # Ekstra boşlukları temizle
        normalized = ' '.join(normalized.split())
        
        # Sayıları genelleştir
        normalized = re.sub(r'\d+', 'NUM', normalized)
        
        return normalized
    
    def _save_pattern_to_db(self, pattern: LearningPattern):
        """Pattern'ı veritabanına kaydeder"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO learned_patterns 
                (pattern_id, pattern_type, pattern_data, frequency, success_rate, last_updated, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern.pattern_id, pattern.pattern_type, json.dumps(pattern.pattern_data),
                pattern.frequency, pattern.success_rate, pattern.last_updated, pattern.confidence
            ))
            conn.commit()
    
    def _save_user_preferences(self, user_id: str):
        """Kullanıcı tercihlerini veritabanına kaydeder"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for pref_type, pref_data in self.user_preferences[user_id].items():
                cursor.execute('''
                    INSERT OR REPLACE INTO user_preferences 
                    (user_id, preference_type, preference_data, weight, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    user_id, pref_type, json.dumps(dict(pref_data) if isinstance(pref_data, Counter) else pref_data),
                    1.0, datetime.now()
                ))
            conn.commit()
    
    def get_intent_suggestions(self, query: str, user_id: str = None) -> Dict:
        """Query için intent önerileri döndürür"""
        
        normalized_query = self._normalize_query(query)
        suggestions = {
            'primary_intent': None,
            'confidence_boost': 0.0,
            'alternative_intents': [],
            'user_preference_bonus': 0.0
        }
        
        # Learned pattern'larda ara
        best_match = None
        best_similarity = 0.0
        
        for pattern in self.learned_patterns.values():
            if pattern.pattern_type == 'query_pattern':
                similarity = self._calculate_similarity(
                    normalized_query, 
                    pattern.pattern_data['normalized_query']
                )
                
                if similarity > best_similarity and similarity > 0.7:
                    best_similarity = similarity
                    best_match = pattern
        
        if best_match:
            suggestions['primary_intent'] = best_match.pattern_data['best_intent']
            suggestions['confidence_boost'] = best_match.success_rate * 0.2
        
        # Kullanıcı tercihlerini kontrol et
        if user_id and user_id in self.user_preferences:
            intent_prefs = self.user_preferences[user_id].get('intent_preferences', Counter())
            if intent_prefs:
                most_preferred = intent_prefs.most_common(1)[0]
                suggestions['user_preference_bonus'] = 0.1
                
                if not suggestions['primary_intent']:
                    suggestions['primary_intent'] = most_preferred[0]
        
        return suggestions
    
    def _calculate_similarity(self, query1: str, query2: str) -> float:
        """İki sorgu arasındaki benzerliği hesaplar"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, query1, query2).ratio()
    
    def get_performance_report(self) -> Dict:
        """Performans raporu oluşturur"""
        
        # Son 30 günün verilerini al
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_interactions = [
            i for i in self.interaction_history 
            if i.timestamp > cutoff_date
        ]
        
        report = {
            'summary': {
                'total_queries': len(recent_interactions),
                'success_rate': self.performance_metrics['successful_responses'] / max(self.performance_metrics['total_queries'], 1),
                'avg_response_time': self.performance_metrics['response_time_avg'],
                'learned_patterns': len(self.learned_patterns)
            },
            'top_intents': dict(self.performance_metrics['common_intents'].most_common(5)),
            'error_patterns': dict(self.performance_metrics['error_patterns'].most_common(3)),
            'learning_progress': self._calculate_learning_progress(),
            'recommendations': self._generate_improvement_recommendations()
        }
        
        return report
    
    def _calculate_learning_progress(self) -> Dict:
        """Öğrenme ilerlemesini hesaplar"""
        
        if not self.interaction_history:
            return {'trend': 'no_data', 'improvement': 0.0}
        
        # Son 10 gün vs önceki 10 gün karşılaştırması
        now = datetime.now()
        recent_period = now - timedelta(days=10)
        older_period = now - timedelta(days=20)
        
        recent_interactions = [i for i in self.interaction_history if i.timestamp > recent_period]
        older_interactions = [i for i in self.interaction_history 
                             if older_period < i.timestamp <= recent_period]
        
        if not older_interactions:
            return {'trend': 'insufficient_data', 'improvement': 0.0}
        
        recent_avg_confidence = np.mean([i.confidence for i in recent_interactions]) if recent_interactions else 0
        older_avg_confidence = np.mean([i.confidence for i in older_interactions])
        
        improvement = recent_avg_confidence - older_avg_confidence
        
        return {
            'trend': 'improving' if improvement > 0.05 else 'stable' if abs(improvement) <= 0.05 else 'declining',
            'improvement': improvement,
            'recent_confidence': recent_avg_confidence,
            'previous_confidence': older_avg_confidence
        }
    
    def _generate_improvement_recommendations(self) -> List[str]:
        """İyileştirme önerileri oluşturur"""
        recommendations = []
        
        # Hata pattern'larına göre öneriler
        for error_pattern, count in self.performance_metrics['error_patterns'].most_common(3):
            if count > 5:  # Sık tekrarlanan hatalar
                recommendations.append(f"'{error_pattern}' hatası {count} kez tekrarlandı - intent tanıma iyileştirmesi gerekli")
        
        # Düşük confidence pattern'ları
        low_confidence_patterns = [
            p for p in self.learned_patterns.values() 
            if p.success_rate < 0.6 and p.frequency > 3
        ]
        
        if low_confidence_patterns:
            recommendations.append(f"{len(low_confidence_patterns)} pattern düşük başarı oranına sahip - eğitim verisi güncellenmeli")
        
        # Kullanıcı feedback'i
        negative_feedback_count = len([
            i for i in self.interaction_history[-100:] 
            if i.user_feedback == 'negative'
        ])
        
        if negative_feedback_count > 10:
            recommendations.append(f"Son 100 etkileşimde {negative_feedback_count} negatif feedback - kullanıcı deneyimi iyileştirmesi gerekli")
        
        # Yanıt süresi
        if self.performance_metrics['response_time_avg'] > 5.0:
            recommendations.append(f"Ortalama yanıt süresi {self.performance_metrics['response_time_avg']:.1f}s - performans optimizasyonu gerekli")
        
        return recommendations
    
    def export_learning_data(self, filename: str):
        """Öğrenme verilerini export eder"""
        export_data = {
            'performance_metrics': self.performance_metrics,
            'learned_patterns': {k: asdict(v) for k, v in self.learned_patterns.items()},
            'user_preferences': dict(self.user_preferences),
            'query_improvements': self.query_improvements,
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        logging.info(f"Öğrenme verileri {filename} dosyasına export edildi")
    
    def import_learning_data(self, filename: str):
        """Öğrenme verilerini import eder"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Performance metrikleri
            if 'performance_metrics' in import_data:
                self.performance_metrics.update(import_data['performance_metrics'])
            
            # Learned patterns
            if 'learned_patterns' in import_data:
                for pattern_id, pattern_data in import_data['learned_patterns'].items():
                    # DateTime string'lerini datetime objesine çevir
                    if 'last_updated' in pattern_data:
                        pattern_data['last_updated'] = datetime.fromisoformat(pattern_data['last_updated'])
                    
                    self.learned_patterns[pattern_id] = LearningPattern(**pattern_data)
            
            # User preferences
            if 'user_preferences' in import_data:
                for user_id, prefs in import_data['user_preferences'].items():
                    self.user_preferences[user_id] = prefs
            
            logging.info(f"Öğrenme verileri {filename} dosyasından import edildi")
            
        except FileNotFoundError:
            logging.warning(f"Import dosyası bulunamadı: {filename}")
        except Exception as e:
            logging.error(f"Import hatası: {e}")


class QueryOptimizer:
    """Sorgu optimizasyon sistemi"""
    
    def __init__(self, learning_system: AdaptiveLearningSystem):
        self.learning_system = learning_system
        self.optimization_rules = {
            'spelling_corrections': {},
            'synonym_mappings': {},
            'context_hints': {},
            'disambiguation_rules': {}
        }
    
    def optimize_query(self, query: str, user_id: str = None, context: Dict = None) -> Dict:
        """Sorguyu optimize eder"""
        
        optimization_result = {
            'original_query': query,
            'optimized_query': query,
            'optimizations_applied': [],
            'confidence_improvement': 0.0,
            'suggestions': []
        }
        
        # 1. Yazım hatalarını düzelt
        corrected_query, spelling_fixes = self._apply_spelling_corrections(query)
        if spelling_fixes:
            optimization_result['optimized_query'] = corrected_query
            optimization_result['optimizations_applied'].extend(spelling_fixes)
        
        # 2. Sinonimlerle genişlet
        expanded_query, synonyms_used = self._apply_synonym_expansion(corrected_query)
        if synonyms_used:
            optimization_result['optimized_query'] = expanded_query
            optimization_result['optimizations_applied'].extend(synonyms_used)
        
        # 3. Context ipuçları ekle
        contextualized_query, context_hints = self._apply_context_hints(expanded_query, context)
        if context_hints:
            optimization_result['optimized_query'] = contextualized_query
            optimization_result['optimizations_applied'].extend(context_hints)
        
        # 4. Belirsizlik giderme
        disambiguated_query, disambiguations = self._apply_disambiguation(contextualized_query, user_id)
        if disambiguations:
            optimization_result['optimized_query'] = disambiguated_query
            optimization_result['optimizations_applied'].extend(disambiguations)
        
        # 5. Confidence improvement hesapla
        optimization_result['confidence_improvement'] = len(optimization_result['optimizations_applied']) * 0.1
        
        # 6. Alternatif sorgu önerileri
        optimization_result['suggestions'] = self._generate_query_suggestions(query, user_id)
        
        return optimization_result
    
    def _apply_spelling_corrections(self, query: str) -> Tuple[str, List[str]]:
        """Yazım hatalarını düzeltir"""
        corrections_applied = []
        corrected_query = query
        
        # Yaygın yazım hataları (manuel olarak tanımlanmış)
        spelling_corrections = {
            'maas': 'maaş',
            'magas': 'mağaza',
            'calisan': 'çalışan',
            'satis': 'satış',
            'departman': 'departman',
            'hesapla': 'hesapla',
            'goster': 'göster',
            'kac': 'kaç'
        }
        
        for wrong, correct in spelling_corrections.items():
            if wrong in query.lower():
                corrected_query = corrected_query.replace(wrong, correct)
                corrections_applied.append(f"spelling_correction: {wrong} -> {correct}")
        
        return corrected_query, corrections_applied
    
    def _apply_synonym_expansion(self, query: str) -> Tuple[str, List[str]]:
        """Sinonim genişletmesi yapar"""
        synonyms_used = []
        expanded_query = query
        
        # Sinonim haritası
        synonyms = {
            'göster': ['listele', 'getir', 'ver'],
            'hesapla': ['bul', 'çıkar', 'belirle'],
            'karşılaştır': ['kıyasla', 'mukayese et'],
            'çalışan': ['personel', 'kişi', 'employee'],
            'maaş': ['ücret', 'salary'],
            'mağaza': ['şube', 'store']
        }
        
        # Context'e göre sinonim ekleme mantığı burada implementasyonu geliştirilecek
        
        return expanded_query, synonyms_used
    
    def _apply_context_hints(self, query: str, context: Dict) -> Tuple[str, List[str]]:
        """Context ipuçları ekler"""
        context_hints = []
        contextualized_query = query
        
        if context:
            # Önceki sorgulardan context çıkarımı
            if 'previous_intent' in context:
                prev_intent = context['previous_intent']
                if prev_intent == 'data_query' and 'toplam' not in query:
                    # Data query sonrası toplam sorgusu gelebilir
                    context_hints.append("context_hint: data_aggregation_likely")
        
        return contextualized_query, context_hints
    
    def _apply_disambiguation(self, query: str, user_id: str) -> Tuple[str, List[str]]:
        """Belirsizlik giderme yapar"""
        disambiguations = []
        disambiguated_query = query
        
        # Kullanıcı geçmişine göre belirsizlik giderme
        if user_id and user_id in self.learning_system.user_preferences:
            user_prefs = self.learning_system.user_preferences[user_id]
            
            # En sık kullanılan intent'e göre öncelik ver
            if 'intent_preferences' in user_prefs:
                top_intent = user_prefs['intent_preferences'].most_common(1)
                if top_intent:
                    disambiguations.append(f"user_preference: likely_{top_intent[0][0]}")
        
        return disambiguated_query, disambiguations
    
    def _generate_query_suggestions(self, query: str, user_id: str) -> List[str]:
        """Alternatif sorgu önerileri oluşturur"""
        suggestions = []
        
        # Öğrenilen pattern'lara göre öneriler
        similar_patterns = []
        normalized_query = self.learning_system._normalize_query(query)
        
        for pattern in self.learning_system.learned_patterns.values():
            if pattern.pattern_type == 'query_pattern':
                similarity = self.learning_system._calculate_similarity(
                    normalized_query, 
                    pattern.pattern_data['normalized_query']
                )
                if 0.3 < similarity < 0.7:  # Benzer ama aynı olmayan
                    similar_patterns.append((pattern, similarity))
        
        # En yüksek benzerlik skoruna göre sırala
        similar_patterns.sort(key=lambda x: x[1], reverse=True)
        
        for pattern, similarity in similar_patterns[:3]:
            suggestions.append(pattern.pattern_data['original_query'])
        
        return suggestions


# Integration helper fonksiyonları
class LearningIntegration:
    """Ana sisteme entegrasyon için yardımcı sınıf"""
    
    @staticmethod
    def create_interaction_from_query(user_id: str, query: str, intent_result: Dict, 
                                    response_data: Dict, response_time: float = 0.0) -> UserInteraction:
        """Query sonucundan interaction oluşturur"""
        
        return UserInteraction(
            user_id=user_id,
            query=query,
            intent=intent_result.get('intent', 'unknown'),
            confidence=intent_result.get('confidence', 0.0),
            response_type=response_data.get('type', 'text'),
            response_time=response_time,
            session_id=f"session_{datetime.now().strftime('%Y%m%d_%H')}",
            context={
                'entities': intent_result.get('entities', {}),
                'data_sources': response_data.get('data_sources', []),
                'processing_method': response_data.get('method', 'unknown')
            }
        )
    
    @staticmethod
    def add_user_feedback(learning_system: AdaptiveLearningSystem, 
                         user_id: str, feedback: str, query_signature: str):
        """Kullanıcı feedback'ini sisteme ekler"""
        
        # Son etkileşimi bul ve feedback ekle
        for interaction in reversed(learning_system.interaction_history):
            if (interaction.user_id == user_id and 
                learning_system._normalize_query(interaction.query) == 
                learning_system._normalize_query(query_signature)):
                
                interaction.user_feedback = feedback
                
                # Veritabanını güncelle
                with sqlite3.connect(learning_system.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE interactions 
                        SET user_feedback = ?
                        WHERE user_id = ? AND query = ?
                        ORDER BY timestamp DESC LIMIT 1
                    ''', (feedback, user_id, interaction.query))
                    conn.commit()
                
                break


# Test ve demo fonksiyonu
def test_adaptive_learning():
    """Adaptif öğrenme sistemini test eder"""
    
    print("🧠 Adaptif Öğrenme Sistemi Test Başlıyor...\n")
    
    # Sistem oluştur
    learning_system = AdaptiveLearningSystem("test_learning.db")
    optimizer = QueryOptimizer(learning_system)
    
    # Test etkileşimleri
    test_interactions = [
        ("user1", "ortalama maaş nedir?", "mathematical_calculation", 0.9, "calculation_result"),
        ("user1", "toplam çalışan sayısı kaç?", "aggregation", 0.8, "count_result"),
        ("user2", "en yüksek maaşlı kim?", "data_query", 0.7, "employee_data"),
        ("user1", "mağaza satışlarını karşılaştır", "comparison", 0.6, "comparison_chart"),
        ("user2", "ortalama maaş", "mathematical_calculation", 0.85, "calculation_result"),
    ]
    
    # Etkileşimleri kaydet
    for user_id, query, intent, confidence, response_type in test_interactions:
        interaction = UserInteraction(
            user_id=user_id,
            query=query,
            intent=intent,
            confidence=confidence,
            response_type=response_type,
            response_time=np.random.uniform(0.5, 3.0),
            user_feedback='positive' if confidence > 0.75 else None
        )
        learning_system.record_interaction(interaction)
    
    print("✅ Test etkileşimleri kaydedildi")
    
    # Intent önerilerini test et
    test_query = "ortalama maaş hesapla"
    suggestions = learning_system.get_intent_suggestions(test_query, "user1")
    print(f"\n🎯 '{test_query}' için öneriler:")
    print(f"   Primary Intent: {suggestions['primary_intent']}")
    print(f"   Confidence Boost: +{suggestions['confidence_boost']:.2f}")
    
    # Query optimization test
    optimization_result = optimizer.optimize_query("maas ortalamasi", "user1")
    print(f"\n🔧 Query Optimization:")
    print(f"   Original: {optimization_result['original_query']}")
    print(f"   Optimized: {optimization_result['optimized_query']}")
    print(f"   Optimizations: {optimization_result['optimizations_applied']}")
    
    # Performans raporu
    performance_report = learning_system.get_performance_report()
    print(f"\n📊 Performans Raporu:")
    print(f"   Toplam Sorgu: {performance_report['summary']['total_queries']}")
    print(f"   Başarı Oranı: %{performance_report['summary']['success_rate']*100:.1f}")
    print(f"   Öğrenilen Pattern: {performance_report['summary']['learned_patterns']}")
    print(f"   Öğrenme Trendi: {performance_report['learning_progress']['trend']}")
    
    if performance_report['recommendations']:
        print(f"\n💡 İyileştirme Önerileri:")
        for rec in performance_report['recommendations']:
            print(f"   - {rec}")
    
    # Export test
    learning_system.export_learning_data("test_export.json")
    print(f"\n💾 Veriler export edildi: test_export.json")
    
    print(f"\n🎉 Test tamamlandı!")


if __name__ == "__main__":
    test_adaptive_learning()