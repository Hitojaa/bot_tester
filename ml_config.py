# ml_config.py - Configuration du système de Machine Learning

"""
Configuration centralisée pour le système ML d'APEX

Architecture:
- Feature extraction standardisée
- Modèles interchangeables (RF, XGBoost, NN)
- Pipeline offline d'entraînement
- Intégration comme 4ème couche dans APEX AI
"""

# ═══════════════════════════════════════════════════════════
# 🧠 ACTIVATION DU SYSTÈME ML
# ═══════════════════════════════════════════════════════════

ML_ENABLED = True              # Active/désactive le système ML
ML_MODEL_PATH = "models/"      # Dossier des modèles entraînés
ML_DEFAULT_MODEL = "apex_ml_model.pkl"  # Modèle par défaut

# ═══════════════════════════════════════════════════════════
# 📊 FEATURES EXTRACTION
# ═══════════════════════════════════════════════════════════

# Liste exhaustive des features à extraire (ordre strict!)
FEATURE_NAMES = [
    # Prix et variations (4 features)
    'price_pct_change_1',      # Variation sur 1 bougie
    'price_pct_change_5',      # Variation sur 5 bougies
    'price_pct_change_15',     # Variation sur 15 bougies
    'high_low_ratio',          # (High - Low) / Close

    # EMA relatives (4 features)
    'price_vs_ema9',           # (Price - EMA9) / Price
    'price_vs_ema20',          # (Price - EMA20) / Price
    'price_vs_ema50',          # (Price - EMA50) / Price
    'price_vs_ema200',         # (Price - EMA200) / Price

    # Oscillateurs (6 features)
    'rsi',                     # RSI normalisé (0-100)
    'rsi_trend',               # RSI - RSI(5 bougies avant)
    'macd',                    # MACD
    'macd_signal',             # MACD Signal
    'macd_diff',               # MACD - Signal
    'stoch_k',                 # Stochastique %K

    # Volatilité (3 features)
    'atr_normalized',          # ATR / Price
    'bb_position',             # Position dans les Bollinger (0-1)
    'bb_width',                # (BB_upper - BB_lower) / Price

    # Volume (3 features)
    'volume_ratio',            # Volume / Moyenne volume (20)
    'volume_trend',            # Volume - Volume(5 avant)
    'obv_trend',               # OBV - OBV(10 avant)

    # Support/Résistance (4 features)
    'distance_to_support',     # (Price - Support) / Price
    'distance_to_resistance',  # (Resistance - Price) / Price
    'support_strength',        # Score de force du support (0-1)
    'resistance_strength',     # Score de force de la résistance (0-1)

    # Autres indicateurs (4 features)
    'supertrend_signal',       # -1 (SELL) / 0 (NEUTRE) / +1 (BUY)
    'vwap_deviation',          # (Price - VWAP) / Price
    'momentum_short',          # Momentum 5 bougies
    'momentum_long',           # Momentum 15 bougies
]

# Total: 28 features standardisées
FEATURE_COUNT = len(FEATURE_NAMES)

# ═══════════════════════════════════════════════════════════
# 🎯 LABELLISATION (pour dataset builder)
# ═══════════════════════════════════════════════════════════

# Paramètres pour créer les labels TP/SL
LABEL_TP_PERCENT = 0.015       # +1.5% = Take Profit
LABEL_SL_PERCENT = 0.008       # -0.8% = Stop Loss
LABEL_MAX_CANDLES = 30         # Cherche TP/SL dans les 30 prochaines bougies

# Classes de prédiction
LABEL_WIN = 1                  # TP atteint avant SL
LABEL_LOSS = 0                 # SL atteint avant TP

# ═══════════════════════════════════════════════════════════
# ⚙️ MODÈLE ML
# ═══════════════════════════════════════════════════════════

# Type de modèle par défaut
DEFAULT_MODEL_TYPE = "random_forest"  # "random_forest", "xgboost", "neural_net"

# Hyperparamètres Random Forest
RF_N_ESTIMATORS = 200
RF_MAX_DEPTH = 15
RF_MIN_SAMPLES_SPLIT = 20
RF_MIN_SAMPLES_LEAF = 10
RF_RANDOM_STATE = 42

# Hyperparamètres XGBoost
XGB_N_ESTIMATORS = 200
XGB_MAX_DEPTH = 8
XGB_LEARNING_RATE = 0.05
XGB_SUBSAMPLE = 0.8
XGB_RANDOM_STATE = 42

# ═══════════════════════════════════════════════════════════
# 🔥 INTÉGRATION DANS APEX AI
# ═══════════════════════════════════════════════════════════

# Pondération du ML dans l'APEX Score
ML_INITIAL_WEIGHT = 0.15       # 15% au départ (4ème couche)
ML_MAX_WEIGHT = 0.30           # 30% maximum si très fiable
ML_MIN_WEIGHT = 0.05           # 5% minimum si peu fiable

# Seuil de confiance ML
ML_MIN_CONFIDENCE = 0.55       # Minimum 55% de confiance pour agir
ML_HIGH_CONFIDENCE = 0.70      # 70%+ = signal fort

# Métrique de fiabilité
ML_ACCURACY_WINDOW = 50        # Fenêtre glissante pour calculer précision
ML_REWEIGHT_THRESHOLD = 10     # Recalcule la pondération tous les 10 trades

# ═══════════════════════════════════════════════════════════
# 📂 DATASET BUILDER
# ═══════════════════════════════════════════════════════════

DATASET_OUTPUT_DIR = "datasets/"
DATASET_MIN_SIZE = 500         # Minimum 500 samples (10k recommandé pour prod)
DATASET_SPLIT_RATIO = 0.8      # 80% train / 20% test

# Validation
CROSS_VALIDATION_FOLDS = 5

# ═══════════════════════════════════════════════════════════
# 🔧 VALIDATION & NORMALISATION
# ═══════════════════════════════════════════════════════════

# Gestion des valeurs manquantes
FILL_NA_METHOD = "forward"     # "forward", "mean", "zero"
MAX_NA_PERCENT = 0.05          # Maximum 5% de NaN toléré

# Normalisation
NORMALIZE_FEATURES = True
NORMALIZATION_METHOD = "minmax"  # "minmax", "standard"

# Limites de features (pour détection d'anomalies)
FEATURE_BOUNDS = {
    'rsi': (0, 100),
    'stoch_k': (0, 100),
    'bb_position': (0, 1),
    'volume_ratio': (0, 10),
    'price_pct_change_1': (-0.05, 0.05),
}
