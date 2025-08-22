# advanced_analytics_engine.py
"""
İleri Düzey Analiz Motoru - Gelişmiş veri analizi ve tahmin yetenekleri
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import logging
from datetime import datetime, timedelta
import json

# İsteğe bağlı kütüphaneler
try:
    from scipy import stats
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.linear_model import LinearRegression
    ADVANCED_STATS_AVAILABLE = True
except ImportError:
    ADVANCED_STATS_AVAILABLE = False
    logging.warning("İleri istatistik kütüphaneleri yok, temel analiz kullanılacak")

class AdvancedAnalyticsEngine:
    """İleri düzey analiz motoru"""
    
    def __init__(self):
        self.analysis_cache = {}
        self.insights_history = []
        
    def comprehensive_analysis(self, df: pd.DataFrame, filename: str) -> Dict:
        """Kapsamlı veri analizi"""
        
        analysis = {
            'filename': filename,
            'timestamp': datetime.now().isoformat(),
            'basic_stats': self._calculate_basic_stats(df),
            'business_insights': self._generate_business_insights(df),
            'anomaly_detection': self._detect_anomalies(df),
            'correlation_analysis': self._analyze_correlations(df),
            'trend_analysis': self._analyze_trends(df),
            'segmentation': self._perform_segmentation(df),
            'forecasting': self._generate_forecasts(df),
            'recommendations': []
        }
        
        # Önerileri oluştur
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _calculate_basic_stats(self, df: pd.DataFrame) -> Dict:
        """Temel istatistikler"""
        
        stats = {
            'total_rows': int(len(df)),
            'total_columns': int(len(df.columns)),
            'missing_data_percentage': float((df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100),
            'numeric_columns': [],
            'categorical_columns': [],
            'data_quality_score': 0.0
        }
        
        # Sütun tiplerini analiz et
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                col_stats = {
                    'column': str(col),
                    'mean': float(df[col].mean()) if not df[col].empty else 0.0,
                    'median': float(df[col].median()) if not df[col].empty else 0.0,
                    'std': float(df[col].std()) if not df[col].empty else 0.0,
                    'min': float(df[col].min()) if not df[col].empty else 0.0,
                    'max': float(df[col].max()) if not df[col].empty else 0.0,
                    'outlier_count': int(self._count_outliers(df[col]))
                }
                stats['numeric_columns'].append(col_stats)
            else:
                col_stats = {
                    'column': str(col),
                    'unique_count': int(df[col].nunique()),
                    'most_frequent': str(df[col].mode().iloc[0]) if not df[col].empty else '',
                    'frequency': int(df[col].value_counts().iloc[0]) if not df[col].empty else 0
                }
                stats['categorical_columns'].append(col_stats)
        
        # Veri kalitesi skoru
        missing_penalty = stats['missing_data_percentage'] / 100
        outlier_penalty = sum([col['outlier_count'] for col in stats['numeric_columns']]) / len(df) if stats['numeric_columns'] else 0
        stats['data_quality_score'] = max(0, 100 - (missing_penalty * 50) - (outlier_penalty * 30))
        
        return stats
    
    def _count_outliers(self, series: pd.Series) -> int:
        """Aykırı değer sayısını hesapla (IQR yöntemi)"""
        if len(series) < 4 or not pd.api.types.is_numeric_dtype(series):
            return 0
        
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        return len(outliers)
    
    def _generate_business_insights(self, df: pd.DataFrame) -> List[Dict]:
        """İş zekası insight'ları"""
        
        insights = []
        
        # Sales veri analizi
        if self._is_sales_data(df):
            insights.extend(self._analyze_sales_performance(df))
        
        # HR veri analizi  
        elif self._is_hr_data(df):
            insights.extend(self._analyze_hr_metrics(df))
        
        # Genel pattern'lar
        insights.extend(self._analyze_general_patterns(df))
        
        return insights
    
    def _is_sales_data(self, df: pd.DataFrame) -> bool:
        """Satış verisi mi kontrolü"""
        columns_text = ' '.join([str(col).lower() for col in df.columns])
        return any(word in columns_text for word in ['ciro', 'satış', 'sales', 'revenue', 'mağaza', 'store'])
    
    def _is_hr_data(self, df: pd.DataFrame) -> bool:
        """İK verisi mi kontrolü"""
        columns_text = ' '.join([str(col).lower() for col in df.columns])
        return any(word in columns_text for word in ['maaş', 'salary', 'çalışan', 'employee', 'departman'])
    
    def _analyze_sales_performance(self, df: pd.DataFrame) -> List[Dict]:
        """Satış performans analizi"""
        
        insights = []
        
        # Ciro sütunlarını bul
        ciro_columns = [col for col in df.columns if 'ciro' in str(col).lower()]
        growth_columns = [col for col in df.columns if 'büyüme' in str(col).lower() or 'growth' in str(col).lower()]
        
        if len(ciro_columns) >= 2:
            # Performans karşılaştırması
            col1, col2 = ciro_columns[0], ciro_columns[1]
            
            total_growth = ((df[col2].sum() - df[col1].sum()) / df[col1].sum() * 100)
            positive_growth_stores = (df[col2] > df[col1]).sum()
            negative_growth_stores = (df[col2] < df[col1]).sum()
            
            insights.append({
                'type': 'sales_performance',
                'title': 'Genel Satış Performansı',
                'value': f"%{total_growth:.2f}",
                'description': f"Toplam ciro büyümesi %{total_growth:.2f}. {positive_growth_stores} mağaza pozitif, {negative_growth_stores} mağaza negatif büyüme gösterdi.",
                'severity': 'critical' if total_growth < -10 else 'warning' if total_growth < 0 else 'good'
            })
            
            # Top/Bottom performerlar
            growth_diff = df[col2] - df[col1]
            top_performer_idx = growth_diff.idxmax()
            bottom_performer_idx = growth_diff.idxmin()
            
            store_col = next((col for col in df.columns if 'mağaza' in str(col).lower() or 'store' in str(col).lower()), None)
            
            if store_col:
                top_store = df.loc[top_performer_idx, store_col]
                bottom_store = df.loc[bottom_performer_idx, store_col]
                top_growth = growth_diff.loc[top_performer_idx]
                bottom_growth = growth_diff.loc[bottom_performer_idx]
                
                insights.append({
                    'type': 'performance_leaders',
                    'title': 'Performans Liderleri',
                    'value': f"{top_store}",
                    'description': f"En iyi: {top_store} (+{top_growth:,.0f} TL), En kötü: {bottom_store} ({bottom_growth:,.0f} TL)".replace(',', '.'),
                    'severity': 'info'
                })
        
        # Büyüme oranı analizi
        if growth_columns:
            growth_col = growth_columns[0]
            avg_growth = df[growth_col].mean()
            std_growth = df[growth_col].std()
            
            insights.append({
                'type': 'growth_analysis',
                'title': 'Büyüme Oranı Analizi',
                'value': f"%{avg_growth:.2f}",
                'description': f"Ortalama büyüme %{avg_growth:.2f} (±%{std_growth:.2f}). {'Tutarlı' if std_growth < 10 else 'Değişken'} performans gösteriliyor.",
                'severity': 'critical' if avg_growth < -10 else 'warning' if avg_growth < 0 else 'good'
            })
        
        return insights
    
    def _analyze_hr_metrics(self, df: pd.DataFrame) -> List[Dict]:
        """İK metrikleri analizi"""
        
        insights = []
        
        # Maaş analizi
        salary_columns = [col for col in df.columns if 'maaş' in str(col).lower() or 'salary' in str(col).lower()]
        dept_columns = [col for col in df.columns if 'departman' in str(col).lower()]
        
        if salary_columns and dept_columns:
            salary_col = salary_columns[0]
            dept_col = dept_columns[0]
            
            # Departman bazında maaş analizi
            dept_stats = df.groupby(dept_col)[salary_col].agg(['mean', 'count']).round(2)
            highest_avg_dept = dept_stats['mean'].idxmax()
            lowest_avg_dept = dept_stats['mean'].idxmin()
            
            insights.append({
                'type': 'salary_analysis',
                'title': 'Departman Maaş Analizi',
                'value': f"{highest_avg_dept}",
                'description': f"En yüksek ortalama: {highest_avg_dept} ({dept_stats.loc[highest_avg_dept, 'mean']:,.0f} TL), En düşük: {lowest_avg_dept} ({dept_stats.loc[lowest_avg_dept, 'mean']:,.0f} TL)".replace(',', '.'),
                'severity': 'info'
            })
            
            # Maaş dağılımı
            salary_std = df[salary_col].std()
            salary_mean = df[salary_col].mean()
            cv = (salary_std / salary_mean) * 100  # Variation coefficient
            
            insights.append({
                'type': 'salary_distribution',
                'title': 'Maaş Dağılımı',
                'value': f"%{cv:.1f}",
                'description': f"Maaş çeşitliliği %{cv:.1f}. {'Homojen' if cv < 20 else 'Orta' if cv < 40 else 'Heterojen'} dağılım.",
                'severity': 'warning' if cv > 50 else 'good'
            })
        
        return insights
    
    def _analyze_general_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Genel pattern analizi"""
        
        insights = []
        
        # Veri kalitesi
        missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        
        insights.append({
            'type': 'data_quality',
            'title': 'Veri Kalitesi',
            'value': f"%{100-missing_percentage:.1f}",
            'description': f"Veri bütünlüğü %{100-missing_percentage:.1f}. {'Mükemmel' if missing_percentage < 1 else 'İyi' if missing_percentage < 5 else 'Orta' if missing_percentage < 10 else 'Zayıf'} kalite.",
            'severity': 'good' if missing_percentage < 5 else 'warning' if missing_percentage < 15 else 'critical'
        })
        
        return insights
    
    def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict]:
        """Anomali tespiti"""
        
        anomalies = []
        
        for col in df.select_dtypes(include=[np.number]).columns:
            outlier_count = self._count_outliers(df[col])
            if outlier_count > 0:
                outlier_percentage = (outlier_count / len(df)) * 100
                
                # Aykırı değerlerin indekslerini bul
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_values = df[col][(df[col] < lower_bound) | (df[col] > upper_bound)]
                
                anomalies.append({
                    'column': str(col),
                    'count': int(outlier_count),
                    'percentage': float(outlier_percentage),
                    'values': [float(x) for x in outlier_values.head(5).tolist()],  # İlk 5 aykırı değer
                    'severity': 'high' if outlier_percentage > 10 else 'medium' if outlier_percentage > 5 else 'low'
                })
        
        return anomalies
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict:
        """Korelasyon analizi"""
        
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return {'correlations': [], 'insights': []}
        
        corr_matrix = numeric_df.corr()
        correlations = []
        insights = []
        
        # Güçlü korelasyonları bul
        for i, col1 in enumerate(numeric_df.columns):
            for j, col2 in enumerate(numeric_df.columns):
                if i < j:  # Tekrarları önle
                    corr_value = corr_matrix.loc[col1, col2]
                    if abs(corr_value) > 0.5:  # Orta-güçlü korelasyon
                        correlations.append({
                            'column1': str(col1),
                            'column2': str(col2),
                            'correlation': float(corr_value),
                            'strength': 'strong' if abs(corr_value) > 0.8 else 'moderate'
                        })
        
        # Korelasyon insight'ları
        if correlations:
            strongest = max(correlations, key=lambda x: abs(x['correlation']))
            insights.append(f"En güçlü korelasyon: {strongest['column1']} ve {strongest['column2']} arasında (r={strongest['correlation']:.3f})")
        
        return {'correlations': correlations, 'insights': insights}
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict:
        """Trend analizi"""
        
        trends = []
        
        # Zaman sütunu varsa trend analizi yap
        date_columns = df.select_dtypes(include=['datetime64', 'object']).columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        # Ciro kollarından trend çıkarımı (2024 vs 2025)
        ciro_columns = [col for col in df.columns if 'ciro' in str(col).lower()]
        
        if len(ciro_columns) >= 2:
            # Zamana dayalı trend simülasyonu
            col1, col2 = ciro_columns[0], ciro_columns[1]
            
            # Genel trend
            total_change = df[col2].sum() - df[col1].sum()
            trend_direction = 'upward' if total_change > 0 else 'downward' if total_change < 0 else 'stable'
            
            trends.append({
                'metric': 'total_revenue',
                'direction': trend_direction,
                'change_amount': float(total_change),
                'change_percentage': float((total_change / df[col1].sum()) * 100),
                'confidence': 'high'
            })
        
        return {'trends': trends}
    
    def _perform_segmentation(self, df: pd.DataFrame) -> Dict:
        """Segment analizi"""
        
        segments = []
        
        if not ADVANCED_STATS_AVAILABLE:
            return {'segments': [], 'method': 'basic'}
        
        # Sayısal sütunlar için K-means clustering
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) >= 2 and len(df) >= 5:
            try:
                # Veriyi standardize et
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(numeric_df.fillna(0))
                
                # K-means clustering (3 segment)
                kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(scaled_data)
                
                # Segment özellikleri
                df_with_clusters = df.copy()
                df_with_clusters['segment'] = cluster_labels
                
                for i in range(3):
                    segment_data = df_with_clusters[df_with_clusters['segment'] == i]
                    segment_size = len(segment_data)
                    
                    if segment_size > 0:
                        segments.append({
                            'segment_id': int(i),
                            'size': int(segment_size),
                            'percentage': float((segment_size / len(df)) * 100),
                            'characteristics': self._describe_segment(segment_data, numeric_df.columns)
                        })
                
            except Exception as e:
                logging.warning(f"Segmentasyon hatası: {e}")
        
        return {'segments': segments, 'method': 'kmeans' if segments else 'basic'}
    
    def _describe_segment(self, segment_df: pd.DataFrame, numeric_columns: List[str]) -> Dict:
        """Segment özelliklerini tanımla"""
        
        characteristics = {}
        
        for col in numeric_columns:
            if col in segment_df.columns:
                mean_val = segment_df[col].mean()
                characteristics[str(col)] = {
                    'mean': float(mean_val),
                    'median': float(segment_df[col].median()),
                    'std': float(segment_df[col].std())
                }
        
        return characteristics
    
    def _generate_forecasts(self, df: pd.DataFrame) -> Dict:
        """Tahmin analizi"""
        
        forecasts = []
        
        # Ciro sütunlarından basit trend tahmini
        ciro_columns = [col for col in df.columns if 'ciro' in str(col).lower()]
        
        if len(ciro_columns) >= 2:
            col1, col2 = ciro_columns[0], ciro_columns[1]
            
            # Linear trend hesaplama
            current_total = df[col2].sum()
            previous_total = df[col1].sum()
            growth_rate = (current_total - previous_total) / previous_total
            
            # Gelecek yıl tahmini
            next_year_forecast = current_total * (1 + growth_rate)
            
            forecasts.append({
                'metric': 'total_revenue',
                'current_value': float(current_total),
                'forecast_value': float(next_year_forecast),
                'growth_rate': float(growth_rate * 100),
                'confidence_level': 'medium',
                'method': 'linear_trend'
            })
        
        return {'forecasts': forecasts}
    
    def _generate_recommendations(self, analysis: Dict) -> List[Dict]:
        """Aksiyon önerileri oluştur"""
        
        recommendations = []
        
        # Veri kalitesi önerileri
        if analysis['basic_stats']['data_quality_score'] < 80:
            recommendations.append({
                'category': 'data_quality',
                'priority': 'high',
                'title': 'Veri Kalitesi İyileştirmesi',
                'description': 'Eksik veri ve aykırı değerler analiz edilmeli',
                'action_items': [
                    'Eksik veri kaynaklarını belirle',
                    'Aykırı değerleri incele',
                    'Veri toplama süreçlerini gözden geçir'
                ]
            })
        
        # İş performansı önerileri
        business_insights = analysis['business_insights']
        critical_insights = [insight for insight in business_insights if insight.get('severity') == 'critical']
        
        if critical_insights:
            recommendations.append({
                'category': 'business_performance',
                'priority': 'high',
                'title': 'Kritik Performans Problemleri',
                'description': f"{len(critical_insights)} kritik alan tespit edildi",
                'action_items': [insight['description'] for insight in critical_insights[:3]]
            })
        
        # Anomali önerileri
        if analysis['anomaly_detection']:
            high_severity_anomalies = [a for a in analysis['anomaly_detection'] if a['severity'] == 'high']
            if high_severity_anomalies:
                recommendations.append({
                    'category': 'anomaly_management',
                    'priority': 'medium',
                    'title': 'Aykırı Değer Yönetimi',
                    'description': f"{len(high_severity_anomalies)} sütunda yüksek seviye anomali",
                    'action_items': [f"{a['column']} sütunundaki {a['count']} aykırı değeri incele" for a in high_severity_anomalies]
                })
        
        return recommendations


def test_advanced_analytics():
    """Gelişmiş analitik motoru test et"""
    
    print("🚀 Advanced Analytics Engine Test Başlıyor...")
    
    engine = AdvancedAnalyticsEngine()
    
    # Sales.xlsx dosyasını test et
    import os
    test_files = ['company_data/sales.xlsx', 'sales.xlsx']
    
    for filename in test_files:
        if os.path.exists(filename):
            print(f"\n📊 {filename} Kapsamlı Analiz:")
            print("=" * 50)
            
            try:
                df = pd.read_excel(filename)
                analysis = engine.comprehensive_analysis(df, filename)
                
                # Temel istatistikler
                basic = analysis['basic_stats']
                print(f"\n📋 Temel İstatistikler:")
                print(f"   Veri Kalitesi: %{basic['data_quality_score']:.1f}")
                print(f"   Sayısal Sütun: {len(basic['numeric_columns'])}")
                print(f"   Kategorik Sütun: {len(basic['categorical_columns'])}")
                
                # İş içgörüleri
                insights = analysis['business_insights']
                if insights:
                    print(f"\n💡 İş İçgörüleri:")
                    for insight in insights:
                        severity_emoji = {
                            'critical': '🔴',
                            'warning': '🟡', 
                            'good': '🟢',
                            'info': '🔵'
                        }.get(insight['severity'], '⚪')
                        
                        print(f"   {severity_emoji} {insight['title']}: {insight['value']}")
                        print(f"      {insight['description']}")
                
                # Anomaliler
                anomalies = analysis['anomaly_detection']
                if anomalies:
                    print(f"\n🔍 Tespit Edilen Anomaliler:")
                    for anomaly in anomalies[:3]:  # İlk 3 anomali
                        print(f"   ⚠️ {anomaly['column']}: {anomaly['count']} aykırı değer (%{anomaly['percentage']:.1f})")
                
                # Korelasyonlar
                corr_analysis = analysis['correlation_analysis']
                if corr_analysis['correlations']:
                    print(f"\n🔗 Güçlü Korelasyonlar:")
                    for corr in corr_analysis['correlations'][:3]:
                        print(f"   📈 {corr['column1']} ↔ {corr['column2']}: r={corr['correlation']:.3f}")
                
                # Tahminler
                forecasts = analysis['forecasting']['forecasts']
                if forecasts:
                    print(f"\n🔮 Gelecek Tahminleri:")
                    for forecast in forecasts:
                        print(f"   📊 {forecast['metric']}: {forecast['current_value']:,.0f} → {forecast['forecast_value']:,.0f} (Büyüme: %{forecast['growth_rate']:.1f})".replace(',', '.'))
                
                # Öneriler
                recommendations = analysis['recommendations']
                if recommendations:
                    print(f"\n🎯 Aksiyon Önerileri:")
                    for rec in recommendations:
                        priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(rec['priority'], '⚪')
                        print(f"   {priority_emoji} {rec['title']}: {rec['description']}")
                        
                        for action in rec['action_items'][:2]:  # İlk 2 aksiyon
                            print(f"      • {action}")
                
                print(f"\n🎉 Kapsamlı analiz tamamlandı!")
                break
                
            except Exception as e:
                print(f"❌ Analiz hatası: {e}")
                import traceback
                traceback.print_exc()
    
    else:
        print("❌ Test dosyası bulunamadı")


if __name__ == "__main__":
    test_advanced_analytics()