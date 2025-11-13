# train_ml_model.py - Entraînement des modèles ML

"""
ML Model Training pour APEX

Responsabilités:
- Charger un dataset créé par dataset_builder.py
- Split train/test (80/20)
- Entraîner un Random Forest (ou XGBoost, NN)
- Cross-validation pour éviter overfitting
- Évaluer les métriques (Accuracy, Precision, Recall, F1)
- Sauvegarder le modèle entraîné

Usage:
    python train_ml_model.py --dataset datasets/dataset_ETH_USDT_1m_*.pkl
    python train_ml_model.py --dataset datasets/dataset_MULTI_3cryptos_1m_*.pkl --model xgboost
"""

import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import ml_config as ml_config
from feature_extractor import FeatureExtractor
from logger_apex import get_logger
import os
from datetime import datetime
import argparse

class ModelTrainer:
    """
    Entraîneur de modèles ML pour APEX

    V1.0: Random Forest avec validation complète
    """

    def __init__(self, model_type: str = 'random_forest'):
        """
        Initialise le trainer

        Args:
            model_type: 'random_forest', 'xgboost', 'neural_net'
        """
        self.logger = get_logger()
        self.model_type = model_type
        self.model = None
        self.feature_extractor = FeatureExtractor()

        self.logger.info(f"✅ ModelTrainer initialisé (type: {model_type})")

    def load_dataset(self, dataset_path: str) -> tuple:
        """
        Charge un dataset depuis un fichier pickle

        Returns:
            (features, labels, dataset_info)
        """
        print(f"\n📂 Chargement dataset...")
        print(f"   Fichier: {dataset_path}")

        try:
            with open(dataset_path, 'rb') as f:
                data = pickle.load(f)

            features = data['features']
            labels = data['labels']

            print(f"\n✅ Dataset chargé:")
            print(f"   Samples: {len(labels):,}")
            print(f"   Features: {features.shape[1]}")
            print(f"   Symbole: {data.get('symbol', 'N/A')}")
            print(f"   Timeframe: {data.get('timeframe', 'N/A')}")

            return features, labels, data

        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
            return None, None, None

    def train(self, X: np.ndarray, y: np.ndarray) -> bool:
        """
        Entraîne le modèle

        Args:
            X: Features (n_samples, 28)
            y: Labels (n_samples,)

        Returns:
            True si succès
        """
        print(f"\n{'='*70}")
        print(f"🤖 ENTRAÎNEMENT MODÈLE {self.model_type.upper()}".center(70))
        print(f"{'='*70}")

        # Split train/test
        print(f"\n[1/6] 📊 Split train/test ({ml_config.DATASET_SPLIT_RATIO*100:.0f}/{(1-ml_config.DATASET_SPLIT_RATIO)*100:.0f})...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=1-ml_config.DATASET_SPLIT_RATIO,
            random_state=42,
            stratify=y  # Garde la balance WIN/LOSS
        )

        print(f"   Train: {len(y_train):,} samples")
        print(f"   Test:  {len(y_test):,} samples")

        # Fit feature extractor sur train set (pour normalisation)
        print(f"\n[2/6] 🔧 Fit feature extractor (normalisation)...")
        self.feature_extractor.fit(X_train)
        print(f"   ✅ Normalisation fitted")

        # Normalise train et test
        if ml_config.NORMALIZE_FEATURES:
            print(f"   Normalisation des features...")
            X_train_normalized = np.array([self.feature_extractor._normalize(x) for x in X_train])
            X_test_normalized = np.array([self.feature_extractor._normalize(x) for x in X_test])
        else:
            X_train_normalized = X_train
            X_test_normalized = X_test

        # Créer le modèle
        print(f"\n[3/6] 🏗️  Création du modèle...")
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=ml_config.RF_N_ESTIMATORS,
                max_depth=ml_config.RF_MAX_DEPTH,
                min_samples_split=ml_config.RF_MIN_SAMPLES_SPLIT,
                min_samples_leaf=ml_config.RF_MIN_SAMPLES_LEAF,
                random_state=ml_config.RF_RANDOM_STATE,
                n_jobs=-1,  # Utilise tous les CPUs
                verbose=1
            )
            print(f"   Random Forest: {ml_config.RF_N_ESTIMATORS} arbres, depth={ml_config.RF_MAX_DEPTH}")

        elif self.model_type == 'xgboost':
            try:
                import xgboost as xgb
                self.model = xgb.XGBClassifier(
                    n_estimators=ml_config.XGB_N_ESTIMATORS,
                    max_depth=ml_config.XGB_MAX_DEPTH,
                    learning_rate=ml_config.XGB_LEARNING_RATE,
                    subsample=ml_config.XGB_SUBSAMPLE,
                    random_state=ml_config.XGB_RANDOM_STATE,
                    n_jobs=-1
                )
                print(f"   XGBoost: {ml_config.XGB_N_ESTIMATORS} estimators")
            except ImportError:
                print(f"   ⚠️  XGBoost pas installé, utilise Random Forest")
                self.model_type = 'random_forest'
                self.model = RandomForestClassifier(
                    n_estimators=ml_config.RF_N_ESTIMATORS,
                    max_depth=ml_config.RF_MAX_DEPTH,
                    random_state=ml_config.RF_RANDOM_STATE,
                    n_jobs=-1
                )

        else:
            print(f"   ❌ Type de modèle inconnu: {self.model_type}")
            return False

        # Entraînement
        print(f"\n[4/6] 🚂 Entraînement en cours...")
        print(f"   (Ceci peut prendre 1-5 minutes)")
        try:
            self.model.fit(X_train_normalized, y_train)
            print(f"   ✅ Entraînement terminé!")
        except Exception as e:
            print(f"   ❌ Erreur entraînement: {e}")
            return False

        # Cross-validation
        print(f"\n[5/6] 🔄 Cross-validation ({ml_config.CROSS_VALIDATION_FOLDS}-fold)...")
        try:
            cv_scores = cross_val_score(
                self.model, X_train_normalized, y_train,
                cv=ml_config.CROSS_VALIDATION_FOLDS,
                scoring='accuracy',
                n_jobs=-1
            )
            print(f"   CV Scores: {cv_scores}")
            print(f"   CV Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        except Exception as e:
            print(f"   ⚠️  CV échoué: {e}")

        # Évaluation sur test set
        print(f"\n[6/6] 📊 Évaluation sur test set...")
        y_pred = self.model.predict(X_test_normalized)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)

        print(f"\n{'='*70}")
        print(f"📊 MÉTRIQUES FINALES".center(70))
        print(f"{'='*70}")
        print(f"\n🎯 Accuracy:  {accuracy*100:.2f}%")
        print(f"🎯 Precision: {precision*100:.2f}%")
        print(f"🎯 Recall:    {recall*100:.2f}%")
        print(f"🎯 F1-Score:  {f1*100:.2f}%")

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"\n📊 Confusion Matrix:")
        print(f"                Predicted")
        print(f"              LOSS    WIN")
        print(f"   Actual LOSS {cm[0][0]:5d}  {cm[0][1]:5d}")
        print(f"          WIN  {cm[1][0]:5d}  {cm[1][1]:5d}")

        # Classification report
        print(f"\n📋 Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['LOSS', 'WIN'], zero_division=0))

        # Feature importance (Random Forest)
        if self.model_type == 'random_forest':
            print(f"\n🌟 TOP 10 FEATURES LES PLUS IMPORTANTES:")
            importances = self.model.feature_importances_
            indices = np.argsort(importances)[::-1][:10]

            for i, idx in enumerate(indices, 1):
                feature_name = ml_config.FEATURE_NAMES[idx]
                importance = importances[idx]
                print(f"   {i:2d}. {feature_name:30s} {importance:.4f}")

        print(f"{'='*70}")

        return True

    def save_model(self, output_path: str = None) -> str:
        """
        Sauvegarde le modèle entraîné

        Args:
            output_path: Chemin de sortie (optionnel)

        Returns:
            Chemin du fichier sauvegardé
        """
        if self.model is None:
            print(f"❌ Aucun modèle à sauvegarder")
            return None

        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"{ml_config.ML_MODEL_PATH}apex_ml_{self.model_type}_{timestamp}.pkl"

        # Créer le dossier si nécessaire
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Package complet
        model_package = {
            'model': self.model,
            'type': self.model_type,
            'feature_min': self.feature_extractor.feature_min,
            'feature_max': self.feature_extractor.feature_max,
            'feature_mean': self.feature_extractor.feature_mean,
            'feature_std': self.feature_extractor.feature_std,
            'feature_names': ml_config.FEATURE_NAMES,
            'created_at': datetime.now().isoformat(),
            'config': {
                'normalize': ml_config.NORMALIZE_FEATURES,
                'normalization_method': ml_config.NORMALIZATION_METHOD,
                'tp_percent': ml_config.LABEL_TP_PERCENT,
                'sl_percent': ml_config.LABEL_SL_PERCENT,
            }
        }

        try:
            with open(output_path, 'wb') as f:
                pickle.dump(model_package, f)

            print(f"\n✅ Modèle sauvegardé: {output_path}")

            # Copie aussi vers le modèle par défaut
            default_path = os.path.join(ml_config.ML_MODEL_PATH, ml_config.ML_DEFAULT_MODEL)
            with open(default_path, 'wb') as f:
                pickle.dump(model_package, f)
            print(f"✅ Modèle par défaut mis à jour: {default_path}")

            self.logger.info(f"Modèle sauvegardé: {output_path}")

            return output_path

        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            self.logger.error(f"Erreur sauvegarde modèle: {e}")
            return None


# Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='APEX ML Model Trainer')
    parser.add_argument('--dataset', type=str, required=True, help='Chemin vers le dataset .pkl')
    parser.add_argument('--model', type=str, default='random_forest', choices=['random_forest', 'xgboost'], help='Type de modèle')
    parser.add_argument('--output', type=str, help='Chemin de sortie du modèle (optionnel)')

    args = parser.parse_args()

    print("🤖 APEX ML Model Trainer")
    print("="*70)

    # Charge dataset
    trainer = ModelTrainer(model_type=args.model)
    X, y, dataset_info = trainer.load_dataset(args.dataset)

    if X is None:
        print("\n❌ Échec chargement dataset")
        exit(1)

    # Entraîne
    success = trainer.train(X, y)

    if not success:
        print("\n❌ Échec entraînement")
        exit(1)

    # Sauvegarde
    model_path = trainer.save_model(args.output)

    if model_path:
        print(f"\n{'='*70}")
        print(f"🎉 SUCCESS! Modèle ML prêt à l'emploi")
        print(f"{'='*70}")
        print(f"\n📁 Modèle: {model_path}")
        print(f"\n💡 Le bot va maintenant utiliser ce modèle automatiquement!")
        print(f"\n🚀 Prochaine étape: Lance le bot avec")
        print(f"   python main_apex.py")
    else:
        print("\n❌ Échec sauvegarde modèle")
        exit(1)
