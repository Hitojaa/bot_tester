# ml_module.py - Module principal du système de Machine Learning

"""
ML Module pour APEX AI

Responsabilités:
- Charger des modèles ML entraînés (pickle)
- Faire des prédictions avec probabilités
- Gérer la fiabilité du modèle (historique prédictions vs résultats)
- S'intégrer comme 4ème couche dans APEX AI
- Pondération dynamique basée sur la précision historique

Architecture:
- Modèles interchangeables (RF, XGBoost, NN)
- Tracking de la précision en temps réel
- Adaptation de la confiance selon les performances
"""

import os
import pickle
import json
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import deque
from datetime import datetime
import ml_config as ml_config
from feature_extractor import FeatureExtractor
from logger_apex import get_logger

class MLPredictor:
    """
    Prédicteur ML pour APEX

    V1.0: Prédictions avec suivi de précision en temps réel
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialise le prédicteur ML

        Args:
            model_path: Chemin vers le modèle pickled (optionnel)
        """
        self.logger = get_logger()
        self.feature_extractor = FeatureExtractor()

        # Modèle ML
        self.model = None
        self.model_type = None
        self.model_path = model_path or os.path.join(ml_config.ML_MODEL_PATH, ml_config.ML_DEFAULT_MODEL)

        # Métriques de fiabilité
        self.predictions_history = deque(maxlen=ml_config.ML_ACCURACY_WINDOW)
        self.accuracy_rate = 0.5  # Commence neutre à 50%
        self.current_weight = ml_config.ML_INITIAL_WEIGHT

        # Compteurs
        self.total_predictions = 0
        self.correct_predictions = 0
        self.trade_count = 0

        # Chargement du modèle
        if ml_config.ML_ENABLED:
            self.load_model()

        # 💾 Chargement des stats persistantes (accuracy, weight, historique)
        self.stats_path = os.path.join(ml_config.ML_MODEL_PATH, 'apex_ml_stats.json')
        self.load_stats()

        self.logger.info(f"✅ MLPredictor initialisé (enabled: {ml_config.ML_ENABLED})")

    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        Charge un modèle ML depuis un fichier pickle

        Args:
            model_path: Chemin vers le modèle (optionnel)

        Returns:
            True si succès, False sinon
        """
        path = model_path or self.model_path

        if not os.path.exists(path):
            self.logger.warning(f"⚠️  Modèle ML introuvable: {path}")
            self.logger.warning("Le bot fonctionnera sans la couche ML")
            return False

        try:
            with open(path, 'rb') as f:
                model_data = pickle.load(f)

            # Le pickle peut contenir juste le modèle ou un dict avec métadonnées
            if isinstance(model_data, dict):
                self.model = model_data.get('model')
                self.model_type = model_data.get('type', 'unknown')
                self.feature_extractor.feature_min = model_data.get('feature_min', {})
                self.feature_extractor.feature_max = model_data.get('feature_max', {})
                self.feature_extractor.feature_mean = model_data.get('feature_mean', {})
                self.feature_extractor.feature_std = model_data.get('feature_std', {})
                self.feature_extractor.is_fitted = True
            else:
                self.model = model_data
                self.model_type = 'unknown'

            self.logger.info(f"✅ Modèle ML chargé: {path} (type: {self.model_type})")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erreur chargement modèle ML: {e}")
            return False

    def predict(self, df, support_resistance: Optional[Dict] = None) -> Optional[Dict]:
        """
        Fait une prédiction ML

        Args:
            df: DataFrame avec indicateurs
            support_resistance: Dict avec S/R

        Returns:
            Dict avec: {
                'prediction': 0 ou 1 (LOSS ou WIN),
                'probability': float (0-1),
                'confidence': float (0-1) ajustée par précision historique,
                'ml_score': float (-100 à +100) compatible APEX,
                'weight': float (pondération actuelle du ML)
            }
        """
        if not ml_config.ML_ENABLED or self.model is None:
            return None

        try:
            # Extrait les features
            features = self.feature_extractor.extract_features(df, support_resistance)
            if features is None:
                return None

            # Reshape pour le modèle (1 sample)
            features_2d = features.reshape(1, -1)

            # Prédiction
            prediction = self.model.predict(features_2d)[0]

            # Probabilités (si le modèle le supporte)
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(features_2d)[0]
                # Probabilité de la classe WIN (index 1)
                probability_win = probabilities[1] if len(probabilities) > 1 else probabilities[0]
            else:
                # Modèles sans predict_proba (SVM, etc.)
                probability_win = 0.6 if prediction == 1 else 0.4

            # Confiance ajustée par la précision historique
            raw_confidence = probability_win
            adjusted_confidence = self._adjust_confidence(raw_confidence)

            # Score ML normalisé (-100 à +100) pour compatibilité APEX
            # Si probabilité > 50% = signal haussier
            # Si probabilité < 50% = signal baissier
            ml_score = (probability_win - 0.5) * 200  # -100 à +100

            self.total_predictions += 1

            return {
                'prediction': int(prediction),
                'probability': float(probability_win),
                'confidence': float(adjusted_confidence),
                'ml_score': float(ml_score),
                'weight': float(self.current_weight),
                'accuracy_rate': float(self.accuracy_rate)
            }

        except Exception as e:
            self.logger.error(f"Erreur prédiction ML: {e}")
            return None

    def _adjust_confidence(self, raw_confidence: float) -> float:
        """
        Ajuste la confiance selon la précision historique du modèle

        Si le modèle est très précis historiquement, on augmente la confiance
        Si le modèle est peu fiable, on la diminue
        """
        # Facteur basé sur la précision historique
        if self.accuracy_rate > 0.65:  # Modèle fiable
            factor = 1.2
        elif self.accuracy_rate < 0.50:  # Modèle peu fiable
            factor = 0.8
        else:  # Modèle neutre
            factor = 1.0

        adjusted = raw_confidence * factor
        return min(max(adjusted, 0.0), 1.0)  # Clamp entre 0 et 1

    def update_accuracy(self, prediction_result: bool):
        """
        Met à jour la précision du modèle après un trade terminé

        Args:
            prediction_result: True si prédiction correcte, False sinon
        """
        self.predictions_history.append(1 if prediction_result else 0)

        if len(self.predictions_history) > 0:
            self.accuracy_rate = sum(self.predictions_history) / len(self.predictions_history)

        if prediction_result:
            self.correct_predictions += 1

        self.trade_count += 1

        # Réajuste la pondération tous les N trades
        if self.trade_count % ml_config.ML_REWEIGHT_THRESHOLD == 0:
            self._recompute_weight()

        # 💾 Sauvegarde les stats après chaque update
        self.save_stats()

        self.logger.info(f"📊 ML Accuracy mise à jour: {self.accuracy_rate*100:.1f}% ({len(self.predictions_history)} trades)")

    def _recompute_weight(self):
        """
        Recalcule la pondération du ML selon sa précision

        Si précision > 65% → Augmente le poids (max 30%)
        Si précision < 50% → Diminue le poids (min 5%)
        """
        if self.accuracy_rate > 0.65:
            # Modèle fiable, augmente le poids
            self.current_weight = min(
                ml_config.ML_MAX_WEIGHT,
                ml_config.ML_INITIAL_WEIGHT + (self.accuracy_rate - 0.65) * 0.5
            )
        elif self.accuracy_rate < 0.50:
            # Modèle peu fiable, diminue le poids
            self.current_weight = max(
                ml_config.ML_MIN_WEIGHT,
                ml_config.ML_INITIAL_WEIGHT - (0.50 - self.accuracy_rate) * 0.5
            )
        else:
            # Modèle neutre, poids initial
            self.current_weight = ml_config.ML_INITIAL_WEIGHT

        self.logger.info(f"🔄 ML Weight ajusté: {self.current_weight:.2%} (accuracy: {self.accuracy_rate*100:.1f}%)")

    def save_stats(self):
        """
        💾 Sauvegarde les stats ML dans un fichier JSON
        Permet de conserver l'accuracy et l'historique entre les redémarrages
        """
        try:
            # Crée le dossier si nécessaire
            os.makedirs(os.path.dirname(self.stats_path), exist_ok=True)

            stats_data = {
                'predictions_history': list(self.predictions_history),
                'accuracy_rate': float(self.accuracy_rate),
                'current_weight': float(self.current_weight),
                'trade_count': int(self.trade_count),
                'total_predictions': int(self.total_predictions),
                'correct_predictions': int(self.correct_predictions),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            with open(self.stats_path, 'w') as f:
                json.dump(stats_data, f, indent=2)

            # self.logger.debug(f"💾 Stats ML sauvegardées: {self.stats_path}")

        except Exception as e:
            self.logger.error(f"❌ Erreur sauvegarde stats ML: {e}")

    def load_stats(self):
        """
        📂 Charge les stats ML depuis le fichier JSON
        Restaure l'accuracy et l'historique des trades précédents
        """
        if not os.path.exists(self.stats_path):
            self.logger.info("📊 Aucun historique ML trouvé (première session)")
            return

        try:
            with open(self.stats_path, 'r') as f:
                stats_data = json.load(f)

            # Restaure l'historique
            self.predictions_history = deque(
                stats_data.get('predictions_history', []),
                maxlen=ml_config.ML_ACCURACY_WINDOW
            )
            self.accuracy_rate = stats_data.get('accuracy_rate', 0.5)
            self.current_weight = stats_data.get('current_weight', ml_config.ML_INITIAL_WEIGHT)
            self.trade_count = stats_data.get('trade_count', 0)
            self.total_predictions = stats_data.get('total_predictions', 0)
            self.correct_predictions = stats_data.get('correct_predictions', 0)

            last_updated = stats_data.get('last_updated', 'inconnu')
            history_size = len(self.predictions_history)

            print(f"📊 Stats ML rechargées: Accuracy {self.accuracy_rate*100:.1f}%, Weight {self.current_weight*100:.0f}%, {history_size} trades en mémoire")
            self.logger.info(f"✅ Stats ML rechargées depuis {last_updated}")

        except Exception as e:
            self.logger.error(f"❌ Erreur chargement stats ML: {e}")
            self.logger.info("🔄 Réinitialisation des stats ML")

    def get_stats(self) -> Dict:
        """Retourne les statistiques du modèle ML"""
        return {
            'enabled': ml_config.ML_ENABLED,
            'model_loaded': self.model is not None,
            'model_type': self.model_type,
            'total_predictions': self.total_predictions,
            'correct_predictions': self.correct_predictions,
            'accuracy_rate': self.accuracy_rate,
            'current_weight': self.current_weight,
            'history_size': len(self.predictions_history)
        }

    def print_stats(self):
        """Affiche les statistiques du modèle ML"""
        stats = self.get_stats()

        print("\n" + "="*60)
        print("🧠 STATISTIQUES MODÈLE ML".center(60))
        print("="*60)

        if not stats['enabled']:
            print("\n⚠️  Système ML désactivé")
            return

        if not stats['model_loaded']:
            print("\n⚠️  Aucun modèle chargé")
            return

        print(f"\n📊 Modèle: {stats['model_type']}")
        print(f"🎯 Précision: {stats['accuracy_rate']*100:.1f}%")
        print(f"⚖️  Pondération actuelle: {stats['current_weight']*100:.1f}%")
        print(f"📈 Prédictions totales: {stats['total_predictions']}")
        print(f"✅ Prédictions correctes: {stats['correct_predictions']}")
        print(f"📝 Historique: {stats['history_size']} trades")

        print("="*60)


# Test du module
if __name__ == "__main__":
    print("🧠 Test ML Module")

    predictor = MLPredictor()

    stats = predictor.get_stats()
    print(f"\n✅ Système ML: {'enabled' if stats['enabled'] else 'disabled'}")
    print(f"📊 Modèle chargé: {'yes' if stats['model_loaded'] else 'no'}")

    if not stats['model_loaded']:
        print("\n⚠️  Aucun modèle trouvé. Pour tester le ML:")
        print("   1. Génère un dataset avec dataset_builder.py")
        print("   2. Entraîne un modèle avec train_ml_model.py")
        print("   3. Place le modèle dans models/apex_ml_model.pkl")
