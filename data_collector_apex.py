# data_collector_apex.py - Collecteur de données Binance (APEX)

import ccxt
import pandas as pd
from datetime import datetime
import time
import config_apex as config
from logger_apex import get_logger

class DataCollectorApex:
    """Collecteur de données depuis Binance - Version APEX"""
    
    def __init__(self):
        """Initialise la connexion Binance"""
        self.logger = get_logger()

        try:
            self.exchange = ccxt.binance({
                'apiKey': config.BINANCE_API_KEY,
                'secret': config.BINANCE_SECRET_KEY,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'
                }
            })

            # Test de connexion
            self.exchange.load_markets()
            print("✅ Connexion Binance établie")
            self.logger.info("Connexion Binance établie")

        except Exception as e:
            print(f"❌ Erreur connexion Binance: {e}")
            self.logger.error(f"Erreur connexion Binance: {e}")
            self.exchange = None

    def _retry_api_call(self, func, max_retries=3, delay=2):
        """
        Exécute un appel API avec retry en cas d'erreur

        Args:
            func: Fonction à exécuter
            max_retries: Nombre de tentatives max
            delay: Délai entre les tentatives (secondes)

        Returns:
            Résultat de la fonction ou None
        """
        for attempt in range(max_retries):
            try:
                return func()
            except ccxt.NetworkError as e:
                if attempt < max_retries - 1:
                    print(f"⚠️  Erreur réseau (tentative {attempt + 1}/{max_retries})")
                    self.logger.warning(f"Erreur réseau, retry dans {delay}s: {e}")
                    time.sleep(delay)
                else:
                    print(f"❌ Échec après {max_retries} tentatives")
                    self.logger.error(f"Échec après {max_retries} tentatives: {e}")
                    return None
            except Exception as e:
                print(f"❌ Erreur API: {e}")
                self.logger.error(f"Erreur API: {e}")
                return None
    
    def get_historical_data(self, symbol=None, timeframe=None, limit=500):
        """
        Récupère les données historiques avec retry automatique

        Args:
            symbol: Paire (défaut: config)
            timeframe: Timeframe (défaut: config)
            limit: Nombre de bougies

        Returns:
            DataFrame: OHLCV
        """
        if self.exchange is None:
            print("❌ Pas de connexion Binance")
            return None

        if symbol is None:
            symbol = config.SYMBOL
        if timeframe is None:
            timeframe = config.TIMEFRAME

        def fetch_data():
            # Récupère les bougies
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

            # Convertit en DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )

            # Convertit timestamp en datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            if config.VERBOSE:
                print(f"✅ {len(df)} bougies récupérées pour {symbol} ({timeframe})")

            return df

        # Utilise le retry mechanism
        return self._retry_api_call(fetch_data)
    
    def get_current_price(self, symbol=None):
        """Récupère le prix actuel"""
        if self.exchange is None:
            return None
        
        if symbol is None:
            symbol = config.SYMBOL
        
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"❌ Erreur prix: {e}")
            return None
    
    def get_order_book(self, symbol=None, limit=20):
        """
        Récupère le carnet d'ordres (Order Book)
        Pour analyse Order Flow
        """
        if self.exchange is None:
            return None
        
        if symbol is None:
            symbol = config.SYMBOL
        
        try:
            order_book = self.exchange.fetch_order_book(symbol, limit=limit)
            
            return {
                'bids': order_book['bids'],  # Ordres d'achat
                'asks': order_book['asks'],  # Ordres de vente
                'timestamp': order_book['timestamp']
            }
        except Exception as e:
            print(f"❌ Erreur order book: {e}")
            return None
    
    def analyze_order_book_imbalance(self, order_book):
        """
        Analyse le déséquilibre du carnet d'ordres
        
        Returns:
            dict: Analyse du déséquilibre
        """
        if not order_book:
            return None
        
        # Calcule le volume total des bids et asks
        total_bid_volume = sum([bid[1] for bid in order_book['bids'][:10]])
        total_ask_volume = sum([ask[1] for ask in order_book['asks'][:10]])
        
        total_volume = total_bid_volume + total_ask_volume
        
        if total_volume == 0:
            return None
        
        # Ratio acheteurs/vendeurs
        bid_ratio = total_bid_volume / total_volume
        ask_ratio = total_ask_volume / total_volume
        
        # Déséquilibre
        imbalance = bid_ratio - ask_ratio
        
        # Interprétation
        if imbalance > config.DELTA_VOLUME_THRESHOLD:
            signal = 'bullish'
            strength = min(abs(imbalance) * 100, 100)
        elif imbalance < -config.DELTA_VOLUME_THRESHOLD:
            signal = 'bearish'
            strength = min(abs(imbalance) * 100, 100)
        else:
            signal = 'neutral'
            strength = 0
        
        return {
            'bid_volume': total_bid_volume,
            'ask_volume': total_ask_volume,
            'bid_ratio': bid_ratio * 100,
            'ask_ratio': ask_ratio * 100,
            'imbalance': imbalance,
            'signal': signal,
            'strength': strength
        }
    
    def get_recent_trades(self, symbol=None, limit=100):
        """Récupère les trades récents (Time & Sales)"""
        if self.exchange is None:
            return None
        
        if symbol is None:
            symbol = config.SYMBOL
        
        try:
            trades = self.exchange.fetch_trades(symbol, limit=limit)
            
            df = pd.DataFrame(trades)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
            
        except Exception as e:
            print(f"❌ Erreur trades: {e}")
            return None
    
    def detect_large_orders(self, trades_df):
        """
        Détecte les gros ordres (institutionnels)
        """
        if trades_df is None or len(trades_df) == 0:
            return []
        
        # Calcule la taille moyenne des trades
        avg_size = trades_df['amount'].mean()
        
        # Gros ordre = 10x la moyenne
        large_threshold = avg_size * config.BIG_ORDER_MULTIPLIER
        
        large_orders = trades_df[trades_df['amount'] >= large_threshold]
        
        large_orders_list = []
        for _, order in large_orders.iterrows():
            large_orders_list.append({
                'price': order['price'],
                'amount': order['amount'],
                'side': order['side'],
                'timestamp': order['timestamp'],
                'multiplier': order['amount'] / avg_size
            })
        
        return large_orders_list
    
    def get_market_depth_analysis(self, symbol=None):
        """
        Analyse complète de la profondeur de marché
        Combine order book + trades récents
        """
        order_book = self.get_order_book(symbol)
        trades = self.get_recent_trades(symbol)
        
        if not order_book or trades is None:
            return None
        
        # Analyse order book
        ob_analysis = self.analyze_order_book_imbalance(order_book)
        
        # Détecte gros ordres
        large_orders = self.detect_large_orders(trades)
        
        # Score de liquidité
        if ob_analysis:
            liquidity_score = min(
                (ob_analysis['bid_volume'] + ob_analysis['ask_volume']) / 100,
                100
            )
        else:
            liquidity_score = 0
        
        return {
            'order_book_analysis': ob_analysis,
            'large_orders': large_orders,
            'liquidity_score': liquidity_score,
            'num_large_orders': len(large_orders)
        }
    
    def print_order_flow_analysis(self, analysis):
        """Affiche l'analyse Order Flow"""
        if not analysis:
            return
        
        print("\n" + "="*60)
        print("📊 ANALYSE ORDER FLOW (PRO)")
        print("="*60)
        
        ob = analysis['order_book_analysis']
        if ob:
            print(f"\n💧 LIQUIDITÉ:")
            print(f"   Bids: {ob['bid_volume']:.2f} ({ob['bid_ratio']:.1f}%)")
            print(f"   Asks: {ob['ask_volume']:.2f} ({ob['ask_ratio']:.1f}%)")
            print(f"   Score liquidité: {analysis['liquidity_score']:.0f}/100")
            
            signal_emoji = "🟢" if ob['signal'] == 'bullish' else "🔴" if ob['signal'] == 'bearish' else "⚪"
            print(f"\n{signal_emoji} Déséquilibre: {ob['imbalance']*100:+.1f}%")
            print(f"   Signal: {ob['signal'].upper()}")
            print(f"   Force: {ob['strength']:.0f}%")
        
        if analysis['large_orders']:
            print(f"\n🐋 GROS ORDRES DÉTECTÉS: {len(analysis['large_orders'])}")
            for order in analysis['large_orders'][:3]:
                emoji = "🟢" if order['side'] == 'buy' else "🔴"
                print(f"   {emoji} {order['side'].upper()}: {order['amount']:.4f} à ${order['price']:.2f}")
                print(f"      ({order['multiplier']:.1f}x la moyenne)")
        
        print("="*60)


# Test du module
if __name__ == "__main__":
    print("🚀 Test du Data Collector APEX")
    
    collector = DataCollectorApex()
    
    if collector.exchange:
        print("\n✅ Collecteur opérationnel")
        print("📊 Capacités:")
        print("  - Données OHLCV historiques")
        print("  - Prix en temps réel")
        print("  - Order Book (DOM)")
        print("  - Trades récents")
        print("  - Détection gros ordres")
        print("  - Analyse déséquilibre")
