# dataset_builder.py - Construction de datasets pour entraînement ML

"""
Dataset Builder pour APEX ML System

Responsabilités:
- Récupérer un historique massif de bougies (50k+)
- Calculer tous les indicateurs sur l'historique
- Extraire les features standardisées
- Labelliser chaque sample (WIN/LOSS basé sur TP/SL virtuel)
- Sauvegarder le dataset au format CSV/pickle

Usage:
    python dataset_builder.py --symbol ETH/USDT --timeframe 1m --limit 50000
    python dataset_builder.py --multi BTC/USDT,ETH/USDT,BNB/USDT --limit 20000
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import ml_config as ml_config
from feature_extractor import FeatureExtractor
from logger_apex import get_logger
from data_collector_apex import DataCollectorApex
from indicators_advanced import AdvancedIndicators
from support_resistance_detector import SupportResistanceDetector
import os
from datetime import datetime
import pickle
import time

class DatasetBuilder:
    """
    Constructeur de datasets pour ML

    V2.0: Complet avec fetch + labellisation TP/SL + multi-crypto
    """

    def __init__(self):
        """Initialise le builder"""
        self.logger = get_logger()
        self.feature_extractor = FeatureExtractor()
        self.data_collector = DataCollectorApex()
        self.indicators = AdvancedIndicators()
        self.sr_detector = SupportResistanceDetector()

        # Créer le dossier datasets
        if not os.path.exists(ml_config.DATASET_OUTPUT_DIR):
            os.makedirs(ml_config.DATASET_OUTPUT_DIR)

        self.logger.info("✅ DatasetBuilder initialisé")

    def build_dataset(self, symbol: str, timeframe: str, limit: int = 50000) -> Optional[str]:
        """
        Construit un dataset complet pour UN symbole

        Args:
            symbol: Symbole (ex: ETH/USDT)
            timeframe: Timeframe (ex: 1m)
            limit: Nombre de bougies à récupérer

        Returns:
            Chemin vers le fichier dataset créé, ou None si erreur
        """
        self.logger.info(f"🔨 Construction dataset: {symbol} {timeframe} ({limit} bougies)")
        print(f"\n{'='*70}")
        print(f"🔨 CONSTRUCTION DATASET".center(70))
        print(f"{'='*70}")
        print(f"\n📊 Symbole: {symbol}")
        print(f"⏱️  Timeframe: {timeframe}")
        print(f"📈 Bougies: {limit}")

        # 1. FETCH DATA
        print(f"\n[1/5] 📥 Téléchargement données historiques...")
        df = self._fetch_historical_data(symbol, timeframe, limit)
        if df is None or len(df) < 500:
            print(f"❌ Données insuffisantes")
            return None
        print(f"✅ {len(df)} bougies téléchargées")

        # 2. CALCULATE INDICATORS
        print(f"\n[2/5] 🧮 Calcul indicateurs techniques...")
        df = self._calculate_all_indicators(df)
        if df is None:
            print(f"❌ Erreur calcul indicateurs")
            return None
        print(f"✅ Indicateurs calculés")

        # 3. EXTRACT FEATURES
        print(f"\n[3/5] 🔬 Extraction features ML...")
        features_list, valid_indices = self._extract_features_batch(df)
        if len(features_list) == 0:
            print(f"❌ Aucune feature extraite")
            return None
        print(f"✅ {len(features_list)} features extraites")

        # 4. LABELIZE
        print(f"\n[4/5] 🏷️  Labellisation TP/SL...")
        labels_list = self._labelize_batch(df, valid_indices)
        print(f"✅ {len([l for l in labels_list if l != -1])} samples labellisés")

        # Filtre les samples non labellisés
        valid_samples = [(f, l) for f, l in zip(features_list, labels_list) if l != -1]
        if len(valid_samples) < ml_config.DATASET_MIN_SIZE:
            print(f"❌ Dataset trop petit ({len(valid_samples)} < {ml_config.DATASET_MIN_SIZE})")
            return None

        features_array = np.array([s[0] for s in valid_samples])
        labels_array = np.array([s[1] for s in valid_samples])

        # 5. SAVE
        print(f"\n[5/5] 💾 Sauvegarde dataset...")
        filename = self._save_dataset(features_array, labels_array, symbol, timeframe)
        if filename:
            print(f"✅ Dataset sauvegardé: {filename}")
            self._print_dataset_stats(features_array, labels_array)
            return filename
        else:
            print(f"❌ Erreur sauvegarde")
            return None

    def build_multi_dataset(self, symbols: List[str], timeframe: str, limit_per_symbol: int = 20000) -> Optional[str]:
        """
        Construit un dataset MULTI-CRYPTO (combine plusieurs symboles)

        Args:
            symbols: Liste de symboles (ex: ['ETH/USDT', 'BTC/USDT', 'BNB/USDT'])
            timeframe: Timeframe
            limit_per_symbol: Bougies par symbole

        Returns:
            Chemin vers le fichier dataset créé
        """
        print(f"\n{'='*70}")
        print(f"🌍 CONSTRUCTION DATASET MULTI-CRYPTO".center(70))
        print(f"{'='*70}")
        print(f"\n🪙  Symboles: {', '.join(symbols)}")
        print(f"📊 {limit_per_symbol} bougies par symbole")

        all_features = []
        all_labels = []

        for i, symbol in enumerate(symbols, 1):
            print(f"\n{'─'*70}")
            print(f"[{i}/{len(symbols)}] Processing {symbol}...")
            print(f"{'─'*70}")

            # Build dataset pour ce symbole
            temp_filename = self.build_dataset(symbol, timeframe, limit_per_symbol)
            if temp_filename:
                # Charge le dataset temporaire
                with open(temp_filename, 'rb') as f:
                    data = pickle.load(f)
                    all_features.append(data['features'])
                    all_labels.append(data['labels'])

                # Supprime le fichier temporaire
                os.remove(temp_filename)
                print(f"✅ {symbol}: {len(data['labels'])} samples ajoutés")
            else:
                print(f"⚠️  {symbol}: échec, ignoré")

            # Pause pour éviter rate limit
            if i < len(symbols):
                time.sleep(2)

        if len(all_features) == 0:
            print(f"\n❌ Aucun dataset généré")
            return None

        # Combine tous les datasets
        print(f"\n{'='*70}")
        print(f"🔗 FUSION DES DATASETS".center(70))
        print(f"{'='*70}")

        combined_features = np.vstack(all_features)
        combined_labels = np.concatenate(all_labels)

        # Shuffle pour mélanger les cryptos
        indices = np.random.permutation(len(combined_labels))
        combined_features = combined_features[indices]
        combined_labels = combined_labels[indices]

        # Sauvegarde
        filename = self._save_dataset(
            combined_features,
            combined_labels,
            f"MULTI_{len(symbols)}cryptos",
            timeframe
        )

        if filename:
            print(f"\n✅ Dataset multi-crypto sauvegardé: {filename}")
            self._print_dataset_stats(combined_features, combined_labels)
            return filename
        return None

    def _fetch_historical_data(self, symbol: str, timeframe: str, limit: int) -> Optional[pd.DataFrame]:
        """Fetch données historiques via ccxt"""
        try:
            # ccxt limite à 1000 bougies par appel, on doit faire plusieurs appels
            # On fetch en remontant dans le temps depuis maintenant
            all_data = []
            remaining = limit
            end_timestamp = None  # None = maintenant

            while remaining > 0:
                fetch_limit = min(remaining, 1000)

                # Fetch les bougies les plus récentes disponibles
                if end_timestamp:
                    # Fetch les bougies juste AVANT end_timestamp (remonte dans le temps)
                    ohlcv = self.data_collector.exchange.fetch_ohlcv(
                        symbol, timeframe, limit=fetch_limit,
                        params={'endTime': end_timestamp}
                    )
                else:
                    # Premier appel: récupère les 1000 dernières bougies
                    ohlcv = self.data_collector.exchange.fetch_ohlcv(
                        symbol, timeframe, limit=fetch_limit
                    )

                if not ohlcv or len(ohlcv) == 0:
                    break

                df_chunk = pd.DataFrame(
                    ohlcv,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                df_chunk['timestamp'] = pd.to_datetime(df_chunk['timestamp'], unit='ms')

                all_data.insert(0, df_chunk)  # Insère au début (ordre chronologique)
                remaining -= len(df_chunk)

                # Prochaine itération: fetch les bougies AVANT la première du chunk actuel
                end_timestamp = int(df_chunk.iloc[0]['timestamp'].timestamp() * 1000) - 1

                print(f"   Téléchargé: {len(df_chunk)} bougies (total: {sum(len(d) for d in all_data)})")

                # Pause pour rate limit
                time.sleep(0.5)

                # Si on a reçu moins que demandé, on a atteint le début de l'historique
                if len(df_chunk) < fetch_limit:
                    print(f"   ℹ️  Fin de l'historique Binance atteinte")
                    break

            if all_data:
                df_final = pd.concat(all_data, ignore_index=True)
                # Remove duplicates
                df_final = df_final.drop_duplicates(subset=['timestamp'])
                df_final = df_final.sort_values('timestamp').reset_index(drop=True)
                return df_final
            return None

        except Exception as e:
            self.logger.error(f"Erreur fetch data: {e}")
            print(f"❌ Erreur: {e}")
            return None

    def _calculate_all_indicators(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Calcule tous les indicateurs nécessaires"""
        try:
            df = AdvancedIndicators.calculate_all(df)
            return df
        except Exception as e:
            self.logger.error(f"Erreur calcul indicateurs: {e}")
            print(f"❌ Erreur calcul indicateurs")
            return None

    def _extract_features_batch(self, df: pd.DataFrame) -> Tuple[List, List]:
        """Extrait les features pour toutes les bougies valides"""
        features_list = []
        valid_indices = []

        # Commence à partir de l'index 200 pour avoir assez d'historique
        for idx in range(200, len(df)):
            # Extrait un subset du DataFrame jusqu'à idx
            df_subset = df.iloc[:idx+1].copy()

            # S/R detection
            self.sr_detector.detect_levels(df_subset)
            current_price = df_subset.iloc[-1]['close']

            sr_dict = {
                'support_levels': self.sr_detector.support_levels,
                'resistance_levels': self.sr_detector.resistance_levels
            }

            # Extract features
            features = self.feature_extractor.extract_features(df_subset, sr_dict)
            if features is not None:
                features_list.append(features)
                valid_indices.append(idx)

            # Progress
            if (idx - 200) % 1000 == 0:
                print(f"   Features extraites: {len(features_list)}/{len(df)-200}")

        return features_list, valid_indices

    def _labelize_batch(self, df: pd.DataFrame, indices: List[int]) -> List[int]:
        """Labellise tous les samples"""
        labels = []
        for idx in indices:
            label = self._label_sample(df, idx)
            labels.append(label)

            if len(labels) % 1000 == 0:
                wins = len([l for l in labels if l == 1])
                losses = len([l for l in labels if l == 0])
                print(f"   Labellisés: {len(labels)} (WIN: {wins}, LOSS: {losses}, SKIP: {len(labels)-wins-losses})")

        return labels

    def _label_sample(self, df: pd.DataFrame, idx: int) -> int:
        """
        Labellise un sample (WIN/LOSS)

        Logique:
        - Regarde les N prochaines bougies
        - Si TP atteint avant SL → WIN (label 1)
        - Si SL atteint avant TP → LOSS (label 0)
        - Si ni l'un ni l'autre → pas de label (-1, skip)

        Args:
            df: DataFrame complet
            idx: Index de la bougie à labelliser

        Returns:
            1 (WIN) ou 0 (LOSS) ou -1 (pas de label)
        """
        entry_price = df.iloc[idx]['close']
        tp_price = entry_price * (1 + ml_config.LABEL_TP_PERCENT)
        sl_price = entry_price * (1 - ml_config.LABEL_SL_PERCENT)

        max_candles = ml_config.LABEL_MAX_CANDLES
        end_idx = min(idx + max_candles, len(df))

        for i in range(idx + 1, end_idx):
            high = df.iloc[i]['high']
            low = df.iloc[i]['low']

            # Check si TP atteint
            if high >= tp_price:
                return ml_config.LABEL_WIN  # 1

            # Check si SL atteint
            if low <= sl_price:
                return ml_config.LABEL_LOSS  # 0

        # Ni TP ni SL atteint dans le délai
        return -1  # Skip ce sample

    def _save_dataset(self, features: np.ndarray, labels: np.ndarray, symbol: str, timeframe: str) -> Optional[str]:
        """Sauvegarde le dataset"""
        try:
            # Nom de fichier
            symbol_clean = symbol.replace('/', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{ml_config.DATASET_OUTPUT_DIR}dataset_{symbol_clean}_{timeframe}_{timestamp}.pkl"

            # Package
            dataset = {
                'features': features,
                'labels': labels,
                'feature_names': ml_config.FEATURE_NAMES,
                'symbol': symbol,
                'timeframe': timeframe,
                'created_at': datetime.now().isoformat(),
                'config': {
                    'tp_percent': ml_config.LABEL_TP_PERCENT,
                    'sl_percent': ml_config.LABEL_SL_PERCENT,
                    'max_candles': ml_config.LABEL_MAX_CANDLES
                }
            }

            # Save
            with open(filename, 'wb') as f:
                pickle.dump(dataset, f)

            self.logger.info(f"Dataset sauvegardé: {filename}")
            return filename

        except Exception as e:
            self.logger.error(f"Erreur sauvegarde dataset: {e}")
            return None

    def _print_dataset_stats(self, features: np.ndarray, labels: np.ndarray):
        """Affiche les statistiques du dataset"""
        wins = np.sum(labels == 1)
        losses = np.sum(labels == 0)
        total = len(labels)
        win_rate = (wins / total * 100) if total > 0 else 0

        print(f"\n{'='*70}")
        print(f"📊 STATISTIQUES DATASET".center(70))
        print(f"{'='*70}")
        print(f"\n📈 Samples totaux: {total:,}")
        print(f"✅ WIN (TP atteint): {wins:,} ({win_rate:.1f}%)")
        print(f"❌ LOSS (SL atteint): {losses:,} ({100-win_rate:.1f}%)")
        print(f"🧬 Features: {features.shape[1]} dimensions")
        print(f"\n💡 Balance: {'✅ Équilibré' if 40 < win_rate < 60 else '⚠️ Déséquilibré'}")
        print(f"{'='*70}")


# Test/Run
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='APEX ML Dataset Builder')
    parser.add_argument('--symbol', type=str, default='ETH/USDT', help='Symbole (ex: ETH/USDT)')
    parser.add_argument('--multi', type=str, help='Plusieurs symboles séparés par virgule (ex: BTC/USDT,ETH/USDT,BNB/USDT)')
    parser.add_argument('--timeframe', type=str, default='1m', help='Timeframe (ex: 1m, 5m)')
    parser.add_argument('--limit', type=int, default=50000, help='Nombre de bougies')

    args = parser.parse_args()

    print("🔨 APEX ML Dataset Builder")
    print("="*70)

    builder = DatasetBuilder()

    if args.multi:
        # Mode multi-crypto
        symbols = [s.strip() for s in args.multi.split(',')]
        dataset_file = builder.build_multi_dataset(symbols, args.timeframe, args.limit)
    else:
        # Mode single crypto
        dataset_file = builder.build_dataset(args.symbol, args.timeframe, args.limit)

    if dataset_file:
        print(f"\n🎉 SUCCESS! Dataset prêt pour entraînement")
        print(f"📁 Fichier: {dataset_file}")
        print(f"\n💡 Prochaine étape:")
        print(f"   python train_ml_model.py --dataset {dataset_file}")
    else:
        print(f"\n❌ Échec création dataset")
