# pattern_scanner.py - Scan 15+ patterns de chandeliers (PRO)

import pandas as pd
import numpy as np

class PatternScanner:
    """Scanner de patterns de chandeliers japonais - Version PRO"""
    
    def __init__(self):
        self.patterns_detected = []
        self.pattern_catalog = self._init_pattern_catalog()
        
        print("✅ Pattern Scanner initialisé (15+ patterns)")
    
    def _init_pattern_catalog(self):
        """Catalogue des patterns avec leur fiabilité"""
        return {
            # PATTERNS HAUSSIERS (bullish)
            'hammer': {'type': 'bullish', 'reliability': 80},
            'inverted_hammer': {'type': 'bullish', 'reliability': 75},
            'bullish_engulfing': {'type': 'bullish', 'reliability': 85},
            'piercing_line': {'type': 'bullish', 'reliability': 75},
            'morning_star': {'type': 'bullish', 'reliability': 90},
            'three_white_soldiers': {'type': 'bullish', 'reliability': 85},
            'bullish_harami': {'type': 'bullish', 'reliability': 70},
            'dragonfly_doji': {'type': 'bullish', 'reliability': 65},
            
            # PATTERNS BAISSIERS (bearish)
            'shooting_star': {'type': 'bearish', 'reliability': 80},
            'hanging_man': {'type': 'bearish', 'reliability': 75},
            'bearish_engulfing': {'type': 'bearish', 'reliability': 85},
            'dark_cloud_cover': {'type': 'bearish', 'reliability': 75},
            'evening_star': {'type': 'bearish', 'reliability': 90},
            'three_black_crows': {'type': 'bearish', 'reliability': 85},
            'bearish_harami': {'type': 'bearish', 'reliability': 70},
            'gravestone_doji': {'type': 'bearish', 'reliability': 65},
            
            # PATTERNS NEUTRES
            'doji': {'type': 'neutral', 'reliability': 60},
            'spinning_top': {'type': 'neutral', 'reliability': 50}
        }
    
    def scan_all_patterns(self, df):
        """
        Scanne TOUS les patterns sur les dernières bougies
        
        Returns:
            list: Patterns détectés avec scores
        """
        if df is None or len(df) < 3:
            return []
        
        self.patterns_detected = []
        
        # Patterns 1 bougie
        self._check_hammer(df)
        self._check_inverted_hammer(df)
        self._check_shooting_star(df)
        self._check_hanging_man(df)
        self._check_doji(df)
        self._check_dragonfly_doji(df)
        self._check_gravestone_doji(df)
        self._check_spinning_top(df)
        
        # Patterns 2 bougies
        if len(df) >= 2:
            self._check_engulfing(df)
            self._check_piercing_line(df)
            self._check_dark_cloud_cover(df)
            self._check_harami(df)
        
        # Patterns 3 bougies
        if len(df) >= 3:
            self._check_morning_star(df)
            self._check_evening_star(df)
            self._check_three_soldiers(df)
            self._check_three_crows(df)
        
        return self.patterns_detected
    
    # ═══════════════════════════════════════════════════════════
    # PATTERNS 1 BOUGIE
    # ═══════════════════════════════════════════════════════════
    
    def _check_hammer(self, df):
        """Marteau - Pattern haussier"""
        candle = df.iloc[-1]
        
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        total_range = candle['high'] - candle['low']
        
        if total_range == 0:
            return
        
        # Marteau : longue ombre basse (2x le corps), petit corps, petite ombre haute
        if (lower_shadow > body * 2 and 
            upper_shadow < body * 0.3 and
            body / total_range < 0.3 and
            candle['close'] > candle['open']):  # Bougie verte
            
            self.patterns_detected.append({
                'name': 'hammer',
                'type': 'bullish',
                'reliability': 80,
                'description': '🔨 Marteau - Fort signal haussier',
                'candle_index': len(df) - 1
            })
    
    def _check_inverted_hammer(self, df):
        """Marteau inversé - Pattern haussier"""
        candle = df.iloc[-1]
        
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        total_range = candle['high'] - candle['low']
        
        if total_range == 0:
            return
        
        # Marteau inversé : longue ombre haute, petit corps, petite ombre basse
        if (upper_shadow > body * 2 and 
            lower_shadow < body * 0.3 and
            body / total_range < 0.3):
            
            self.patterns_detected.append({
                'name': 'inverted_hammer',
                'type': 'bullish',
                'reliability': 75,
                'description': '🔨 Marteau inversé - Signal haussier',
                'candle_index': len(df) - 1
            })
    
    def _check_shooting_star(self, df):
        """Étoile filante - Pattern baissier"""
        candle = df.iloc[-1]
        
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        total_range = candle['high'] - candle['low']
        
        if total_range == 0:
            return
        
        # Étoile filante : longue ombre haute, petit corps, petite ombre basse, bougie rouge
        if (upper_shadow > body * 2 and 
            lower_shadow < body * 0.3 and
            body / total_range < 0.3 and
            candle['close'] < candle['open']):  # Bougie rouge
            
            self.patterns_detected.append({
                'name': 'shooting_star',
                'type': 'bearish',
                'reliability': 80,
                'description': '⭐ Étoile filante - Fort signal baissier',
                'candle_index': len(df) - 1
            })
    
    def _check_hanging_man(self, df):
        """Pendu - Pattern baissier"""
        candle = df.iloc[-1]
        prev_candle = df.iloc[-2] if len(df) >= 2 else None
        
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        total_range = candle['high'] - candle['low']
        
        if total_range == 0:
            return
        
        # Pendu : ressemble au marteau mais apparaît après une hausse
        if (lower_shadow > body * 2 and 
            upper_shadow < body * 0.3 and
            body / total_range < 0.3 and
            prev_candle is not None and
            candle['close'] > prev_candle['close']):  # Après une hausse
            
            self.patterns_detected.append({
                'name': 'hanging_man',
                'type': 'bearish',
                'reliability': 75,
                'description': '🧑‍🦯 Pendu - Signal baissier',
                'candle_index': len(df) - 1
            })
    
    def _check_doji(self, df):
        """Doji - Pattern d'indécision"""
        candle = df.iloc[-1]
        
        body = abs(candle['close'] - candle['open'])
        total_range = candle['high'] - candle['low']
        
        if total_range == 0:
            return
        
        # Doji : corps très petit (< 10% du range total)
        if body / total_range < 0.1:
            self.patterns_detected.append({
                'name': 'doji',
                'type': 'neutral',
                'reliability': 60,
                'description': '🎯 Doji - Indécision, possible retournement',
                'candle_index': len(df) - 1
            })
    
    def _check_dragonfly_doji(self, df):
        """Doji libellule - Pattern haussier"""
        candle = df.iloc[-1]
        
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        total_range = candle['high'] - candle['low']
        
        if total_range == 0:
            return
        
        # Doji libellule : petit corps, longue ombre basse, pas d'ombre haute
        if (body / total_range < 0.1 and
            lower_shadow > total_range * 0.6 and
            upper_shadow < total_range * 0.1):
            
            self.patterns_detected.append({
                'name': 'dragonfly_doji',
                'type': 'bullish',
                'reliability': 65,
                'description': '🦗 Doji libellule - Signal haussier',
                'candle_index': len(df) - 1
            })
    
    def _check_gravestone_doji(self, df):
        """Doji pierre tombale - Pattern baissier"""
        candle = df.iloc[-1]
        
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        total_range = candle['high'] - candle['low']
        
        if total_range == 0:
            return
        
        # Doji pierre tombale : petit corps, longue ombre haute, pas d'ombre basse
        if (body / total_range < 0.1 and
            upper_shadow > total_range * 0.6 and
            lower_shadow < total_range * 0.1):
            
            self.patterns_detected.append({
                'name': 'gravestone_doji',
                'type': 'bearish',
                'reliability': 65,
                'description': '🪦 Doji pierre tombale - Signal baissier',
                'candle_index': len(df) - 1
            })
    
    def _check_spinning_top(self, df):
        """Toupie - Pattern d'indécision"""
        candle = df.iloc[-1]
        
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        total_range = candle['high'] - candle['low']
        
        if total_range == 0:
            return
        
        # Toupie : petit corps, ombres similaires des deux côtés
        if (body / total_range < 0.3 and
            0.3 < lower_shadow / total_range < 0.5 and
            0.3 < upper_shadow / total_range < 0.5):
            
            self.patterns_detected.append({
                'name': 'spinning_top',
                'type': 'neutral',
                'reliability': 50,
                'description': '🌪️ Toupie - Indécision forte',
                'candle_index': len(df) - 1
            })
    
    # ═══════════════════════════════════════════════════════════
    # PATTERNS 2 BOUGIES
    # ═══════════════════════════════════════════════════════════
    
    def _check_engulfing(self, df):
        """Engloutissant haussier/baissier"""
        if len(df) < 2:
            return
        
        prev = df.iloc[-2]
        curr = df.iloc[-1]
        
        prev_body = prev['close'] - prev['open']
        curr_body = curr['close'] - curr['open']
        
        # Engloutissant haussier
        if (prev_body < 0 and curr_body > 0 and  # prev rouge, curr verte
            curr['close'] > prev['open'] and
            curr['open'] < prev['close'] and
            abs(curr_body) > abs(prev_body) * 1.2):  # Corps actuel > 120% du précédent
            
            self.patterns_detected.append({
                'name': 'bullish_engulfing',
                'type': 'bullish',
                'reliability': 85,
                'description': '📊 Engloutissant haussier - Fort signal achat',
                'candle_index': len(df) - 1
            })
        
        # Engloutissant baissier
        elif (prev_body > 0 and curr_body < 0 and  # prev verte, curr rouge
              curr['close'] < prev['open'] and
              curr['open'] > prev['close'] and
              abs(curr_body) > abs(prev_body) * 1.2):
            
            self.patterns_detected.append({
                'name': 'bearish_engulfing',
                'type': 'bearish',
                'reliability': 85,
                'description': '📉 Engloutissant baissier - Fort signal vente',
                'candle_index': len(df) - 1
            })
    
    def _check_piercing_line(self, df):
        """Ligne perçante - Pattern haussier"""
        if len(df) < 2:
            return
        
        prev = df.iloc[-2]
        curr = df.iloc[-1]
        
        prev_body = prev['close'] - prev['open']
        curr_body = curr['close'] - curr['open']
        
        # Ligne perçante : prev rouge, curr verte qui clôture > 50% du corps précédent
        if (prev_body < 0 and curr_body > 0 and
            curr['open'] < prev['close'] and
            curr['close'] > prev['open'] + abs(prev_body) * 0.5):
            
            self.patterns_detected.append({
                'name': 'piercing_line',
                'type': 'bullish',
                'reliability': 75,
                'description': '🗡️ Ligne perçante - Signal haussier',
                'candle_index': len(df) - 1
            })
    
    def _check_dark_cloud_cover(self, df):
        """Couverture nuage noir - Pattern baissier"""
        if len(df) < 2:
            return
        
        prev = df.iloc[-2]
        curr = df.iloc[-1]
        
        prev_body = prev['close'] - prev['open']
        curr_body = curr['close'] - curr['open']
        
        # Couverture nuage : prev verte, curr rouge qui clôture < 50% du corps précédent
        if (prev_body > 0 and curr_body < 0 and
            curr['open'] > prev['close'] and
            curr['close'] < prev['open'] + prev_body * 0.5):
            
            self.patterns_detected.append({
                'name': 'dark_cloud_cover',
                'type': 'bearish',
                'reliability': 75,
                'description': '☁️ Couverture nuage noir - Signal baissier',
                'candle_index': len(df) - 1
            })
    
    def _check_harami(self, df):
        """Harami haussier/baissier"""
        if len(df) < 2:
            return
        
        prev = df.iloc[-2]
        curr = df.iloc[-1]
        
        prev_body = abs(prev['close'] - prev['open'])
        curr_body = abs(curr['close'] - curr['open'])
        
        # Harami : petite bougie contenue dans le corps de la précédente
        if curr_body < prev_body * 0.5:
            # Harami haussier : prev rouge, curr petite verte
            if prev['close'] < prev['open'] and curr['close'] > curr['open']:
                self.patterns_detected.append({
                    'name': 'bullish_harami',
                    'type': 'bullish',
                    'reliability': 70,
                    'description': '🤰 Harami haussier - Signal achat',
                    'candle_index': len(df) - 1
                })
            
            # Harami baissier : prev verte, curr petite rouge
            elif prev['close'] > prev['open'] and curr['close'] < curr['open']:
                self.patterns_detected.append({
                    'name': 'bearish_harami',
                    'type': 'bearish',
                    'reliability': 70,
                    'description': '🤰 Harami baissier - Signal vente',
                    'candle_index': len(df) - 1
                })
    
    # ═══════════════════════════════════════════════════════════
    # PATTERNS 3 BOUGIES
    # ═══════════════════════════════════════════════════════════
    
    def _check_morning_star(self, df):
        """Étoile du matin - Fort pattern haussier"""
        if len(df) < 3:
            return
        
        first = df.iloc[-3]
        second = df.iloc[-2]
        third = df.iloc[-1]
        
        first_body = first['close'] - first['open']
        second_body = abs(second['close'] - second['open'])
        third_body = third['close'] - third['open']
        
        # Étoile du matin : rouge, petit corps, verte
        if (first_body < 0 and  # 1ère rouge
            second_body < abs(first_body) * 0.3 and  # 2ème petit corps
            third_body > 0 and  # 3ème verte
            third['close'] > first['open'] + abs(first_body) * 0.5):  # Clôture > 50% de la 1ère
            
            self.patterns_detected.append({
                'name': 'morning_star',
                'type': 'bullish',
                'reliability': 90,
                'description': '⭐🌅 Étoile du matin - Très fort signal haussier',
                'candle_index': len(df) - 1
            })
    
    def _check_evening_star(self, df):
        """Étoile du soir - Fort pattern baissier"""
        if len(df) < 3:
            return
        
        first = df.iloc[-3]
        second = df.iloc[-2]
        third = df.iloc[-1]
        
        first_body = first['close'] - first['open']
        second_body = abs(second['close'] - second['open'])
        third_body = third['close'] - third['open']
        
        # Étoile du soir : verte, petit corps, rouge
        if (first_body > 0 and  # 1ère verte
            second_body < first_body * 0.3 and  # 2ème petit corps
            third_body < 0 and  # 3ème rouge
            third['close'] < first['open'] + first_body * 0.5):  # Clôture < 50% de la 1ère
            
            self.patterns_detected.append({
                'name': 'evening_star',
                'type': 'bearish',
                'reliability': 90,
                'description': '⭐🌆 Étoile du soir - Très fort signal baissier',
                'candle_index': len(df) - 1
            })
    
    def _check_three_soldiers(self, df):
        """Trois soldats blancs - Fort pattern haussier"""
        if len(df) < 3:
            return
        
        last_3 = df.tail(3)
        
        # Vérifie que toutes sont vertes et en progression
        all_green = all(candle['close'] > candle['open'] for _, candle in last_3.iterrows())
        ascending = (last_3.iloc[0]['close'] < last_3.iloc[1]['close'] < last_3.iloc[2]['close'])
        
        if all_green and ascending:
            self.patterns_detected.append({
                'name': 'three_white_soldiers',
                'type': 'bullish',
                'reliability': 85,
                'description': '🪖🪖🪖 Trois soldats blancs - Fort signal haussier',
                'candle_index': len(df) - 1
            })
    
    def _check_three_crows(self, df):
        """Trois corbeaux noirs - Fort pattern baissier"""
        if len(df) < 3:
            return
        
        last_3 = df.tail(3)
        
        # Vérifie que toutes sont rouges et en descente
        all_red = all(candle['close'] < candle['open'] for _, candle in last_3.iterrows())
        descending = (last_3.iloc[0]['close'] > last_3.iloc[1]['close'] > last_3.iloc[2]['close'])
        
        if all_red and descending:
            self.patterns_detected.append({
                'name': 'three_black_crows',
                'type': 'bearish',
                'reliability': 85,
                'description': '🦅🦅🦅 Trois corbeaux noirs - Fort signal baissier',
                'candle_index': len(df) - 1
            })
    
    def get_combined_score(self):
        """
        Calcule un score combiné de tous les patterns détectés
        
        Returns:
            dict: Scores buy/sell
        """
        buy_score = 0
        sell_score = 0
        
        for pattern in self.patterns_detected:
            if pattern['type'] == 'bullish':
                buy_score += pattern['reliability'] * 0.5  # Pondéré à 50%
            elif pattern['type'] == 'bearish':
                sell_score += pattern['reliability'] * 0.5
        
        return {
            'buy_score': min(buy_score, 100),
            'sell_score': min(sell_score, 100),
            'patterns': self.patterns_detected
        }
    
    def print_patterns(self):
        """Affiche les patterns de manière lisible"""
        if not self.patterns_detected:
            print("\n⚪ Aucun pattern détecté")
            return
        
        print("\n" + "="*60)
        print(f"🔍 PATTERNS DÉTECTÉS ({len(self.patterns_detected)})")
        print("="*60)
        
        for pattern in self.patterns_detected:
            emoji = "🟢" if pattern['type'] == 'bullish' else "🔴" if pattern['type'] == 'bearish' else "⚪"
            print(f"{emoji} {pattern['description']}")
            print(f"   Fiabilité: {pattern['reliability']}%")
        
        print("="*60)


# Test du module
if __name__ == "__main__":
    print("🚀 Test du Pattern Scanner")
    
    scanner = PatternScanner()
    
    print(f"\n✅ Pattern Scanner opérationnel")
    print(f"📊 {len(scanner.pattern_catalog)} patterns disponibles")
    print("🔍 Patterns haussiers, baissiers et neutres")
