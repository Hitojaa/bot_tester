# trader_apex.py - Exécution des ordres (APEX)

import ccxt
from datetime import datetime
import config_apex as config
from logger_apex import get_logger

class TraderApex:
    """Exécuteur d'ordres ultra-rapide - APEX"""
    
    def __init__(self):
        """Initialise le trader"""
        self.logger = get_logger()

        try:
            if not config.DRY_RUN:
                self.exchange = ccxt.binance({
                    'apiKey': config.BINANCE_API_KEY,
                    'secret': config.BINANCE_SECRET_KEY,
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'}
                })
                self.exchange.load_markets()
            else:
                self.exchange = None

            # État
            self.position = None
            self.positions_history = []
            self.total_profit = 0
            self.wins = 0
            self.losses = 0

            mode = "SIMULATION" if config.DRY_RUN else "RÉEL"
            print(f"✅ Trader APEX initialisé ({mode})")
            self.logger.info(f"Trader APEX initialisé en mode {mode}")

        except Exception as e:
            print(f"❌ Erreur init trader: {e}")
            self.logger.error(f"Erreur init trader: {e}")
            self.exchange = None
    
    def buy(self, current_price, quantity, stop_loss, take_profit):
        """
        Exécute un ordre d'ACHAT
        
        Returns:
            dict: Détails de la position
        """
        if self.position is not None:
            print("⚠️  Position déjà ouverte")
            return None
        
        try:
            # Mode simulation
            if config.DRY_RUN or self.exchange is None:
                self.position = {
                    'entry_price': current_price,
                    'quantity': quantity,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'entry_time': datetime.now(),
                    'targets_hit': [],
                    'mode': 'simulation'
                }
                
                cost = quantity * current_price
                print(f"\n🟢 ACHAT SIMULÉ")
                print(f"   Prix: ${current_price:.2f}")
                print(f"   Quantité: {quantity:.6f} {config.SYMBOL.split('/')[0]}")
                print(f"   Coût: ${cost:.2f}")
                print(f"   Stop: ${stop_loss:.2f} ({((stop_loss-current_price)/current_price)*100:.2f}%)")
                print(f"   Target: ${take_profit:.2f} ({((take_profit-current_price)/current_price)*100:+.2f}%)")

                self.logger.trade("BUY", current_price, quantity, "SIMULATION")

                return self.position
            
            # Mode réel
            else:
                order = self.exchange.create_market_buy_order(
                    config.SYMBOL,
                    quantity
                )
                
                self.position = {
                    'entry_price': order['price'],
                    'quantity': order['amount'],
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'entry_time': datetime.now(),
                    'order_id': order['id'],
                    'targets_hit': [],
                    'mode': 'real'
                }
                
                print(f"\n🟢 ACHAT RÉEL EXÉCUTÉ")
                print(f"   Order ID: {order['id']}")
                print(f"   Prix: ${order['price']:.2f}")
                print(f"   Quantité: {order['amount']:.6f}")
                
                return self.position
                
        except Exception as e:
            print(f"❌ Erreur achat: {e}")
            return None
    
    def sell(self, current_price, reason=""):
        """
        Exécute un ordre de VENTE (fermeture position)
        
        Returns:
            dict: Résultat du trade
        """
        if self.position is None:
            print("⚠️  Aucune position à fermer")
            return None
        
        try:
            entry_price = self.position['entry_price']
            quantity = self.position['quantity']
            
            # Calcule profit
            profit_percent = ((current_price - entry_price) / entry_price) * 100
            profit_usdt = (current_price - entry_price) * quantity
            
            # Frais
            fees = (entry_price * quantity + current_price * quantity) * config.BINANCE_FEE
            net_profit = profit_usdt - fees
            
            trade_result = {
                'entry_price': entry_price,
                'exit_price': current_price,
                'quantity': quantity,
                'profit_percent': profit_percent,
                'profit_usdt': net_profit,
                'entry_time': self.position['entry_time'],
                'exit_time': datetime.now(),
                'duration': datetime.now() - self.position['entry_time'],
                'reason': reason,
                'targets_hit': self.position['targets_hit']
            }
            
            # Mode simulation
            if config.DRY_RUN or self.position.get('mode') == 'simulation':
                print(f"\n🔴 VENTE SIMULÉE")
                print(f"   Prix: ${current_price:.2f}")
                print(f"   Profit: ${net_profit:+.2f} ({profit_percent:+.2f}%)")
                print(f"   Raison: {reason}")

                self.logger.trade("SELL", current_price, quantity, f"{reason} | P&L: ${net_profit:+.2f}")
            
            # Mode réel
            else:
                order = self.exchange.create_market_sell_order(
                    config.SYMBOL,
                    quantity
                )
                
                print(f"\n🔴 VENTE RÉELLE EXÉCUTÉE")
                print(f"   Order ID: {order['id']}")
                print(f"   Prix: ${order['price']:.2f}")
                print(f"   Profit net: ${net_profit:+.2f}")
            
            # Stats
            self.total_profit += net_profit
            if net_profit > 0:
                self.wins += 1
            else:
                self.losses += 1
            
            # Historique
            self.positions_history.append(trade_result)
            self.position = None
            
            return trade_result
            
        except Exception as e:
            print(f"❌ Erreur vente: {e}")
            return None
    
    def check_multi_target_exit(self, current_price):
        """
        Vérifie les sorties multi-targets
        Ferme partiellement la position
        """
        if self.position is None:
            return False
        
        entry_price = self.position['entry_price']
        profit_percent = ((current_price - entry_price) / entry_price) * 100
        
        # Target 1 : +1.5% (ferme 50%)
        if (profit_percent >= config.FIRST_TARGET_PERCENT * 100 and 
            'target1' not in self.position['targets_hit']):
            
            print(f"\n🎯 TARGET 1 ATTEINT (+{config.FIRST_TARGET_PERCENT*100:.1f}%)")
            print(f"   Fermeture de 50% de la position")
            
            self.position['targets_hit'].append('target1')
            self.position['quantity'] *= 0.5  # Garde 50%
            
            # Ajuste le stop-loss au breakeven
            self.position['stop_loss'] = entry_price
            print(f"   Stop ajusté au breakeven: ${entry_price:.2f}")
            
            return True
        
        # Target 2 : +2.5% (ferme 60% du reste = 30% du total)
        if (profit_percent >= config.SECOND_TARGET_PERCENT * 100 and 
            'target2' not in self.position['targets_hit'] and
            'target1' in self.position['targets_hit']):
            
            print(f"\n🎯 TARGET 2 ATTEINT (+{config.SECOND_TARGET_PERCENT*100:.1f}%)")
            print(f"   Fermeture de 30% supplémentaires")
            
            self.position['targets_hit'].append('target2')
            self.position['quantity'] *= 0.4  # Garde 20%
            
            # Trail le stop
            new_stop = current_price * (1 - config.TRAILING_STOP_DISTANCE)
            self.position['stop_loss'] = max(self.position['stop_loss'], new_stop)
            print(f"   Stop trail à: ${self.position['stop_loss']:.2f}")
            
            return True
        
        # Target 3 : +4% (laisse runner les 20% restants)
        if (profit_percent >= config.THIRD_TARGET_PERCENT * 100 and 
            'target3' not in self.position['targets_hit']):
            
            print(f"\n🎯 TARGET 3 ATTEINT (+{config.THIRD_TARGET_PERCENT*100:.1f}%)")
            print(f"   Position finale (20%) laissée runner")
            
            self.position['targets_hit'].append('target3')
            
            # Trail agressif
            new_stop = current_price * (1 - config.TRAILING_STOP_DISTANCE * 0.7)
            self.position['stop_loss'] = max(self.position['stop_loss'], new_stop)
            print(f"   Stop trail agressif à: ${self.position['stop_loss']:.2f}")
            
            return True
        
        return False
    
    def has_position(self):
        """Vérifie si une position est ouverte"""
        return self.position is not None
    
    def get_position_info(self):
        """Retourne les infos de la position actuelle"""
        return self.position
    
    def get_performance_summary(self):
        """Retourne un résumé des performances"""
        total_trades = self.wins + self.losses
        win_rate = (self.wins / total_trades * 100) if total_trades > 0 else 0
        
        avg_profit = 0
        avg_win = 0
        avg_loss = 0
        
        if self.positions_history:
            avg_profit = sum(p['profit_usdt'] for p in self.positions_history) / len(self.positions_history)
            
            wins = [p['profit_usdt'] for p in self.positions_history if p['profit_usdt'] > 0]
            losses = [p['profit_usdt'] for p in self.positions_history if p['profit_usdt'] < 0]
            
            if wins:
                avg_win = sum(wins) / len(wins)
            if losses:
                avg_loss = sum(losses) / len(losses)
        
        return {
            'total_trades': total_trades,
            'winning_trades': self.wins,
            'losing_trades': self.losses,
            'win_rate': win_rate,
            'total_profit': self.total_profit,
            'avg_profit': avg_profit,
            'avg_win': avg_win,
            'avg_loss': avg_loss
        }
    
    def print_performance(self):
        """Affiche les performances"""
        perf = self.get_performance_summary()
        
        print("\n" + "="*60)
        print("📊 PERFORMANCES TRADER APEX")
        print("="*60)
        
        print(f"\n💰 Profit total: ${perf['total_profit']:+.2f}")
        print(f"📊 Trades: {perf['total_trades']}")
        print(f"✅ Gagnants: {perf['winning_trades']}")
        print(f"❌ Perdants: {perf['losing_trades']}")
        print(f"📈 Win rate: {perf['win_rate']:.1f}%")
        
        if perf['total_trades'] > 0:
            print(f"\n💵 Profit moyen: ${perf['avg_profit']:+.2f}")
            if perf['winning_trades'] > 0:
                print(f"✅ Gain moyen: ${perf['avg_win']:+.2f}")
            if perf['losing_trades'] > 0:
                print(f"❌ Perte moyenne: ${perf['avg_loss']:+.2f}")
        
        print("="*60)


# Test du module
if __name__ == "__main__":
    print("🚀 Test du Trader APEX")
    
    trader = TraderApex()
    
    print("\n✅ Trader opérationnel")
    print("📊 Capacités:")
    print("  - Exécution market orders")
    print("  - Multi-target exits (3 niveaux)")
    print("  - Trailing stop automatique")
    print("  - Historique des trades")
    print("  - Stats de performance")
