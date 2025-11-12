# setup_interactive.py - Configuration interactive du bot

import config_apex as config

def display_menu():
    """Affiche le menu principal"""
    print("\n" + "="*70)
    print("⚙️  CONFIGURATION INTERACTIVE - APEX PREDATOR BOT".center(70))
    print("="*70)

def get_capital():
    """Demande le capital de départ"""
    print("\n💰 CAPITAL DE DÉPART")
    print("-" * 40)

    while True:
        try:
            capital_input = input(f"Montant en USDT (défaut: {config.INITIAL_CAPITAL}): ").strip()

            if capital_input == "":
                return config.INITIAL_CAPITAL

            capital = float(capital_input)

            if capital < 10:
                print("⚠️  Capital minimum: 10 USDT")
                continue

            if capital > 10000:
                response = input(f"⚠️  {capital} USDT c'est beaucoup ! Confirmer? (y/n): ")
                if response.lower() != 'y':
                    continue

            return capital

        except ValueError:
            print("❌ Montant invalide. Exemple: 100")

def get_symbol():
    """Demande la paire à trader"""
    print("\n📊 PAIRE À TRADER")
    print("-" * 40)

    # Liste des paires populaires
    popular_pairs = [
        "BTC/USDT",
        "ETH/USDT",
        "BNB/USDT",
        "SOL/USDT",
        "XRP/USDT",
        "ADA/USDT",
        "AVAX/USDT",
        "MATIC/USDT"
    ]

    print("\nPaires populaires:")
    for i, pair in enumerate(popular_pairs, 1):
        default = " (défaut)" if pair == config.SYMBOL else ""
        print(f"  {i}. {pair}{default}")
    print(f"  9. Autre (personnalisé)")

    while True:
        try:
            choice = input(f"\nChoix (1-9, défaut: 2): ").strip()

            if choice == "":
                return config.SYMBOL

            choice_num = int(choice)

            if 1 <= choice_num <= 8:
                return popular_pairs[choice_num - 1]

            elif choice_num == 9:
                custom = input("Paire personnalisée (ex: DOGE/USDT): ").strip().upper()
                if "/" not in custom:
                    print("❌ Format invalide. Utilise: SYMBOL/USDT")
                    continue
                return custom

            else:
                print("❌ Choix invalide")

        except ValueError:
            print("❌ Entrée invalide")

def get_profile():
    """Demande le profil de risque"""
    print("\n🎯 PROFIL DE TRADING")
    print("-" * 40)

    profiles_info = {
        'dynamic': {
            'emoji': '🤖',
            'desc': 'Dynamic (NOUVEAU V2.0)',
            'detail': '🆕 Position 16%, Stop 0.9%, Score min 70, Max 60 trades/jour - Adaptatif & Intelligent'
        },
        'ultra_aggressive': {
            'emoji': '🔥',
            'desc': 'Ultra Agressif',
            'detail': 'Position 25%, Stop 0.6%, Score min 75, Max 80 trades/jour'
        },
        'aggressive': {
            'emoji': '⚡',
            'desc': 'Agressif',
            'detail': 'Position 18%, Stop 0.8%, Score min 78, Max 50 trades/jour'
        },
        'balanced': {
            'emoji': '⚖️',
            'desc': 'Équilibré',
            'detail': 'Position 15%, Stop 1.0%, Score min 82, Max 30 trades/jour'
        },
        'conservative': {
            'emoji': '🛡️',
            'desc': 'Conservateur',
            'detail': 'Position 10%, Stop 1.2%, Score min 88, Max 20 trades/jour'
        }
    }

    print("\nProfils disponibles:")
    profile_list = list(profiles_info.keys())

    for i, (key, info) in enumerate(profiles_info.items(), 1):
        default = " (défaut)" if key == config.ACTIVE_PROFILE else ""
        print(f"  {i}. {info['emoji']} {info['desc']}{default}")
        print(f"     → {info['detail']}")

    while True:
        try:
            choice = input(f"\nChoix (1-5, défaut: 1 Dynamic): ").strip()

            if choice == "":
                return config.ACTIVE_PROFILE  # Dynamic par défaut

            choice_num = int(choice)

            if 1 <= choice_num <= 5:
                return profile_list[choice_num - 1]

            else:
                print("❌ Choix invalide")

        except ValueError:
            print("❌ Entrée invalide")

def get_observation_time():
    """Demande le temps d'observation"""
    print("\n⏱️  PHASE D'OBSERVATION")
    print("-" * 40)
    print("Temps d'observation avant le premier trade")
    print("(Le bot peut quand même trader si APEX Score > 92)")

    while True:
        try:
            time_input = input(f"Durée en minutes (défaut: {config.MIN_OBSERVATION_TIME/60:.0f}): ").strip()

            if time_input == "":
                return config.MIN_OBSERVATION_TIME

            minutes = float(time_input)

            if minutes < 0:
                print("⚠️  Durée minimum: 0 minutes (désactivé)")
                continue

            if minutes > 60:
                response = input(f"⚠️  {minutes} minutes c'est long ! Confirmer? (y/n): ")
                if response.lower() != 'y':
                    continue

            return int(minutes * 60)  # Convertit en secondes

        except ValueError:
            print("❌ Durée invalide. Exemple: 30")

def get_dry_run_mode():
    """Demande le mode simulation/réel"""
    print("\n🎮 MODE DE FONCTIONNEMENT")
    print("-" * 40)

    print("1. 🎮 SIMULATION (recommandé pour débuter)")
    print("   → Aucun risque, teste le bot gratuitement")
    print("2. ⚠️  RÉEL (attention !)")
    print("   → Utilise de l'argent réel sur Binance")

    while True:
        choice = input(f"\nChoix (1-2, défaut: 1): ").strip()

        if choice == "" or choice == "1":
            return True  # DRY_RUN = True

        elif choice == "2":
            print("\n⚠️  MODE RÉEL SÉLECTIONNÉ!")
            print("Le bot va trader avec de l'argent réel sur Binance.")
            confirm = input("Es-tu VRAIMENT sûr ? (tape 'OUI' en majuscules): ")

            if confirm == "OUI":
                return False  # DRY_RUN = False
            else:
                print("Retour au mode simulation")
                return True

        else:
            print("❌ Choix invalide")

def print_config_summary(capital, symbol, profile, observation_time, dry_run):
    """Affiche un résumé de la configuration"""
    print("\n" + "="*70)
    print("📋 RÉSUMÉ DE LA CONFIGURATION".center(70))
    print("="*70)

    print(f"\n💰 Capital: ${capital:.2f} USDT")
    print(f"📊 Paire: {symbol}")
    print(f"🎯 Profil: {profile.upper()}")
    print(f"⏱️  Observation: {observation_time/60:.0f} minutes")
    print(f"🎮 Mode: {'SIMULATION' if dry_run else '⚠️  RÉEL'}")

    profile_details = config.PROFILES[profile]
    print(f"\n📊 Détails du profil:")
    print(f"   Position size: {profile_details['position_size']*100:.0f}%")
    print(f"   Stop-loss: {profile_details['stop_loss']*100:.2f}%")
    print(f"   Take-profit: {profile_details['take_profit']*100:.2f}%")
    print(f"   Score min: {profile_details['min_apex_score']}")
    print(f"   Max trades/jour: {profile_details['max_daily_trades']}")

    print("\n" + "="*70)

def confirm_config():
    """Demande confirmation"""
    print("\n❓ Confirmer cette configuration ?")
    response = input("(y/n): ").strip().lower()
    return response == 'y' or response == 'yes' or response == 'o' or response == 'oui'

def run_interactive_setup():
    """Lance le setup interactif complet"""
    display_menu()

    print("\n🚀 Bienvenue ! Configurons ton bot de trading ensemble.")
    print("Appuie sur ENTRÉE pour utiliser la valeur par défaut.\n")

    while True:
        # Récupère toutes les configurations
        capital = get_capital()
        symbol = get_symbol()
        profile = get_profile()
        observation_time = get_observation_time()
        dry_run = get_dry_run_mode()

        # Affiche le résumé
        print_config_summary(capital, symbol, profile, observation_time, dry_run)

        # Demande confirmation
        if confirm_config():
            break
        else:
            print("\n🔄 Recommençons...")

    # Applique la configuration
    config.INITIAL_CAPITAL = capital
    config.SYMBOL = symbol
    config.ACTIVE_PROFILE = profile
    config.MIN_OBSERVATION_TIME = observation_time
    config.DRY_RUN = dry_run

    # Charge le profil
    config.load_profile(profile)

    print("\n✅ Configuration enregistrée !")
    print("🚀 Démarrage du bot...")

    return {
        'capital': capital,
        'symbol': symbol,
        'profile': profile,
        'observation_time': observation_time,
        'dry_run': dry_run
    }

# Test du module
if __name__ == "__main__":
    print("🚀 Test du setup interactif")
    result = run_interactive_setup()
    print(f"\n✅ Config finale: {result}")
