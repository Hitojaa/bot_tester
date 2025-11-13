# feature_extractor.py - Extraction standardisée de features pour ML

"""
Feature Extractor pour APEX ML System

Responsabilités:
- Extraire 28 features standardisées depuis un DataFrame avec indicateurs
- Gérer les valeurs manquantes (forward fill, mean, zero)
- Normaliser les features (minmax ou standard)
- Valider la cohérence et détecter les anomalies
- Retourner un vecteur numpy prêt pour n'importe quel modèle ML

Architecture:
- Input: DataFrame pandas avec tous les indicateurs calculés
- Output: numpy array de shape (FEATURE_COUNT,) ou (n_samples, FEATURE_COUNT)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import ml_config as ml_config
from logger_apex import get_logger

class FeatureExtractor:
    """
    Extracteur de features standardisé pour le système ML

    V1.0: 28 features extraites et normalisées
    """

    def __init__(self):
        """Initialise l'extracteur de features"""
        self.logger = get_logger()
        self.feature_names = ml_config.FEATURE_NAMES
        self.feature_count = ml_config.FEATURE_COUNT

        # Stats pour normalisation (calculées sur dataset training)
        self.feature_min = {}
        self.feature_max = {}
        self.feature_mean = {}
        self.feature_std = {}

        self.is_fitted = False

        self.logger.info("✅ FeatureExtractor initialisé")

    def extract_features(self, df: pd.DataFrame, support_resistance: Optional[Dict] = None) -> Optional[np.ndarray]:
        """
        Extrait les features depuis un DataFrame avec indicateurs

        Args:
            df: DataFrame pandas avec colonnes: open, high, low, close, volume + tous les indicateurs
            support_resistance: Dict avec 'support' et 'resistance' (optionnel)

        Returns:
            numpy array de shape (FEATURE_COUNT,) ou None si erreur
        """
        try:
            if df is None or len(df) < 20:
                self.logger.warning("DataFrame insuffisant pour extraction de features")
                return None

            features = {}

            # Dernière bougie
            last_idx = len(df) - 1
            current = df.iloc[last_idx]
            prev_5 = df.iloc[max(0, last_idx - 5)]
            prev_15 = df.iloc[max(0, last_idx - 15)]

            current_price = current['close']

            # ═══════════════════════════════════════════════════════════
            # 1. PRIX ET VARIATIONS (4 features)
            # ═══════════════════════════════════════════════════════════
            features['price_pct_change_1'] = self._safe_pct_change(df, last_idx, 1)
            features['price_pct_change_5'] = self._safe_pct_change(df, last_idx, 5)
            features['price_pct_change_15'] = self._safe_pct_change(df, last_idx, 15)
            features['high_low_ratio'] = (current['high'] - current['low']) / current['close'] if current['close'] > 0 else 0

            # ═══════════════════════════════════════════════════════════
            # 2. EMA RELATIVES (4 features)
            # ═══════════════════════════════════════════════════════════
            features['price_vs_ema9'] = self._safe_relative_diff(current_price, current.get('ema_fast'))
            features['price_vs_ema20'] = self._safe_relative_diff(current_price, current.get('ema_medium'))
            features['price_vs_ema50'] = self._safe_relative_diff(current_price, current.get('ema_slow'))
            features['price_vs_ema200'] = self._safe_relative_diff(current_price, current.get('ema_trend'))

            # ═══════════════════════════════════════════════════════════
            # 3. OSCILLATEURS (6 features)
            # ═══════════════════════════════════════════════════════════
            features['rsi'] = current.get('rsi', 50)  # Défaut neutre
            features['rsi_trend'] = current.get('rsi', 50) - prev_5.get('rsi', 50)
            features['macd'] = current.get('macd', 0)
            features['macd_signal'] = current.get('macd_signal', 0)
            features['macd_diff'] = features['macd'] - features['macd_signal']
            features['stoch_k'] = current.get('stoch_k', 50)

            # ═══════════════════════════════════════════════════════════
            # 4. VOLATILITÉ (3 features)
            # ═══════════════════════════════════════════════════════════
            atr = current.get('atr', 0)
            features['atr_normalized'] = atr / current_price if current_price > 0 else 0

            bb_lower = current.get('bb_lower', current_price)
            bb_upper = current.get('bb_upper', current_price)
            bb_range = bb_upper - bb_lower
            features['bb_position'] = (current_price - bb_lower) / bb_range if bb_range > 0 else 0.5
            features['bb_width'] = bb_range / current_price if current_price > 0 else 0

            # ═══════════════════════════════════════════════════════════
            # 5. VOLUME (3 features)
            # ═══════════════════════════════════════════════════════════
            avg_volume = df['volume'].rolling(window=20, min_periods=1).mean().iloc[last_idx]
            features['volume_ratio'] = current['volume'] / avg_volume if avg_volume > 0 else 1.0
            features['volume_trend'] = current['volume'] - prev_5['volume']

            # OBV (On-Balance Volume)
            obv_current = self._calculate_obv(df, last_idx)
            obv_prev = self._calculate_obv(df, max(0, last_idx - 10))
            features['obv_trend'] = obv_current - obv_prev

            # ═══════════════════════════════════════════════════════════
            # 6. SUPPORT/RÉSISTANCE (4 features)
            # ═══════════════════════════════════════════════════════════
            if support_resistance and 'support' in support_resistance and 'resistance' in support_resistance:
                support = support_resistance['support']
                resistance = support_resistance['resistance']

                features['distance_to_support'] = (current_price - support) / current_price if support else 0
                features['distance_to_resistance'] = (resistance - current_price) / current_price if resistance else 0

                # Force des niveaux (score 0-1, basé sur proximité)
                features['support_strength'] = self._calculate_level_strength(current_price, support)
                features['resistance_strength'] = self._calculate_level_strength(current_price, resistance)
            else:
                features['distance_to_support'] = 0
                features['distance_to_resistance'] = 0
                features['support_strength'] = 0
                features['resistance_strength'] = 0

            # ═══════════════════════════════════════════════════════════
            # 7. AUTRES INDICATEURS (4 features)
            # ═══════════════════════════════════════════════════════════
            supertrend = current.get('supertrend', 0)
            features['supertrend_signal'] = 1 if supertrend > 0 else -1 if supertrend < 0 else 0

            vwap = current.get('vwap', current_price)
            features['vwap_deviation'] = (current_price - vwap) / current_price if current_price > 0 else 0

            # Momentum
            features['momentum_short'] = self._calculate_momentum(df, last_idx, 5)
            features['momentum_long'] = self._calculate_momentum(df, last_idx, 15)

            # ═══════════════════════════════════════════════════════════
            # VALIDATION & CONVERSION
            # ═══════════════════════════════════════════════════════════
            feature_vector = self._features_dict_to_array(features)

            # Gère les NaN
            feature_vector = self._handle_missing_values(feature_vector)

            # Normalise si fitted
            if self.is_fitted and ml_config.NORMALIZE_FEATURES:
                feature_vector = self._normalize(feature_vector)

            return feature_vector

        except Exception as e:
            self.logger.error(f"Erreur extraction features: {e}")
            return None

    def _features_dict_to_array(self, features: Dict) -> np.ndarray:
        """Convertit le dict de features en array numpy dans l'ordre strict"""
        feature_list = []
        for name in self.feature_names:
            value = features.get(name, 0.0)  # Défaut 0 si manquant
            feature_list.append(float(value))
        return np.array(feature_list, dtype=np.float32)

    def _safe_pct_change(self, df: pd.DataFrame, idx: int, periods: int) -> float:
        """Calcule la variation en % de manière sûre"""
        if idx < periods:
            return 0.0
        prev_price = df.iloc[idx - periods]['close']
        curr_price = df.iloc[idx]['close']
        if prev_price == 0:
            return 0.0
        return (curr_price - prev_price) / prev_price

    def _safe_relative_diff(self, price: float, reference: Optional[float]) -> float:
        """Calcule (price - ref) / price de manière sûre"""
        if reference is None or price == 0:
            return 0.0
        return (price - reference) / price

    def _calculate_obv(self, df: pd.DataFrame, idx: int) -> float:
        """Calcule On-Balance Volume jusqu'à idx"""
        if idx < 0 or idx >= len(df):
            return 0.0
        obv = 0
        for i in range(1, min(idx + 1, len(df))):
            if df.iloc[i]['close'] > df.iloc[i-1]['close']:
                obv += df.iloc[i]['volume']
            elif df.iloc[i]['close'] < df.iloc[i-1]['close']:
                obv -= df.iloc[i]['volume']
        return obv

    def _calculate_level_strength(self, price: float, level: Optional[float]) -> float:
        """
        Calcule la force d'un niveau S/R (0-1)
        Plus le prix est proche, plus la force est élevée
        """
        if level is None or level == 0:
            return 0.0
        distance_pct = abs(price - level) / price
        # Force = 1 si distance < 0.5%, décroît exponentiellement
        strength = np.exp(-distance_pct * 200)  # Décroissance rapide
        return min(strength, 1.0)

    def _calculate_momentum(self, df: pd.DataFrame, idx: int, periods: int) -> float:
        """Calcule le momentum sur N périodes"""
        if idx < periods:
            return 0.0
        return df.iloc[idx]['close'] - df.iloc[idx - periods]['close']

    def _handle_missing_values(self, features: np.ndarray) -> np.ndarray:
        """Gère les valeurs manquantes (NaN, inf)"""
        # Remplace inf par des valeurs raisonnables
        features = np.where(np.isinf(features), 0, features)

        # Remplace NaN selon la méthode configurée
        if np.isnan(features).any():
            method = ml_config.FILL_NA_METHOD
            if method == "zero":
                features = np.nan_to_num(features, nan=0.0)
            elif method == "mean" and self.is_fitted:
                for i, val in enumerate(features):
                    if np.isnan(val):
                        features[i] = self.feature_mean.get(self.feature_names[i], 0.0)
            else:  # forward ou défaut
                features = np.nan_to_num(features, nan=0.0)

        return features

    def _normalize(self, features: np.ndarray) -> np.ndarray:
        """Normalise les features selon la méthode configurée"""
        if not self.is_fitted:
            return features

        method = ml_config.NORMALIZATION_METHOD
        normalized = np.zeros_like(features)

        for i, name in enumerate(self.feature_names):
            value = features[i]

            if method == "minmax":
                min_val = self.feature_min.get(name, value)
                max_val = self.feature_max.get(name, value)
                if max_val - min_val > 0:
                    normalized[i] = (value - min_val) / (max_val - min_val)
                else:
                    normalized[i] = 0.5
            elif method == "standard":
                mean = self.feature_mean.get(name, 0)
                std = self.feature_std.get(name, 1)
                if std > 0:
                    normalized[i] = (value - mean) / std
                else:
                    normalized[i] = 0

        return normalized

    def fit(self, feature_matrix: np.ndarray):
        """
        Calcule les statistiques de normalisation sur un dataset d'entraînement

        Args:
            feature_matrix: Array de shape (n_samples, FEATURE_COUNT)
        """
        if feature_matrix.shape[1] != self.feature_count:
            raise ValueError(f"Feature matrix doit avoir {self.feature_count} colonnes")

        for i, name in enumerate(self.feature_names):
            column = feature_matrix[:, i]
            self.feature_min[name] = np.min(column)
            self.feature_max[name] = np.max(column)
            self.feature_mean[name] = np.mean(column)
            self.feature_std[name] = np.std(column)

        self.is_fitted = True
        self.logger.info(f"✅ FeatureExtractor fitted sur {len(feature_matrix)} samples")

    def get_feature_names(self) -> List[str]:
        """Retourne la liste des noms de features"""
        return self.feature_names.copy()


# Test du module
if __name__ == "__main__":
    print("🧠 Test Feature Extractor")

    extractor = FeatureExtractor()
    print(f"✅ {extractor.feature_count} features configurées:")
    for i, name in enumerate(extractor.get_feature_names(), 1):
        print(f"   {i:2d}. {name}")

    # Test avec données simulées
    test_df = pd.DataFrame({
        'open': [100, 101, 102],
        'high': [102, 103, 104],
        'low': [99, 100, 101],
        'close': [101, 102, 103],
        'volume': [1000, 1100, 1200],
        'rsi': [45, 50, 55],
        'macd': [-1, 0, 1],
        'macd_signal': [-0.5, 0, 0.5],
        'ema_fast': [100, 101, 102],
        'ema_medium': [99, 100, 101],
    })

    features = extractor.extract_features(test_df)
    if features is not None:
        print(f"\n✅ Features extraites: shape {features.shape}")
        print(f"   Exemple: {features[:5]}")
    else:
        print("❌ Échec extraction features")
