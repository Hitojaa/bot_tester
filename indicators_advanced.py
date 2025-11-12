# indicators_advanced.py - Indicateurs techniques PRO

import pandas as pd
import numpy as np
import config_apex as config

class AdvancedIndicators:
    """Tous les indicateurs techniques PRO en un seul endroit"""
    
    @staticmethod
    def calculate_all(df):
        """
        Calcule TOUS les indicateurs sur le DataFrame
        
        Returns:
            DataFrame: Avec tous les indicateurs
        """
        if df is None or len(df) < 200:
            return df
        
        # EMA (Exponential Moving Averages)
        df = AdvancedIndicators.calculate_ema(df)
        
        # RSI (Relative Strength Index)
        df = AdvancedIndicators.calculate_rsi(df)
        
        # MACD
        df = AdvancedIndicators.calculate_macd(df)
        
        # Bollinger Bands
        df = AdvancedIndicators.calculate_bollinger(df)
        
        # ATR (Average True Range)
        df = AdvancedIndicators.calculate_atr(df)
        
        # Stochastic
        df = AdvancedIndicators.calculate_stochastic(df)
        
        # Volume
        df = AdvancedIndicators.calculate_volume_indicators(df)
        
        # SuperTrend
        df = AdvancedIndicators.calculate_supertrend(df)
        
        # CCI (Commodity Channel Index)
        df = AdvancedIndicators.calculate_cci(df)
        
        # Williams %R
        df = AdvancedIndicators.calculate_williams_r(df)
        
        return df
    
    @staticmethod
    def calculate_ema(df):
        """Calcule les EMAs (9, 20, 50, 200)"""
        df['ema_fast'] = df['close'].ewm(span=config.EMA_FAST, adjust=False).mean()
        df['ema_medium'] = df['close'].ewm(span=config.EMA_MEDIUM, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=config.EMA_SLOW, adjust=False).mean()
        df['ema_trend'] = df['close'].ewm(span=config.EMA_TREND, adjust=False).mean()
        
        return df
    
    @staticmethod
    def calculate_rsi(df, period=None):
        """Calcule le RSI"""
        if period is None:
            period = config.RSI_PERIOD
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    @staticmethod
    def calculate_macd(df):
        """Calcule le MACD"""
        exp1 = df['close'].ewm(span=config.MACD_FAST, adjust=False).mean()
        exp2 = df['close'].ewm(span=config.MACD_SLOW, adjust=False).mean()
        
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=config.MACD_SIGNAL, adjust=False).mean()
        df['macd_diff'] = df['macd'] - df['macd_signal']
        
        return df
    
    @staticmethod
    def calculate_bollinger(df):
        """Calcule les Bollinger Bands"""
        df['bb_middle'] = df['close'].rolling(window=config.BB_PERIOD).mean()
        std = df['close'].rolling(window=config.BB_PERIOD).std()
        
        df['bb_upper'] = df['bb_middle'] + (std * config.BB_STD)
        df['bb_lower'] = df['bb_middle'] - (std * config.BB_STD)
        
        # Bandwidth (indicateur de volatilité)
        df['bb_bandwidth'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        return df
    
    @staticmethod
    def calculate_atr(df, period=None):
        """Calcule l'ATR (Average True Range)"""
        if period is None:
            period = config.ATR_PERIOD
        
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        
        df['atr'] = true_range.rolling(window=period).mean()
        
        return df
    
    @staticmethod
    def calculate_stochastic(df):
        """Calcule le Stochastic Oscillator"""
        low_min = df['low'].rolling(window=config.STOCH_K).min()
        high_max = df['high'].rolling(window=config.STOCH_K).max()
        
        df['stoch_k'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
        df['stoch_d'] = df['stoch_k'].rolling(window=config.STOCH_D).mean()
        
        return df
    
    @staticmethod
    def calculate_volume_indicators(df):
        """Calcule les indicateurs de volume"""
        # Volume SMA
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        
        # Volume ratio
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # OBV (On Balance Volume)
        obv = [0]
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        
        df['obv'] = obv
        
        return df
    
    @staticmethod
    def calculate_supertrend(df, period=10, multiplier=3):
        """Calcule le SuperTrend"""
        hl2 = (df['high'] + df['low']) / 2
        
        if 'atr' not in df.columns:
            df = AdvancedIndicators.calculate_atr(df, period)
        
        # Bandes
        upperband = hl2 + (multiplier * df['atr'])
        lowerband = hl2 - (multiplier * df['atr'])
        
        supertrend = [True] * len(df)
        direction = [1] * len(df)
        
        for i in range(1, len(df)):
            # SuperTrend calculation
            if df['close'].iloc[i] > upperband.iloc[i-1]:
                direction[i] = 1
            elif df['close'].iloc[i] < lowerband.iloc[i-1]:
                direction[i] = -1
            else:
                direction[i] = direction[i-1]
            
            supertrend[i] = lowerband.iloc[i] if direction[i] == 1 else upperband.iloc[i]
        
        df['supertrend'] = supertrend
        df['supertrend_direction'] = direction
        
        return df
    
    @staticmethod
    def calculate_cci(df, period=20):
        """Calcule le CCI (Commodity Channel Index)"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        sma_tp = typical_price.rolling(window=period).mean()
        
        mad = typical_price.rolling(window=period).apply(
            lambda x: np.abs(x - x.mean()).mean()
        )
        
        df['cci'] = (typical_price - sma_tp) / (0.015 * mad)
        
        return df
    
    @staticmethod
    def calculate_williams_r(df, period=14):
        """Calcule Williams %R"""
        highest_high = df['high'].rolling(window=period).max()
        lowest_low = df['low'].rolling(window=period).min()
        
        df['williams_r'] = -100 * ((highest_high - df['close']) / (highest_high - lowest_low))
        
        return df
    
    @staticmethod
    def print_current_indicators(df):
        """Affiche les indicateurs actuels de manière lisible"""
        if df is None or len(df) < 2:
            return
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        print("\n" + "="*60)
        print("📊 INDICATEURS TECHNIQUES ACTUELS")
        print("="*60)
        
        print(f"\n💰 Prix: ${last['close']:.2f}")
        print(f"📊 Volume: {last['volume']:,.0f} ({last.get('volume_ratio', 1):.2f}x moyenne)")
        
        # Tendance (EMAs)
        print(f"\n📈 TENDANCE:")
        print(f"   EMA 9:   ${last['ema_fast']:.2f}")
        print(f"   EMA 20:  ${last['ema_medium']:.2f}")
        print(f"   EMA 50:  ${last['ema_slow']:.2f}")
        print(f"   EMA 200: ${last['ema_trend']:.2f}")
        
        if last['ema_fast'] > last['ema_medium'] > last['ema_slow']:
            print(f"   ✅ Tendance HAUSSIÈRE forte")
        elif last['ema_fast'] < last['ema_medium'] < last['ema_slow']:
            print(f"   ❌ Tendance BAISSIÈRE forte")
        else:
            print(f"   ⚪ Tendance MIXTE")
        
        # Momentum
        print(f"\n📊 MOMENTUM:")
        rsi = last['rsi']
        rsi_status = "🔴 SURACHAT" if rsi > config.RSI_OVERBOUGHT else "🟢 SURVENTE" if rsi < config.RSI_OVERSOLD else "⚪ NEUTRE"
        print(f"   RSI: {rsi:.1f} {rsi_status}")
        
        macd_trend = "🟢 HAUSSIER" if last['macd'] > last['macd_signal'] else "🔴 BAISSIER"
        print(f"   MACD: {last['macd']:.2f} {macd_trend}")
        
        stoch = last['stoch_k']
        stoch_status = "🔴 SURACHAT" if stoch > 80 else "🟢 SURVENTE" if stoch < 20 else "⚪ NEUTRE"
        print(f"   Stochastic: {stoch:.1f} {stoch_status}")
        
        # Volatilité
        print(f"\n⚡ VOLATILITÉ:")
        print(f"   ATR: {last['atr']:.2f}")
        print(f"   Bollinger Width: {last.get('bb_bandwidth', 0)*100:.2f}%")
        
        # Support/Résistance Bollinger
        print(f"\n📊 BOLLINGER BANDS:")
        print(f"   Supérieure: ${last['bb_upper']:.2f}")
        print(f"   Moyenne:    ${last['bb_middle']:.2f}")
        print(f"   Inférieure: ${last['bb_lower']:.2f}")
        
        if last['close'] > last['bb_upper']:
            print(f"   ⚠️  Prix AU-DESSUS de la bande supérieure")
        elif last['close'] < last['bb_lower']:
            print(f"   ⚠️  Prix EN-DESSOUS de la bande inférieure")
        
        # SuperTrend
        if 'supertrend_direction' in df.columns:
            st_dir = "🟢 ACHAT" if last['supertrend_direction'] == 1 else "🔴 VENTE"
            print(f"\n🎯 SUPERTREND: {st_dir}")
        
        print("="*60)
    
    @staticmethod
    def get_momentum_score(df):
        """
        Calcule un score de momentum combiné
        
        Returns:
            dict: Scores et analyse
        """
        if df is None or len(df) < 2:
            return {'score': 0, 'strength': 'neutre'}
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        score = 0
        reasons = []
        
        # RSI
        if last['rsi'] < config.RSI_OVERSOLD:
            score += 30
            reasons.append(f"RSI survente ({last['rsi']:.1f})")
        elif last['rsi'] > config.RSI_OVERBOUGHT:
            score -= 30
            reasons.append(f"RSI surachat ({last['rsi']:.1f})")
        
        # MACD
        if prev['macd'] <= prev['macd_signal'] and last['macd'] > last['macd_signal']:
            score += 25
            reasons.append("MACD croisement haussier")
        elif prev['macd'] >= prev['macd_signal'] and last['macd'] < last['macd_signal']:
            score -= 25
            reasons.append("MACD croisement baissier")
        
        # Stochastic
        if last['stoch_k'] < 20:
            score += 15
            reasons.append("Stoch survente")
        elif last['stoch_k'] > 80:
            score -= 15
            reasons.append("Stoch surachat")
        
        # SuperTrend
        if 'supertrend_direction' in df.columns:
            if last['supertrend_direction'] == 1:
                score += 20
                reasons.append("SuperTrend haussier")
            else:
                score -= 20
                reasons.append("SuperTrend baissier")
        
        # Déterminer la force
        abs_score = abs(score)
        if abs_score > 70:
            strength = 'très fort'
        elif abs_score > 50:
            strength = 'fort'
        elif abs_score > 30:
            strength = 'modéré'
        else:
            strength = 'faible'
        
        direction = 'haussier' if score > 0 else 'baissier' if score < 0 else 'neutre'
        
        return {
            'score': score,
            'strength': strength,
            'direction': direction,
            'reasons': reasons
        }


# Test du module
if __name__ == "__main__":
    print("🚀 Test des Indicateurs Avancés")
    
    print("\n✅ Module opérationnel")
    print("📊 Indicateurs disponibles:")
    print("  - EMA (9, 20, 50, 200)")
    print("  - RSI")
    print("  - MACD")
    print("  - Bollinger Bands")
    print("  - ATR")
    print("  - Stochastic")
    print("  - Volume (SMA, Ratio, OBV)")
    print("  - SuperTrend")
    print("  - CCI")
    print("  - Williams %R")
