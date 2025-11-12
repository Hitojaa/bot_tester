# volume_profile_engine.py - Analyse Volume Profile + VWAP (PRO)

import pandas as pd
import numpy as np
import config_apex as config

class VolumeProfileEngine:
    """Analyse du Volume Profile et VWAP comme les traders PRO"""
    
    def __init__(self):
        self.vwap = None
        self.volume_profile = {}
        self.poc = None  # Point of Control (prix avec le plus de volume)
        self.value_area_high = None
        self.value_area_low = None
        
        print("✅ Volume Profile Engine initialisé")
    
    def calculate_vwap(self, df):
        """
        Calcule le VWAP (Volume Weighted Average Price)
        Prix moyen pondéré par le volume - niveau clé pour les institutions
        
        Returns:
            float: VWAP actuel
        """
        if df is None or len(df) < 2:
            return None
        
        # VWAP = Σ(Prix typique × Volume) / Σ(Volume)
        # Prix typique = (High + Low + Close) / 3
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        
        # Calcul cumulatif
        cumulative_tp_volume = (typical_price * df['volume']).cumsum()
        cumulative_volume = df['volume'].cumsum()
        
        # VWAP
        vwap = cumulative_tp_volume / cumulative_volume
        
        self.vwap = vwap.iloc[-1]
        
        # Ajoute au DataFrame
        df['vwap'] = vwap
        
        return self.vwap
    
    def calculate_volume_profile(self, df, price_bins=50):
        """
        Calcule le Volume Profile
        Distribution du volume à différents niveaux de prix
        
        Args:
            df: DataFrame avec OHLCV
            price_bins: Nombre de niveaux de prix
            
        Returns:
            dict: Volume profile data
        """
        if df is None or len(df) < config.VOLUME_PROFILE_PERIODS:
            return None
        
        # Prend les dernières bougies
        recent_df = df.tail(config.VOLUME_PROFILE_PERIODS)
        
        # Définit les bins de prix
        price_min = recent_df['low'].min()
        price_max = recent_df['high'].max()
        
        bins = np.linspace(price_min, price_max, price_bins)
        
        # Calcule le volume à chaque niveau de prix
        volume_at_price = {}
        
        for _, candle in recent_df.iterrows():
            # Pour chaque bougie, distribue le volume entre high et low
            candle_range = candle['high'] - candle['low']
            if candle_range == 0:
                continue
            
            # Trouve les bins concernés
            for i in range(len(bins) - 1):
                bin_low = bins[i]
                bin_high = bins[i + 1]
                bin_mid = (bin_low + bin_high) / 2
                
                # Si le bin intersecte la bougie
                if bin_high >= candle['low'] and bin_low <= candle['high']:
                    # Calcule la proportion du volume
                    overlap_low = max(bin_low, candle['low'])
                    overlap_high = min(bin_high, candle['high'])
                    overlap_range = overlap_high - overlap_low
                    
                    volume_proportion = overlap_range / candle_range
                    volume_in_bin = candle['volume'] * volume_proportion
                    
                    if bin_mid in volume_at_price:
                        volume_at_price[bin_mid] += volume_in_bin
                    else:
                        volume_at_price[bin_mid] = volume_in_bin
        
        self.volume_profile = volume_at_price
        
        # Trouve le Point of Control (POC) - prix avec le plus de volume
        if volume_at_price:
            self.poc = max(volume_at_price, key=volume_at_price.get)
        
        # Calcule la Value Area (zone où 70% du volume s'est échangé)
        self._calculate_value_area(volume_at_price)
        
        return {
            'volume_profile': volume_at_price,
            'poc': self.poc,
            'value_area_high': self.value_area_high,
            'value_area_low': self.value_area_low
        }
    
    def _calculate_value_area(self, volume_at_price):
        """Calcule la Value Area (70% du volume)"""
        if not volume_at_price:
            return
        
        # Trie par volume décroissant
        sorted_prices = sorted(volume_at_price.items(), key=lambda x: x[1], reverse=True)
        
        total_volume = sum(volume_at_price.values())
        target_volume = total_volume * 0.70
        
        # Prend les prix jusqu'à 70% du volume
        cumulative_volume = 0
        value_area_prices = []
        
        for price, volume in sorted_prices:
            cumulative_volume += volume
            value_area_prices.append(price)
            
            if cumulative_volume >= target_volume:
                break
        
        if value_area_prices:
            self.value_area_high = max(value_area_prices)
            self.value_area_low = min(value_area_prices)
    
    def is_price_in_value_area(self, price):
        """Vérifie si le prix est dans la Value Area"""
        if self.value_area_low is None or self.value_area_high is None:
            return False
        
        return self.value_area_low <= price <= self.value_area_high
    
    def get_vwap_deviation(self, current_price):
        """
        Calcule l'écart par rapport au VWAP
        
        Returns:
            float: % d'écart (positif = au-dessus, négatif = en-dessous)
        """
        if self.vwap is None:
            return 0
        
        deviation = (current_price - self.vwap) / self.vwap
        return deviation
    
    def is_near_vwap(self, current_price, threshold=None):
        """Vérifie si le prix est proche du VWAP"""
        if threshold is None:
            threshold = config.VWAP_DEVIATION_THRESHOLD
        
        deviation = abs(self.get_vwap_deviation(current_price))
        return deviation <= threshold
    
    def get_vwap_signal(self, current_price, prev_price):
        """
        Génère un signal basé sur VWAP
        
        Returns:
            dict: Signal avec score
        """
        if self.vwap is None:
            return {'action': 'hold', 'score': 0, 'reason': 'VWAP non calculé'}
        
        deviation = self.get_vwap_deviation(current_price)
        
        signal = {
            'action': 'hold',
            'score': 0,
            'reason': '',
            'vwap': self.vwap,
            'deviation': deviation * 100
        }
        
        # Signal d'achat : Prix revient vers VWAP depuis le bas
        if prev_price < self.vwap and current_price >= self.vwap:
            signal['action'] = 'buy'
            signal['score'] = 25
            signal['reason'] = f"Prix croise VWAP à la hausse (VWAP: ${self.vwap:.2f})"
        
        # Signal d'achat : Prix rebondit sur VWAP
        elif self.is_near_vwap(current_price) and current_price < self.vwap:
            signal['action'] = 'buy'
            signal['score'] = 20
            signal['reason'] = f"Prix proche VWAP en support (écart: {deviation*100:.2f}%)"
        
        # Signal de vente : Prix s'éloigne trop du VWAP (surachat)
        elif deviation > 0.01:  # +1% au-dessus
            signal['action'] = 'sell'
            signal['score'] = 15
            signal['reason'] = f"Prix trop éloigné VWAP (+{deviation*100:.2f}%)"
        
        return signal
    
    def get_volume_profile_signal(self, current_price):
        """
        Génère un signal basé sur Volume Profile
        
        Returns:
            dict: Signal avec score
        """
        if not self.volume_profile or self.poc is None:
            return {'action': 'hold', 'score': 0, 'reason': 'Volume Profile non calculé'}
        
        signal = {
            'action': 'hold',
            'score': 0,
            'reason': '',
            'poc': self.poc,
            'in_value_area': self.is_price_in_value_area(current_price)
        }
        
        # Distance au POC
        distance_to_poc = abs(current_price - self.poc) / self.poc
        
        # Signal fort si prix proche du POC (zone de haute liquidité)
        if distance_to_poc < 0.005:  # 0.5%
            signal['score'] = 20
            signal['reason'] = f"Prix proche POC (${self.poc:.2f}) - Zone de liquidité"
        
        # Signal si prix dans la Value Area
        if self.is_price_in_value_area(current_price):
            signal['score'] += 15
            signal['reason'] += " | Dans Value Area"
        
        # Signal d'achat si prix sous la Value Area (potentiel retour)
        elif current_price < self.value_area_low:
            signal['action'] = 'buy'
            signal['score'] = 25
            signal['reason'] = f"Prix sous Value Area (${self.value_area_low:.2f}) - Potentiel retour"
        
        # Signal de vente si prix au-dessus Value Area
        elif current_price > self.value_area_high:
            signal['action'] = 'sell'
            signal['score'] = 20
            signal['reason'] = f"Prix au-dessus Value Area (${self.value_area_high:.2f}) - Surachat"
        
        return signal
    
    def analyze_complete(self, df, current_price, prev_price):
        """
        Analyse complète Volume Profile + VWAP
        
        Returns:
            dict: Analyse combinée
        """
        # Calcule VWAP
        self.calculate_vwap(df)
        
        # Calcule Volume Profile
        self.calculate_volume_profile(df)
        
        # Signaux
        vwap_signal = self.get_vwap_signal(current_price, prev_price)
        vp_signal = self.get_volume_profile_signal(current_price)
        
        # Combine les scores
        combined_score = vwap_signal['score'] + vp_signal['score']
        
        # Détermine l'action
        if vwap_signal['action'] == 'buy' or vp_signal['action'] == 'buy':
            action = 'buy'
        elif vwap_signal['action'] == 'sell' or vp_signal['action'] == 'sell':
            action = 'sell'
        else:
            action = 'hold'
        
        return {
            'action': action,
            'score': min(combined_score, 50),  # Max 50 points
            'vwap': self.vwap,
            'poc': self.poc,
            'value_area_high': self.value_area_high,
            'value_area_low': self.value_area_low,
            'vwap_signal': vwap_signal,
            'vp_signal': vp_signal,
            'in_value_area': self.is_price_in_value_area(current_price)
        }
    
    def print_analysis(self, analysis):
        """Affiche l'analyse de manière lisible"""
        if not analysis:
            return
        
        print("\n" + "="*60)
        print("📊 ANALYSE VOLUME PROFILE + VWAP")
        print("="*60)
        
        if analysis['vwap']:
            print(f"💧 VWAP: ${analysis['vwap']:.2f}")
            print(f"   {analysis['vwap_signal']['reason']}")
        
        if analysis['poc']:
            print(f"\n🎯 POC (Point of Control): ${analysis['poc']:.2f}")
            print(f"📊 Value Area: ${analysis['value_area_low']:.2f} - ${analysis['value_area_high']:.2f}")
            print(f"   {'✅ Prix dans Value Area' if analysis['in_value_area'] else '⚠️ Prix hors Value Area'}")
            print(f"   {analysis['vp_signal']['reason']}")
        
        print(f"\n🎯 Score combiné: {analysis['score']}/50")
        print(f"📊 Action suggérée: {analysis['action'].upper()}")
        print("="*60)


# Test du module
if __name__ == "__main__":
    print("🚀 Test du Volume Profile Engine")
    
    engine = VolumeProfileEngine()
    
    print("\n✅ Volume Profile Engine opérationnel")
    print("📊 Capacités:")
    print("  - VWAP en temps réel")
    print("  - Volume Profile (distribution)")
    print("  - POC (Point of Control)")
    print("  - Value Area (70% volume)")
    print("  - Signaux de trading")
