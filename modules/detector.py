# modules/detector.py
import pandas as pd
from typing import Tuple, Dict

SUPPORTED_STORES = ['fashion','electronics','beauty','home_garden','digital','subscription','handmade','food','general']

class StoreTypeDetector:
    """كشف نوع المتجر بناءً على أسماء الأعمدة وعينات القيم"""
    STORE_PATTERNS = {
        'fashion': {
            'column_keywords': ['size','color','variant','dress','shirt','pants','fashion','clothing'],
            'value_indicators': ['cm','size','s','m','l','xl']
        },
        'electronics': {
            'column_keywords': ['model','warranty','spec','gb','mp','inch','battery'],
            'value_indicators': ['gb','mp','inch','ghz']
        },
        'food': {
            'column_keywords': ['expiry','ingredient','nutrition','weight'],
            'value_indicators': ['g','kg','calories','organic']
        }
        # يمكن توسيعه
    }

    def detect(self, df: pd.DataFrame) -> Tuple[str, Dict[str,int]]:
        cols = [str(c).lower() for c in df.columns]
        scores = {k:0 for k in SUPPORTED_STORES}
        sample = df.head(50).astype(str).fillna('').values.flatten()
        sample_text = " ".join(sample).lower()

        for store, patt in self.STORE_PATTERNS.items():
            for kw in patt.get('column_keywords',[]):
                if any(kw in c for c in cols):
                    scores[store] += 3
            for ind in patt.get('value_indicators',[]):
                if ind in sample_text:
                    scores[store] += 1

        # choose best
        best = max(scores.items(), key=lambda x: x[1])
        if best[1] == 0:
            return 'general', scores
        return best[0], scores