# smart_intent_engine.py
"""
Akıllı Niyet Tanıma Motoru - Kullanıcı sorgularını daha iyi anlar ve kategorize eder
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from fuzzywuzzy import fuzz
import numpy as np

@dataclass
class Intent:
    """Intent veri yapısı"""
    name: str
    confidence: float
    entities: Dict
    suggested_action: str
    context_needed: List[str]

@dataclass
class EntityMatch:
    """Varlık eşleşme bilgisi"""
    entity_type: str
    value: str
    confidence: float
    position: Tuple[int, int]

class SmartIntentEngine:
    def __init__(self):
        """Akıllı intent motoru"""
        
        # Gelişmiş intent pattern'ları
        self.intent_patterns = {
            'data_analysis': {
                'patterns': [
                    r'analiz\s+(?:et|yap|göster)',
                    r'(?:nasıl|ne\s+kadar)\s+(?:performans|durum)',
                    r'raporla\w*',
                    r'değerlendir\w*',
                    r'karşılaştır\w*'
                ],
                'keywords': ['analiz', 'rapor', 'değerlendirme', 'karşılaştırma', 'trend', 'pattern'],
                'context': ['data_source', 'time_period', 'metrics'],
                'confidence_boost': 1.2
            },
            
            'mathematical_calculation': {
                'patterns': [
                    r'hesapla\w*',
                    r'(?:kaç|ne\s+kadar)\s+(?:eder|yapar)',
                    r'\d+\s*[+\-*/×÷]\s*\d+',
                    r'topla\w*|çıkar\w*|çarp\w*|böl\w*',
                    r'ortalama\w*|minimum\w*|maksimum\w*'
                ],
                'keywords': ['hesapla', 'topla', 'çarp', 'böl', 'ortalama', 'maksimum', 'minimum', 'yüzde'],
                'context': ['numbers', 'operation_type', 'data_column'],
                'confidence_boost': 1.3
            },
            
            'data_query': {
                'patterns': [
                    r'(?:göster|listele|getir)\w*',
                    r'(?:hangi|kim|ne)\s+(?:olan|yapan|bulunan)',
                    r'(?:kaç|ne\s+kadar)\s+(?:tane|adet|kişi)',
                    r'(?:en\s+(?:yüksek|düşük|iyi|kötü))'
                ],
                'keywords': ['göster', 'listele', 'kaç', 'hangi', 'kim', 'en yüksek', 'en düşük'],
                'context': ['entity_type', 'filter_criteria', 'sort_order'],
                'confidence_boost': 1.1
            },
            
            'comparison': {
                'patterns': [
                    r'(?:karşılaştır|kıyasla)\w*',
                    r'(?:fark|farkı)\w*',
                    r'(?:ile|arasında)\s+(?:fark|karşılaştırma)',
                    r'(?:hangisi\s+(?:daha|en))',
                    r'(?:kaç\s+kat|misli)'
                ],
                'keywords': ['karşılaştır', 'fark', 'kıyasla', 'hangisi daha', 'kat', 'misli'],
                'context': ['entities_to_compare', 'comparison_metric'],
                'confidence_boost': 1.2
            },
            
            'aggregation': {
                'patterns': [
                    r'toplam\w*',
                    r'genel\w*',
                    r'tüm\w*',
                    r'hep(?:si|i)\w*',
                    r'(?:sayısı|adedi)'
                ],
                'keywords': ['toplam', 'genel', 'tüm', 'hepsi', 'sayısı', 'adet'],
                'context': ['aggregation_type', 'data_scope'],
                'confidence_boost': 1.1
            },
            
            'search_and_filter': {
                'patterns': [
                    r'(?:ara|bul)\w*',
                    r'(?:filtrele|süz)\w*',
                    r'(?:sadece|yalnız|only)',
                    r'(?:olan|bulunan|yapan)'
                ],
                'keywords': ['ara', 'bul', 'filtrele', 'sadece', 'olan', 'bulunan'],
                'context': ['search_criteria', 'filter_conditions'],
                'confidence_boost': 1.0
            },
            
            'trend_analysis': {
                'patterns': [
                    r'trend\w*',
                    r'(?:artış|azalış|değişim)\w*',
                    r'(?:büyüme|küçülme|gelişim)\w*',
                    r'(?:zaman|dönem|ay|yıl)\s+(?:bazında|göre)',
                    r'(?:geçen|önceki|şu)\s+(?:ay|yıl|dönem)'
                ],
                'keywords': ['trend', 'artış', 'azalış', 'büyüme', 'değişim', 'zaman', 'dönem'],
                'context': ['time_dimension', 'metric', 'comparison_period'],
                'confidence_boost': 1.2
            },
            
            'help_and_guidance': {
                'patterns': [
                    r'(?:nasıl|ne\s+şekilde)',
                    r'(?:yardım|help)',
                    r'(?:anlamadım|bilmiyorum)',
                    r'(?:örnek|sample)',
                    r'(?:açıkla|explain)'
                ],
                'keywords': ['nasıl', 'yardım', 'help', 'örnek', 'açıkla', 'anlamadım'],
                'context': ['help_topic'],
                'confidence_boost': 0.9
            }
        }
        
        # Varlık tanıma pattern'ları
        self.entity_patterns = {
            'numbers': r'\b\d+(?:[.,]\d+)?\b',
            'percentages': r'\b\d+(?:[.,]\d+)?%',
            'dates': r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b',
            'money': r'\b\d+(?:[.,]\d+)?\s*(?:TL|₺|lira|euro|dolar|\$)\b',
            'operators': r'[+\-*/×÷=]',
            'comparison_words': r'\b(?:büyük|küçük|yüksek|düşük|fazla|az|iyi|kötü)\b',
            'time_words': r'\b(?:bugün|dün|yarın|geçen|şu|gelecek|ay|yıl|hafta|gün)\b'
        }
        
        # Domain-specific entities (veri setinden öğrenilecek)
        self.learned_entities = {
            'employees': set(),
            'departments': set(),
            'stores': set(),
            'products': set(),
            'metrics': set()
        }
        
        # Context tracking
        self.conversation_context = {}
        
    def analyze_intent(self, query: str, context: Dict = None) -> Intent:
        """Ana intent analiz fonksiyonu"""
        
        query = query.strip()
        query_lower = query.lower()
        
        # 1. Varlıkları çıkar
        entities = self._extract_entities(query)
        
        # 2. Intent'leri puanla
        intent_scores = self._score_intents(query_lower, entities)
        
        # 3. En yüksek puanlı intent'i seç
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_name, confidence = best_intent
        
        # 4. Context analizi
        context_needed = self._analyze_context_needs(intent_name, entities, query_lower)
        
        # 5. Önerilen aksiyonu belirle
        suggested_action = self._suggest_action(intent_name, entities, confidence)
        
        return Intent(
            name=intent_name,
            confidence=confidence,
            entities=entities,
            suggested_action=suggested_action,
            context_needed=context_needed
        )
    
    def _extract_entities(self, query: str) -> Dict:
        """Varlıkları çıkarır"""
        entities = {}
        
        # Genel pattern'larla varlık çıkarımı
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, query, re.IGNORECASE)
            entity_matches = []
            
            for match in matches:
                entity_matches.append(EntityMatch(
                    entity_type=entity_type,
                    value=match.group(),
                    confidence=0.9,
                    position=(match.start(), match.end())
                ))
            
            if entity_matches:
                entities[entity_type] = entity_matches
        
        # Öğrenilmiş varlıkları kontrol et
        query_lower = query.lower()
        
        for entity_category, entity_set in self.learned_entities.items():
            matches = []
            for entity in entity_set:
                if entity.lower() in query_lower:
                    # Fuzzy matching için confidence hesapla
                    confidence = fuzz.ratio(entity.lower(), query_lower) / 100.0
                    if confidence > 0.6:  # %60 eşik
                        matches.append(EntityMatch(
                            entity_type=entity_category,
                            value=entity,
                            confidence=confidence,
                            position=(0, 0)  # Pozisyon tespiti geliştirilecek
                        ))
            
            if matches:
                entities[entity_category] = matches
        
        return entities
    
    def _score_intents(self, query_lower: str, entities: Dict) -> Dict[str, float]:
        """Intent'leri puanlar"""
        scores = {}
        
        for intent_name, intent_config in self.intent_patterns.items():
            score = 0.0
            
            # Pattern matching
            pattern_matches = 0
            for pattern in intent_config['patterns']:
                if re.search(pattern, query_lower):
                    pattern_matches += 1
                    score += 2.0  # Pattern match bonus
            
            # Keyword matching
            keyword_matches = 0
            for keyword in intent_config['keywords']:
                if keyword in query_lower:
                    keyword_matches += 1
                    score += 1.0  # Keyword match bonus
            
            # Entity context bonus
            if intent_name == 'mathematical_calculation' and 'numbers' in entities:
                score += 1.5
            
            if intent_name == 'comparison' and len(entities.get('employees', [])) >= 2:
                score += 1.0
            
            # Confidence boost uygula
            score *= intent_config.get('confidence_boost', 1.0)
            
            # Normalize (0-1 arası)
            max_possible_score = (len(intent_config['patterns']) * 2 + 
                                len(intent_config['keywords']) * 1 + 2) * intent_config.get('confidence_boost', 1.0)
            
            normalized_score = min(score / max_possible_score, 1.0) if max_possible_score > 0 else 0.0
            scores[intent_name] = normalized_score
        
        return scores
    
    def _analyze_context_needs(self, intent_name: str, entities: Dict, query: str) -> List[str]:
        """Eksik context'leri analiz eder"""
        needed_context = []
        
        intent_config = self.intent_patterns.get(intent_name, {})
        required_context = intent_config.get('context', [])
        
        for context_item in required_context:
            if context_item == 'data_source' and not any(k in entities for k in ['employees', 'stores', 'departments']):
                needed_context.append('data_source')
            
            elif context_item == 'numbers' and 'numbers' not in entities:
                needed_context.append('numbers')
            
            elif context_item == 'operation_type' and not any(op in query for op in ['topla', 'çıkar', 'çarp', 'böl', 'ortalama']):
                needed_context.append('operation_type')
            
            elif context_item == 'comparison_metric' and intent_name == 'comparison':
                if not any(metric in query for metric in ['maaş', 'satış', 'ciro', 'performans']):
                    needed_context.append('comparison_metric')
        
        return needed_context
    
    def _suggest_action(self, intent_name: str, entities: Dict, confidence: float) -> str:
        """Önerilen aksiyonu belirler"""
        
        if confidence < 0.3:
            return "clarify_intent"  # Intent belirsiz, açıklama iste
        
        action_mapping = {
            'mathematical_calculation': 'execute_calculation',
            'data_query': 'fetch_data',
            'comparison': 'compare_entities',
            'aggregation': 'aggregate_data',
            'search_and_filter': 'filter_data',
            'trend_analysis': 'analyze_trends',
            'data_analysis': 'generate_report',
            'help_and_guidance': 'provide_help'
        }
        
        base_action = action_mapping.get(intent_name, 'general_query')
        
        # Entity'lere göre aksiyonu özelleştir
        if 'numbers' in entities and len(entities['numbers']) >= 2:
            if intent_name == 'mathematical_calculation':
                return 'execute_arithmetic'
        
        if 'employees' in entities:
            if intent_name == 'data_query':
                return 'fetch_employee_data'
            elif intent_name == 'comparison':
                return 'compare_employees'
        
        return base_action
    
    def learn_from_data(self, data_insights: Dict):
        """Veri setinden öğrenme"""
        
        for filename, insights in data_insights.items():
            if insights.get('type') in ['excel', 'csv']:
                
                # Çalışan isimlerini öğren
                if 'employee_rows' in insights:
                    self.learned_entities['employees'].update(insights['employee_rows'].keys())
                
                # Mağaza isimlerini öğren
                if 'store_rows' in insights:
                    self.learned_entities['stores'].update(insights['store_rows'].keys())
        
        logging.info(f"Öğrenilen varlıklar: {len(self.learned_entities['employees'])} çalışan, {len(self.learned_entities['stores'])} mağaza")
    
    def generate_clarification_questions(self, intent: Intent) -> List[str]:
        """Belirsiz intent'ler için açıklayıcı sorular"""
        questions = []
        
        if intent.confidence < 0.5:
            questions.append("Hangi konuda yardıma ihtiyacınız var?")
            
            # Context eksikliklerine göre sorular
            for context in intent.context_needed:
                if context == 'data_source':
                    questions.append("Hangi veri üzerinde işlem yapmak istiyorsunuz? (çalışanlar, mağazalar, satışlar)")
                elif context == 'operation_type':
                    questions.append("Hangi hesaplama işlemini yapmak istiyorsunuz? (toplama, ortalama, karşılaştırma)")
                elif context == 'comparison_metric':
                    questions.append("Neye göre karşılaştırma yapmak istiyorsunuz? (maaş, satış, performans)")
        
        return questions[:3]  # En fazla 3 soru
    
    def get_suggested_queries(self, intent: Intent, available_data: List[str]) -> List[str]:
        """Intent'e uygun sorgu önerileri"""
        suggestions = []
        
        intent_suggestions = {
            'mathematical_calculation': [
                "Ortalama maaş nedir?",
                "Toplam satış tutarı kaç?",
                "En yüksek ve en düşük maaş arasındaki fark nedir?"
            ],
            'data_query': [
                "Tüm çalışanları listele",
                "Hangi departmanlarda kimler çalışıyor?",
                "En yüksek satış yapan mağaza hangisi?"
            ],
            'comparison': [
                "Departmanlar arası maaş karşılaştırması",
                "Mağaza performans karşılaştırması",
                "Bu ay geçen aya göre satış durumu"
            ],
            'aggregation': [
                "Toplam çalışan sayısı",
                "Departman bazında çalışan dağılımı",
                "Genel satış özeti"
            ]
        }
        
        base_suggestions = intent_suggestions.get(intent.name, [])
        
        # Mevcut veriye göre özelleştir
        if 'çalışan' in available_data:
            suggestions.extend([
                "Çalışan maaş analizi yap",
                "Departman bazında çalışan sayısı"
            ])
        
        if 'satış' in available_data:
            suggestions.extend([
                "Satış trend analizi",
                "Mağaza bazında ciro karşılaştırması"
            ])
        
        return list(set(base_suggestions + suggestions))[:5]


class IntentTrainer:
    """Intent sistemini eğitmek için yardımcı sınıf"""
    
    def __init__(self, intent_engine: SmartIntentEngine):
        self.engine = intent_engine
        self.training_data = []
    
    def add_training_example(self, query: str, expected_intent: str, entities: Dict = None):
        """Eğitim verisi ekle"""
        self.training_data.append({
            'query': query,
            'intent': expected_intent,
            'entities': entities or {}
        })
    
    def load_training_data(self, filename: str):
        """JSON'dan eğitim verisi yükle"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.training_data.extend(data)
        except FileNotFoundError:
            logging.warning(f"Eğitim dosyası bulunamadı: {filename}")
    
    def evaluate_accuracy(self) -> Dict:
        """Sistem doğruluğunu değerlendir"""
        correct = 0
        total = len(self.training_data)
        
        results = {
            'accuracy': 0.0,
            'intent_performance': {},
            'errors': []
        }
        
        for example in self.training_data:
            predicted = self.engine.analyze_intent(example['query'])
            
            if predicted.name == example['intent']:
                correct += 1
            else:
                results['errors'].append({
                    'query': example['query'],
                    'expected': example['intent'],
                    'predicted': predicted.name,
                    'confidence': predicted.confidence
                })
        
        results['accuracy'] = correct / total if total > 0 else 0.0
        return results
    
    def generate_training_data_template(self) -> Dict:
        """Eğitim verisi şablonu oluştur"""
        template = []
        
        for intent_name in self.engine.intent_patterns.keys():
            template.append({
                "query": f"Örnek {intent_name} sorgusu",
                "intent": intent_name,
                "entities": {},
                "explanation": f"{intent_name} intent'i için örnek"
            })
        
        return template


# Test ve kullanım örneği
def test_smart_intent_engine():
    """Test fonksiyonu"""
    
    # Engine'i oluştur
    engine = SmartIntentEngine()
    
    # Test sorguları
    test_queries = [
        "Ortalama maaş nedir?",
        "Ahmet ile Mehmet'in maaşlarını karşılaştır",
        "Toplam çalışan sayısı kaç?",
        "En yüksek satış yapan mağaza hangisi?",
        "Bilgi İşlem departmanında kaç kişi çalışıyor?",
        "Geçen ay bu aya göre satış artışı ne kadar?",
        "Bu verilerle ne yapabilirim?",
        "100 * 25 kaç eder?"
    ]
    
    print("🧠 Smart Intent Engine Test Sonuçları\n")
    
    for query in test_queries:
        intent = engine.analyze_intent(query)
        
        print(f"📝 Sorgu: '{query}'")
        print(f"🎯 Intent: {intent.name} (Güven: %{intent.confidence*100:.1f})")
        print(f"🔧 Önerilen Aksiyon: {intent.suggested_action}")
        
        if intent.entities:
            print(f"📊 Bulunan Varlıklar:")
            for entity_type, entities in intent.entities.items():
                values = [e.value for e in entities] if isinstance(entities, list) else entities
                print(f"   - {entity_type}: {values}")
        
        if intent.context_needed:
            print(f"❓ Eksik Context: {intent.context_needed}")
            
            # Açıklayıcı sorular öner
            questions = engine.generate_clarification_questions(intent)
            if questions:
                print(f"💭 Önerilen Sorular:")
                for q in questions:
                    print(f"   - {q}")
        
        print("-" * 60)


if __name__ == "__main__":
    test_smart_intent_engine()