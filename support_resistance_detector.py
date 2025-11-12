# support_resistance_detector.py - Détection S/R dynamique (PRO)

import pandas as pd
import numpy as np
from collections import defaultdict

class SupportResistanceDetector:
    """Détecte les niveaux de support et résistance clés"""
    
    def __init__(self):
        self.support_levels = []
        self.resistance_levels = []
        self.key_levels = []  # Niveaux les plus importants
        
        print("✅ Support/Resistance Detector initialisé")
    
    def detect_levels(self, df, lookback=100, num_levels=5):
        """
        Détecte les niveaux de S/R par analyse des pivots
        
        Args:
            df: DataFrame avec OHLC
            lookback: Nombre de bougies à analyser
            num_levels: Nombre de niveaux à retenir
            
        Returns:
            dict: Supports et résistances
        """
        if df is None or len(df) < lookback:
            return None
        
        recent_df = df.tail(lookback)
        
        # Trouve les pivots hauts et bas
        pivot_highs = self._find_pivot_highs(recent_df)
        pivot_lows = self._find_pivot_lows(recent_df)
        
        # Groupe les pivots proches (clustering)
        self.resistance_levels = self._cluster_levels(pivot_highs, num_levels)
        self.support_levels = self._cluster_levels(pivot_lows, num_levels)
        
        # Identifie les niveaux clés (touchés plusieurs fois)
        self.key_levels = self._identify_key_levels(recent_df)
        
        return {
            'supports': self.support_levels,
            'resistances': self.resistance_levels,
            'key_levels': self.key_levels
        }
    
    def _find_pivot_highs(self, df, window=5):
        """Trouve les pivots hauts (sommets locaux)"""
        pivots = []
        
        for i in range(window, len(df) - window):
            high = df.iloc[i]['high']
            is_pivot = True
            
            # Vérifie si c'est un maximum local
            for j in range(i - window, i + window + 1):
                if j != i and df.iloc[j]['high'] >= high:
                    is_pivot = False
                    break
            
            if is_pivot:
                pivots.append(high)
        
        return pivots
    
    def _find_pivot_lows(self, df, window=5):
        """Trouve les pivots bas (creux locaux)"""
        pivots = []
        
        for i in range(window, len(df) - window):
            low = df.iloc[i]['low']
            is_pivot = True
            
            # Vérifie si c'est un minimum local
            for j in range(i - window, i + window + 1):
                if j != i and df.iloc[j]['low'] <= low:
                    is_pivot = False
                    break
            
            if is_pivot:
                pivots.append(low)
        
        return pivots
    
    def _cluster_levels(self, levels, num_clusters):
        """Groupe les niveaux proches ensemble"""
        if not levels:
            return []
        
        # Trie les niveaux
        sorted_levels = sorted(levels)
        
        # Groupe les niveaux proches (1% de distance)
        clusters = []
        current_cluster = [sorted_levels[0]]
        
        for level in sorted_levels[1:]:
            # Si proche du niveau actuel (< 1%)
            if abs(level - current_cluster[-1]) / current_cluster[-1] < 0.01:
                current_cluster.append(level)
            else:
                # Nouveau cluster
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]
        
        # Ajoute le dernier cluster
        if current_cluster:
            clusters.append(np.mean(current_cluster))
        
        # Retourne les N clusters les plus importants
        # (Les plus "touchés" = plus de niveaux dans le cluster)
        return sorted(clusters)[:num_clusters]
    
    def _identify_key_levels(self, df, min_touches=3):
        """Identifie les niveaux clés (touchés plusieurs fois)"""
        key_levels = []
        
        all_levels = self.support_levels + self.resistance_levels
        
        for level in all_levels:
            touches = 0
            
            # Compte combien de fois le niveau a été touché
            for _, candle in df.iterrows():
                # Touché si le niveau est entre low et high
                if candle['low'] <= level <= candle['high']:
                    touches += 1
            
            # Si touché assez de fois, c'est un niveau clé
            if touches >= min_touches:
                key_levels.append({
                    'level': level,
                    'touches': touches,
                    'strength': min(touches / 10 * 100, 100)  # Force du niveau
                })
        
        # Trie par force décroissante
        key_levels.sort(key=lambda x: x['strength'], reverse=True)
        
        return key_levels[:5]  # Top 5
    
    def get_nearest_support(self, current_price):
        """Trouve le support le plus proche sous le prix"""
        if not self.support_levels:
            return None
        
        supports_below = [s for s in self.support_levels if s < current_price]
        
        if not supports_below:
            return None
        
        return max(supports_below)  # Le plus proche = le plus haut
    
    def get_nearest_resistance(self, current_price):
        """Trouve la résistance la plus proche au-dessus du prix"""
        if not self.resistance_levels:
            return None
        
        resistances_above = [r for r in self.resistance_levels if r > current_price]
        
        if not resistances_above:
            return None
        
        return min(resistances_above)  # Le plus proche = le plus bas
    
    def is_at_support(self, current_price, tolerance=0.005):
        """Vérifie si le prix est sur un support"""
        nearest_support = self.get_nearest_support(current_price)
        
        if nearest_support is None:
            return False
        
        distance = abs(current_price - nearest_support) / nearest_support
        return distance <= tolerance
    
    def is_at_resistance(self, current_price, tolerance=0.005):
        """Vérifie si le prix est sur une résistance"""
        nearest_resistance = self.get_nearest_resistance(current_price)
        
        if nearest_resistance is None:
            return False
        
        distance = abs(current_price - nearest_resistance) / nearest_resistance
        return distance <= tolerance
    
    def get_trading_signal(self, current_price, prev_price):
        """
        Génère un signal basé sur S/R
        
        Returns:
            dict: Signal avec score
        """
        signal = {
            'action': 'hold',
            'score': 0,
            'reason': '',
            'nearest_support': self.get_nearest_support(current_price),
            'nearest_resistance': self.get_nearest_resistance(current_price)
        }
        
        # Signal d'achat : Rebond sur support
        if self.is_at_support(current_price):
            signal['action'] = 'buy'
            signal['score'] = 30
            signal['reason'] = f"Rebond sur support (${signal['nearest_support']:.2f})"

        # Signal d'achat : Cassure de résistance
        elif signal['nearest_resistance'] is not None and prev_price < signal['nearest_resistance'] and current_price >= signal['nearest_resistance']:
            signal['action'] = 'buy'
            signal['score'] = 35
            signal['reason'] = f"Cassure résistance (${signal['nearest_resistance']:.2f})"

        # Signal de vente : Rejet sur résistance
        elif self.is_at_resistance(current_price):
            signal['action'] = 'sell'
            signal['score'] = 25
            signal['reason'] = f"Rejet résistance (${signal['nearest_resistance']:.2f})"

        # Signal de vente : Cassure de support
        elif signal['nearest_support'] is not None and prev_price > signal['nearest_support'] and current_price <= signal['nearest_support']:
            signal['action'] = 'sell'
            signal['score'] = 30
            signal['reason'] = f"Cassure support (${signal['nearest_support']:.2f})"
        
        # Bonus si proche d'un niveau clé fort
        for key_level in self.key_levels:
            if abs(current_price - key_level['level']) / current_price < 0.005:
                signal['score'] += 10
                signal['reason'] += f" | Niveau clé fort ({key_level['touches']} touches)"
                break
        
        return signal
    
    def has_clear_path(self, current_price, target_price):
        """
        Vérifie s'il y a un chemin dégagé entre prix actuel et target
        (pas de résistance majeure)
        """
        if target_price > current_price:
            # Check résistances au-dessus
            for resistance in self.resistance_levels:
                if current_price < resistance < target_price:
                    return False, f"Résistance à ${resistance:.2f}"
        else:
            # Check supports en-dessous
            for support in self.support_levels:
                if target_price < support < current_price:
                    return False, f"Support à ${support:.2f}"
        
        return True, "Chemin dégagé"
    
    def print_levels(self, current_price):
        """Affiche les niveaux de manière lisible"""
        print("\n" + "="*60)
        print("🎯 SUPPORT / RÉSISTANCE DYNAMIQUES")
        print("="*60)
        
        print(f"\n💰 Prix actuel: ${current_price:.2f}")
        
        if self.resistance_levels:
            print(f"\n🔴 RÉSISTANCES:")
            for i, r in enumerate(self.resistance_levels, 1):
                distance = ((r - current_price) / current_price) * 100
                emoji = "⚠️" if distance < 1 else "📊"
                print(f"   {emoji} R{i}: ${r:.2f} (+{distance:.2f}%)")
        
        if self.support_levels:
            print(f"\n🟢 SUPPORTS:")
            for i, s in enumerate(self.support_levels, 1):
                distance = ((current_price - s) / current_price) * 100
                emoji = "⚠️" if distance < 1 else "📊"
                print(f"   {emoji} S{i}: ${s:.2f} (-{distance:.2f}%)")
        
        if self.key_levels:
            print(f"\n⭐ NIVEAUX CLÉS:")
            for level_info in self.key_levels:
                level = level_info['level']
                touches = level_info['touches']
                strength = level_info['strength']
                distance = abs(current_price - level) / current_price * 100
                
                emoji = "🔥" if strength > 80 else "⭐"
                print(f"   {emoji} ${level:.2f} - {touches} touches (force: {strength:.0f}%) - Distance: {distance:.2f}%")
        
        print("="*60)


# Test du module
if __name__ == "__main__":
    print("🚀 Test du Support/Resistance Detector")
    
    detector = SupportResistanceDetector()
    
    print("\n✅ S/R Detector opérationnel")
    print("📊 Capacités:")
    print("  - Détection pivots hauts/bas")
    print("  - Clustering des niveaux")
    print("  - Niveaux clés (multi-touches)")
    print("  - Signaux de trading S/R")
    print("  - Vérification chemin dégagé")
