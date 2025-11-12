# config_apex.py - Configuration PRO du bot APEX PREDATOR

# ═══════════════════════════════════════════════════════════
# 🔐 BINANCE API (OBLIGATOIRE)
# ═══════════════════════════════════════════════════════════
BINANCE_API_KEY = "jF0g4luf0aoTn2myoWaivW3R1cP7JiPT1E4dOe6guz6olaiCJmFelCWX4YX4qbm7"
BINANCE_SECRET_KEY = "M7TIECN2ONPU6OJhRiJQuK1Dm7U6aDDPP6Ue5xFoSu3TUW3ch2hCbtk4ameTDrOe"

# ═══════════════════════════════════════════════════════════
# 🎯 CONFIGURATION SCALPING PRO
# ═══════════════════════════════════════════════════════════

# Mode de fonctionnement
DRY_RUN = True  # True = Simulation, False = Trading réel ⚠️
VERBOSE = True  # Affichage détaillé

# Marché
SYMBOL = "ETH/USDT"  # Paire à trader
TIMEFRAME = "1m"     # 1 minute pour scalping ultra-rapide

# Capital
INITIAL_CAPITAL = 100.0  # Capital de départ en USDT

# ═══════════════════════════════════════════════════════════
# ⚡ PARAMÈTRES SCALPING AGRESSIF
# ═══════════════════════════════════════════════════════════

# Position sizing PRO
MIN_POSITION_SIZE = 0.10    # 10% minimum du capital
MAX_POSITION_SIZE = 0.25    # 25% maximum du capital
DEFAULT_POSITION_SIZE = 0.15  # 15% par défaut

# Stops ultra-serrés pour scalping
STOP_LOSS_PERCENT = 0.008   # 0.8% stop-loss (serré)
TAKE_PROFIT_PERCENT = 0.025  # 2.5% take-profit (réaliste)

# Multi-target exits (PRO)
FIRST_TARGET_PERCENT = 0.015   # 1.5% - prend 50% de profit
SECOND_TARGET_PERCENT = 0.025  # 2.5% - prend 30% de profit
THIRD_TARGET_PERCENT = 0.04    # 4% - laisse runner 20%

# Trailing stop
TRAILING_STOP_ACTIVATION = 0.012  # Active à +1.2%
TRAILING_STOP_DISTANCE = 0.008    # Distance 0.8%

# ═══════════════════════════════════════════════════════════
# 🧠 APEX SCORE - Seuils d'entrée
# ═══════════════════════════════════════════════════════════

MIN_APEX_SCORE = 72        # Score minimum pour entrer (strict!)
IDEAL_APEX_SCORE = 78      # Score idéal (setup parfait)
MIN_CONFIDENCE = 65        # Confiance IA minimum

# ═══════════════════════════════════════════════════════════
# 📊 INDICATEURS TECHNIQUES PRO
# ═══════════════════════════════════════════════════════════

# EMA (Exponential Moving Average)
EMA_FAST = 9      # EMA rapide
EMA_MEDIUM = 20   # EMA moyenne
EMA_SLOW = 50     # EMA lente
EMA_TREND = 200   # EMA tendance long terme

# RSI (Relative Strength Index)
RSI_PERIOD = 14
RSI_OVERSOLD = 25      # Survente extrême
RSI_OVERSOLD_LIGHT = 35  # Survente légère
RSI_OVERBOUGHT = 75    # Surachat extrême
RSI_OVERBOUGHT_LIGHT = 65  # Surachat léger

# MACD
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Bollinger Bands
BB_PERIOD = 20
BB_STD = 2

# ATR (Average True Range)
ATR_PERIOD = 14
ATR_MULTIPLIER = 1.5  # Pour stop-loss adaptatif

# Stochastic
STOCH_K = 14
STOCH_D = 3
STOCH_SMOOTH = 3

# ═══════════════════════════════════════════════════════════
# 📈 VOLUME & ORDER FLOW
# ═══════════════════════════════════════════════════════════

# Volume Profile
VOLUME_PROFILE_PERIODS = 100  # Nombre de périodes à analyser
VOLUME_SPIKE_THRESHOLD = 1.5  # Volume spike si > 150% de la moyenne

# VWAP
VWAP_DEVIATION_THRESHOLD = 0.005  # 0.5% d'écart acceptable

# Order Flow (Delta Volume)
DELTA_VOLUME_THRESHOLD = 0.7  # 70% déséquilibre acheteurs/vendeurs
BIG_ORDER_MULTIPLIER = 10     # Ordre considéré "gros" si 10x la moyenne

# ═══════════════════════════════════════════════════════════
# 🎯 STRATÉGIES ACTIVÉES
# ═══════════════════════════════════════════════════════════

STRATEGIES_ENABLED = {
    'ema_cross': True,        # Croisement EMA
    'breakout': True,         # Cassure de range
    'reversal': True,         # Retournement
    'vwap_bounce': True,      # Rebond VWAP
    'order_flow': True,       # Order flow
    'support_resistance': True  # S/R
}

# Poids des stratégies dans le score final
STRATEGY_WEIGHTS = {
    'ema_cross': 0.20,
    'breakout': 0.25,
    'reversal': 0.15,
    'vwap_bounce': 0.20,
    'order_flow': 0.10,
    'support_resistance': 0.10
}

# ═══════════════════════════════════════════════════════════
# 🛡️ GESTION DU RISQUE PRO
# ═══════════════════════════════════════════════════════════

# Limites journalières
MAX_DAILY_LOSS_PERCENT = 0.10     # 10% perte max par jour
MAX_DAILY_TRADES = 50             # 50 trades max par jour
MAX_CONSECUTIVE_LOSSES = 4        # Arrêt après 4 pertes consécutives

# Limites par trade
MIN_RISK_REWARD_RATIO = 2.0       # R/R minimum 2:1
MAX_POSITION_RISK = 0.015         # 1.5% du capital max par trade

# Période d'observation avant 1er trade
MIN_OBSERVATION_TIME = 1800       # 30 minutes (en secondes)
MIN_CANDLES_BEFORE_TRADE = 100    # 100 bougies minimum avant trade

# ═══════════════════════════════════════════════════════════
# 🔍 DÉTECTION DE MARCHÉ
# ═══════════════════════════════════════════════════════════

# Régimes de marché
TRENDING_THRESHOLD = 0.02      # 2% de mouvement = tendance
RANGING_THRESHOLD = 0.005      # 0.5% de mouvement = range
VOLATILE_THRESHOLD = 1.8       # ATR élevé = volatile

# Breakout detection
RANGE_MIN_DURATION = 15        # 15 bougies minimum pour un range
BREAKOUT_VOLUME_MULTIPLIER = 1.5  # Volume spike pour confirmer breakout

# ═══════════════════════════════════════════════════════════
# ⚙️ PARAMÈTRES TECHNIQUES
# ═══════════════════════════════════════════════════════════

# Binance
MIN_ORDER_SIZE = 10.0          # Taille minimum d'ordre en USDT
BINANCE_FEE = 0.001            # 0.1% de frais (réduit à 0.075% avec BNB)

# Analyse
DATA_FETCH_LIMIT = 500         # Nombre de bougies à récupérer
ANALYSIS_INTERVAL = 10         # Analyse toutes les 10 secondes

# Cache
CACHE_DURATION = 30            # Durée du cache en secondes

# ═══════════════════════════════════════════════════════════
# 🎨 AFFICHAGE
# ═══════════════════════════════════════════════════════════

SHOW_DETAILED_ANALYSIS = True   # Affiche analyse détaillée
SHOW_INDICATORS = True          # Affiche indicateurs
SHOW_PATTERNS = True            # Affiche patterns détectés
SHOW_ORDER_FLOW = True          # Affiche order flow
SHOW_VOLUME_PROFILE = True      # Affiche volume profile

# Fréquence d'affichage stats
STATS_DISPLAY_FREQUENCY = 10    # Affiche stats toutes les 10 itérations

# ═══════════════════════════════════════════════════════════
# 📊 PROFILS PRE-CONFIGURÉS
# ═══════════════════════════════════════════════════════════

PROFILES = {
    'ultra_aggressive': {
        'position_size': 0.25,
        'min_apex_score': 80,
        'stop_loss': 0.006,
        'take_profit': 0.020,
        'max_daily_trades': 80
    },
    'aggressive': {
        'position_size': 0.18,
        'min_apex_score': 85,
        'stop_loss': 0.008,
        'take_profit': 0.025,
        'max_daily_trades': 50
    },
    'balanced': {
        'position_size': 0.15,
        'min_apex_score': 88,
        'stop_loss': 0.010,
        'take_profit': 0.030,
        'max_daily_trades': 30
    },
    'conservative': {
        'position_size': 0.10,
        'min_apex_score': 92,
        'stop_loss': 0.012,
        'take_profit': 0.035,
        'max_daily_trades': 20
    }
}

# Profil actif par défaut
ACTIVE_PROFILE = 'aggressive'

# ═══════════════════════════════════════════════════════════
# 🔧 FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════

def load_profile(profile_name):
    """Charge un profil de configuration"""
    if profile_name not in PROFILES:
        print(f"⚠️  Profil '{profile_name}' inconnu, utilisation du profil par défaut")
        profile_name = ACTIVE_PROFILE
    
    profile = PROFILES[profile_name]
    
    global DEFAULT_POSITION_SIZE, MIN_APEX_SCORE, STOP_LOSS_PERCENT
    global TAKE_PROFIT_PERCENT, MAX_DAILY_TRADES
    
    DEFAULT_POSITION_SIZE = profile['position_size']
    MIN_APEX_SCORE = profile['min_apex_score']
    STOP_LOSS_PERCENT = profile['stop_loss']
    TAKE_PROFIT_PERCENT = profile['take_profit']
    MAX_DAILY_TRADES = profile['max_daily_trades']
    
    print(f"✅ Profil '{profile_name}' chargé")
    print(f"   Position: {DEFAULT_POSITION_SIZE*100}%")
    print(f"   Score min: {MIN_APEX_SCORE}")
    print(f"   Stop: {STOP_LOSS_PERCENT*100}%")
    print(f"   Target: {TAKE_PROFIT_PERCENT*100}%")

def validate_config():
    """Valide la configuration"""
    errors = []
    
    if not BINANCE_API_KEY or BINANCE_API_KEY == "ta_clé_api_ici":
        errors.append("❌ Clé API Binance manquante")
    
    if not BINANCE_SECRET_KEY or BINANCE_SECRET_KEY == "ton_secret_ici":
        errors.append("❌ Secret API Binance manquant")
    
    if MIN_APEX_SCORE < 60 or MIN_APEX_SCORE > 100:
        errors.append("❌ MIN_APEX_SCORE doit être entre 60 et 100")
    
    if STOP_LOSS_PERCENT >= TAKE_PROFIT_PERCENT:
        errors.append("❌ Take-profit doit être > Stop-loss")
    
    if MIN_RISK_REWARD_RATIO < 1:
        errors.append("❌ Risk/Reward ratio doit être >= 1")
    
    if errors:
        print("\n⚠️  ERREURS DE CONFIGURATION:")
        for error in errors:
            print(f"   {error}")
        return False
    
    print("✅ Configuration valide")
    return True

def print_config_summary():
    """Affiche un résumé de la config"""
    print("\n" + "="*60)
    print("⚙️  CONFIGURATION APEX PREDATOR BOT")
    print("="*60)
    print(f"💱 Paire: {SYMBOL}")
    print(f"📊 Timeframe: {TIMEFRAME}")
    print(f"💰 Capital: ${INITIAL_CAPITAL}")
    print(f"🎯 Profil: {ACTIVE_PROFILE.upper()}")
    print(f"📈 Position size: {DEFAULT_POSITION_SIZE*100}%")
    print(f"🛡️  Stop-loss: {STOP_LOSS_PERCENT*100}%")
    print(f"🎯 Take-profit: {TAKE_PROFIT_PERCENT*100}%")
    print(f"🎯 APEX score min: {MIN_APEX_SCORE}")
    print(f"🎯 Mode: {'SIMULATION' if DRY_RUN else '⚠️  RÉEL'}")
    print("="*60)

# Auto-validation au chargement
if __name__ == "__main__":
    print("🔧 Test de la configuration...")
    validate_config()
    print_config_summary()
