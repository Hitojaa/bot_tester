# main_apex.py - BOT APEX PREDATOR ULTIME 🦈

"""
═══════════════════════════════════════════════════════════════
    APEX PREDATOR BOT - Le Meilleur Bot de Scalping au Monde
═══════════════════════════════════════════════════════════════

Fonctionnalités PRO:
- IA Multi-Layer (Macro/Méso/Micro)
- Volume Profile + VWAP
- 18+ Patterns de chandeliers
- Support/Résistance dynamiques
- Order Flow Analysis
- Multi-target exits
- Trailing stop automatique
- APEX Score (0-100)

Créé avec ❤️ et beaucoup de café ☕
"""

import time
import sys
from datetime import datetime, timedelta
import config_apex as config
from data_collector_apex import DataCollectorApex
from indicators_advanced import AdvancedIndicators
from ai_apex import ApexAI
from trader_apex import TraderApex
from setup_interactive import run_interactive_setup

class ApexPredatorBot:
    """Le Bot de Scalping PRO Ultime"""
    
    def __init__(self):
        """Initialise le bot APEX"""
        self.print_banner()
        
        print("🚀 INITIALISATION DU BOT APEX PREDATOR")
        print("="*70)
        
        # Validation config
        if not config.validate_config():
            print("\n❌ Configuration invalide. Arrêt.")
            sys.exit(1)
        
        # Charge le profil
        config.load_profile(config.ACTIVE_PROFILE)
        
        # Initialise les composants
        print("\n📦 Chargement des modules...")
        self.collector = DataCollectorApex()
        self.ai = ApexAI()
        self.trader = TraderApex()
        
        # État
        self.running = False
        self.iteration = 0
        self.session_start = datetime.now()
        self.observation_start = None
        self.can_trade = False
        
        # Stats session
        self.stats = {
            'analyses': 0,
            'signals_detected': 0,
            'trades_executed': 0,
            'apex_scores': []
        }
        
        print("\n✅ BOT APEX PREDATOR PRÊT!")
        config.print_config_summary()
    
    def print_banner(self):
        """Affiche la bannière APEX"""
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         🦈  APEX PREDATOR BOT  🦈                            ║
║                                                               ║
║         Le Meilleur Bot de Scalping au Monde                 ║
║                                                               ║
║    🧠 IA Multi-Layer  |  📊 Volume Profile  |  🎯 18+ Patterns║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def start_observation_phase(self):
        """Phase d'observation avant le 1er trade"""
        self.observation_start = datetime.now()
        
        observation_time = config.MIN_OBSERVATION_TIME / 60  # En minutes
        
        print("\n" + "="*70)
        print("🔍 PHASE D'OBSERVATION".center(70))
        print("="*70)
        print(f"\n⏳ Le bot va observer le marché pendant {observation_time:.0f} minutes")
        print("📊 Analyse approfondie en cours...")
        print("💡 Aucun trade ne sera pris pendant cette phase")
        print("🎯 Objectif: Comprendre le marché avant d'attaquer\n")
    
    def is_observation_complete(self):
        """Vérifie si la phase d'observation est terminée"""
        if self.observation_start is None:
            return False
        
        elapsed = (datetime.now() - self.observation_start).total_seconds()
        return elapsed >= config.MIN_OBSERVATION_TIME
    
    def run_iteration(self):
        """Une itération du bot"""
        self.iteration += 1
        self.stats['analyses'] += 1
        
        print("\n" + "="*70)
        print(f"🔄 ITÉRATION #{self.iteration} - {datetime.now().strftime('%H:%M:%S')}".center(70))
        print("="*70)
        
        try:
            # 1. Récupère les données
            print("\n📊 Récupération des données...")
            df = self.collector.get_historical_data(limit=config.DATA_FETCH_LIMIT)
            
            if df is None or len(df) < config.MIN_CANDLES_BEFORE_TRADE:
                print("❌ Pas assez de données")
                return
            
            print(f"✅ {len(df)} bougies récupérées")
            
            # 2. Calcule les indicateurs
            print("🔢 Calcul des indicateurs avancés...")
            df = AdvancedIndicators.calculate_all(df)
            
            # 3. Prix actuel
            current_price = df.iloc[-1]['close']
            
            # 4. Affiche les indicateurs
            if config.SHOW_INDICATORS:
                AdvancedIndicators.print_current_indicators(df)
            
            # 5. Analyse Order Flow
            if config.SHOW_ORDER_FLOW and self.iteration % 5 == 0:
                print("\n📊 Analyse Order Flow...")
                order_flow = self.collector.get_market_depth_analysis()
                if order_flow:
                    self.collector.print_order_flow_analysis(order_flow)
            
            # 6. Analyse IA COMPLÈTE
            print("\n🧠 Analyse IA APEX en cours...")
            analysis = self.ai.analyze_complete(df)
            
            if not analysis:
                print("❌ Analyse IA impossible")
                return
            
            # Affiche l'analyse
            self.ai.print_analysis(analysis)
            
            # Enregistre le score
            self.stats['apex_scores'].append(analysis['apex_score']['total_score'])
            
            # 7. Vérifie phase d'observation
            if not self.can_trade:
                if not self.is_observation_complete():
                    remaining = config.MIN_OBSERVATION_TIME - (datetime.now() - self.observation_start).total_seconds()
                    print(f"\n⏳ Phase d'observation: {remaining/60:.1f} minutes restantes")

                    # EMERGENCY BUY : Si opportunité EXCEPTIONNELLE, trade quand même !
                    apex_score = analysis['apex_score']['total_score']
                    if apex_score >= 92 and analysis['decision']['action'] == 'buy':
                        print(f"\n🚨 OPPORTUNITÉ EXCEPTIONNELLE DÉTECTÉE!")
                        print(f"   APEX Score: {apex_score:.1f}/100 (>92)")
                        print(f"   🔥 EMERGENCY BUY activé - Phase d'observation ignorée!")
                        self.can_trade = True  # Active temporairement
                    else:
                        return
                else:
                    self.can_trade = True
                    print("\n✅ PHASE D'OBSERVATION TERMINÉE!")
                    print("🦈 Le bot peut maintenant attaquer!")
            
            # 8. Gestion des positions existantes
            if self.trader.has_position():
                self._manage_open_position(current_price, df, analysis)
            
            # 9. Cherche opportunités d'achat
            else:
                self._look_for_entry(current_price, df, analysis)
            
            # 10. Stats toutes les 10 itérations
            if self.iteration % config.STATS_DISPLAY_FREQUENCY == 0:
                self._print_session_stats()
        
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"\n❌ Erreur dans l'itération: {e}")
            import traceback
            traceback.print_exc()
    
    def _manage_open_position(self, current_price, df, analysis):
        """Gère une position ouverte"""
        position = self.trader.get_position_info()
        
        print(f"\n📍 POSITION OUVERTE")
        print("="*70)
        
        entry_price = position['entry_price']
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        pnl_usdt = (current_price - entry_price) * position['quantity']
        
        emoji = "🟢" if pnl_percent > 0 else "🔴"
        print(f"💰 Entrée: ${entry_price:.2f}")
        print(f"💰 Actuel: ${current_price:.2f}")
        print(f"{emoji} P&L: {pnl_percent:+.2f}% (${pnl_usdt:+.2f})")
        print(f"🛡️  Stop: ${position['stop_loss']:.2f}")
        print(f"🎯 Target: ${position['take_profit']:.2f}")
        
        if position['targets_hit']:
            print(f"✅ Targets atteints: {', '.join(position['targets_hit'])}")
        
        # Vérifie multi-targets
        target_hit = self.trader.check_multi_target_exit(current_price)
        
        # Vérifie stop-loss
        if current_price <= position['stop_loss']:
            print(f"\n🛑 STOP-LOSS ATTEINT!")
            self.trader.sell(current_price, "Stop-loss")
            return
        
        # Vérifie take-profit
        if current_price >= position['take_profit']:
            print(f"\n🎯 TAKE-PROFIT ATTEINT!")
            self.trader.sell(current_price, "Take-profit")
            return
        
        # Vérifie signal de sortie IA
        if analysis['decision']['action'] == 'sell' and analysis['confidence'] >= 80:
            print(f"\n⚠️  SIGNAL DE SORTIE IA (Confiance: {analysis['confidence']:.0f}%)")
            response = input("Fermer la position maintenant? (y/n): ")
            if response.lower() == 'y':
                self.trader.sell(current_price, "Signal IA")
                return
        
        print("\n⏳ Maintien de la position")
    
    def _look_for_entry(self, current_price, df, analysis):
        """Cherche une opportunité d'entrée"""
        print(f"\n💼 RECHERCHE D'OPPORTUNITÉ")
        print("="*70)
        
        apex_score = analysis['apex_score']['total_score']
        decision = analysis['decision']
        
        print(f"🎯 APEX Score: {apex_score:.1f}/100")
        print(f"📊 Décision: {decision['recommendation']}")
        print(f"💪 Force: {decision['strength'].upper()}")
        
        # Vérifie si le score est suffisant
        if apex_score < config.MIN_APEX_SCORE:
            print(f"\n⏳ Score insuffisant (min: {config.MIN_APEX_SCORE})")
            print("   Attente d'un meilleur setup...")
            return
        
        # Signal d'achat détecté !
        if decision['action'] == 'buy':
            self.stats['signals_detected'] += 1
            
            print(f"\n🚨 SIGNAL D'ACHAT DÉTECTÉ!")
            print(f"   APEX Score: {apex_score:.1f}/100 ✅")
            print(f"   Confiance: {analysis['confidence']:.0f}%")
            
            # Calcule stop-loss et take-profit
            atr = df.iloc[-1]['atr']
            regime = analysis['market_regime']
            
            # Stop-loss adaptatif
            stop_distance = max(
                config.STOP_LOSS_PERCENT,
                (atr / current_price) * config.ATR_MULTIPLIER
            )
            stop_loss = current_price * (1 - stop_distance)
            
            # Take-profit adaptatif
            take_profit = current_price * (1 + config.TAKE_PROFIT_PERCENT)
            
            # Vérifie Risk/Reward
            risk = current_price - stop_loss
            reward = take_profit - current_price
            rr_ratio = reward / risk if risk > 0 else 0
            
            print(f"\n📊 ANALYSE DU TRADE:")
            print(f"   Prix entrée: ${current_price:.2f}")
            print(f"   Stop-loss:   ${stop_loss:.2f} (-{stop_distance*100:.2f}%)")
            print(f"   Take-profit: ${take_profit:.2f} (+{config.TAKE_PROFIT_PERCENT*100:.2f}%)")
            print(f"   R/R Ratio:   {rr_ratio:.2f}:1")
            
            # Vérifie si le trade est acceptable
            if rr_ratio < config.MIN_RISK_REWARD_RATIO:
                print(f"\n❌ R/R ratio insuffisant (min: {config.MIN_RISK_REWARD_RATIO}:1)")
                return
            
            # Calcule la taille de position
            capital = config.INITIAL_CAPITAL + self.trader.total_profit
            position_size = capital * config.DEFAULT_POSITION_SIZE
            quantity = position_size / current_price
            
            print(f"\n💰 POSITION:")
            print(f"   Capital disponible: ${capital:.2f}")
            print(f"   Taille position: ${position_size:.2f} ({config.DEFAULT_POSITION_SIZE*100:.0f}%)")
            print(f"   Quantité: {quantity:.6f} {config.SYMBOL.split('/')[0]}")
            
            # Confirmation (en mode non-verbose)
            if not config.DRY_RUN:
                print(f"\n⚠️  MODE RÉEL ACTIVÉ!")
                response = input("Exécuter ce trade? (y/n): ")
                if response.lower() != 'y':
                    print("❌ Trade annulé")
                    return
            
            # EXÉCUTE LE TRADE !
            print(f"\n🚀 EXÉCUTION DU TRADE...")
            position = self.trader.buy(current_price, quantity, stop_loss, take_profit)
            
            if position:
                self.stats['trades_executed'] += 1
                print(f"✅ POSITION OUVERTE AVEC SUCCÈS!")
            else:
                print(f"❌ Échec de l'ouverture de position")
        
        else:
            print(f"\n⏳ Pas de signal d'achat")
            print(f"   Action recommandée: {decision['action'].upper()}")
    
    def _print_session_stats(self):
        """Affiche les stats de la session"""
        duration = datetime.now() - self.session_start
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        
        print("\n" + "="*70)
        print("📊 STATISTIQUES DE SESSION".center(70))
        print("="*70)
        
        print(f"\n⏱️  Durée: {hours}h {minutes}min")
        print(f"🔄 Itérations: {self.iteration}")
        print(f"📊 Analyses: {self.stats['analyses']}")
        print(f"🚨 Signaux détectés: {self.stats['signals_detected']}")
        print(f"💼 Trades exécutés: {self.stats['trades_executed']}")
        
        if self.stats['apex_scores']:
            avg_score = sum(self.stats['apex_scores']) / len(self.stats['apex_scores'])
            max_score = max(self.stats['apex_scores'])
            print(f"\n🎯 APEX Score moyen: {avg_score:.1f}/100")
            print(f"🎯 APEX Score max: {max_score:.1f}/100")
        
        # Performance trading
        perf = self.trader.get_performance_summary()
        if perf['total_trades'] > 0:
            print(f"\n💰 TRADING:")
            print(f"   Trades: {perf['total_trades']}")
            print(f"   Win rate: {perf['win_rate']:.1f}%")
            print(f"   Profit total: ${perf['total_profit']:+.2f}")
        
        print("="*70)
    
    def start(self):
        """Démarre le bot"""
        print("\n🚀 DÉMARRAGE DU BOT APEX PREDATOR")
        print("="*70)
        print(f"⏱️  Analyse toutes les {config.ANALYSIS_INTERVAL} secondes")
        print(f"📊 Timeframe: {config.TIMEFRAME}")
        print(f"💰 Capital: ${config.INITIAL_CAPITAL}")
        print(f"🎯 Profil: {config.ACTIVE_PROFILE.upper()}")
        print("\n⌨️  Appuie sur Ctrl+C pour arrêter proprement\n")
        
        self.running = True
        self.start_observation_phase()
        
        try:
            while self.running:
                self.run_iteration()
                
                if self.running:
                    time.sleep(config.ANALYSIS_INTERVAL)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Arrêt demandé...")
            self.stop()
        
        except Exception as e:
            print(f"\n\n❌ Erreur critique: {e}")
            import traceback
            traceback.print_exc()
            self.stop()
    
    def stop(self):
        """Arrête le bot proprement"""
        print("\n" + "="*70)
        print("🛑 ARRÊT DU BOT APEX PREDATOR".center(70))
        print("="*70)
        
        self.running = False
        
        # Position ouverte ?
        if self.trader.has_position():
            print("\n⚠️  POSITION ENCORE OUVERTE!")
            position = self.trader.get_position_info()
            current_price = self.collector.get_current_price()
            
            if current_price:
                pnl = ((current_price - position['entry_price']) / position['entry_price']) * 100
                print(f"   P&L actuel: {pnl:+.2f}%")
            
            response = input("\nFermer la position maintenant? (y/n): ")
            if response.lower() == 'y':
                if current_price:
                    self.trader.sell(current_price, "Arrêt du bot")
        
        # Rapport final
        self._generate_final_report()
        
        print("\n👋 Au revoir et bon trading!")
    
    def _generate_final_report(self):
        """Génère le rapport final de session"""
        duration = datetime.now() - self.session_start
        
        print("\n" + "="*70)
        print("📊 RAPPORT FINAL DE SESSION".center(70))
        print("="*70)
        
        # Durée
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        print(f"\n⏱️  Durée totale: {hours}h {minutes}min")
        print(f"🔄 Itérations: {self.iteration}")
        
        # Stats trading
        self.trader.print_performance()
        
        # Conseils
        perf = self.trader.get_performance_summary()
        
        print("\n💡 RECOMMANDATIONS:")
        
        if perf['total_trades'] == 0:
            print("  • Aucun trade exécuté - Le bot était trop strict")
            print("  • Conseil: Baisse MIN_APEX_SCORE ou laisse tourner plus longtemps")
        
        elif perf['win_rate'] < 40:
            print("  • ⚠️  Win rate faible - Analyse ta stratégie")
            print("  • Conseil: Augmente MIN_APEX_SCORE pour être plus sélectif")
        
        elif perf['win_rate'] > 60:
            print("  • ✅ Excellent win rate! Continue comme ça")
            print("  • Conseil: Tu peux peut-être augmenter la position size")
        
        else:
            print("  • 📊 Win rate acceptable")
            print("  • Continue d'optimiser les paramètres")
        
        print("\n📚 PROCHAINES ÉTAPES:")
        print("  • Laisse tourner au moins 2-3 jours pour des stats fiables")
        print("  • Note les patterns qui fonctionnent le mieux")
        print("  • Ajuste UN paramètre à la fois")
        print("  • Augmente le capital progressivement si profitable")
        
        print("\n" + "="*70)


def main():
    """Point d'entrée principal"""
    try:
        # Lance le setup interactif
        print("🔧 Configuration du bot...")
        user_wants_interactive = input("\nUtiliser la configuration interactive? (y/n, défaut: y): ").strip().lower()

        if user_wants_interactive != 'n' and user_wants_interactive != 'non':
            run_interactive_setup()
        else:
            print("✅ Utilisation de la configuration par défaut")

        # Crée et démarre le bot
        bot = ApexPredatorBot()
        bot.start()

    except KeyboardInterrupt:
        print("\n\n👋 Au revoir!")

    except Exception as e:
        print(f"\n\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
