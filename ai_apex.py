# ai_apex.py - Intelligence Artificielle APEX (Multi-Layer Analysis)

import pandas as pd
import numpy as np
import os
import config_apex as config
from indicators_advanced import AdvancedIndicators
from pattern_scanner import PatternScanner
from volume_profile_engine import VolumeProfileEngine
from support_resistance_detector import SupportResistanceDetector
from ml_module import MLPredictor

class ApexAI:
    """
    Intelligence Artificielle APEX
    Analyse multi-layer : Macro → Méso → Micro → ML
    """

    def __init__(self):
        self.pattern_scanner = PatternScanner()
        self.volume_engine = VolumeProfileEngine()
        self.sr_detector = SupportResistanceDetector()

        # État du marché
        self.market_regime = 'neutral'
        self.trend_strength = 0
        self.volatility_level = 'normal'

        # Historique des prédictions
        self.predictions_history = []
        self.accuracy_rate = 0.5  # Commence à 50%

        # 🤖 ML PREDICTOR (4ème couche - V2.4)
        self.ml_predictor = None
        self.ml_enabled = False
        self._initialize_ml()

        if self.ml_enabled:
            print("✅ IA APEX initialisée (Multi-Layer + ML)")
        else:
            print("✅ IA APEX initialisée (Multi-Layer)")

    def _initialize_ml(self):
        """
        🤖 Initialise le système de Machine Learning
        Charge le modèle si disponible, sinon désactive ML
        """
        model_path = 'models/apex_ml_model.pkl'

        if not os.path.exists(model_path):
            print("⚠️  Aucun modèle ML trouvé (train avec train_ml_model.py)")
            self.ml_enabled = False
            return

        try:
            self.ml_predictor = MLPredictor()
            success = self.ml_predictor.load_model(model_path)

            if success:
                self.ml_enabled = True
                print(f"🤖 Modèle ML chargé: {model_path}")
            else:
                self.ml_enabled = False
                print("❌ Échec chargement modèle ML")

        except Exception as e:
            print(f"❌ Erreur init ML: {e}")
            self.ml_enabled = False
            self.ml_predictor = None

    def analyze_complete(self, df):
        """
        Analyse COMPLÈTE multi-layer

        Returns:
            dict: Analyse ultra-détaillée + APEX Score
        """
        if df is None or len(df) < 100:
            return None

        current_price = df.iloc[-1]['close']
        prev_price = df.iloc[-2]['close']

        # LAYER 1 : MACRO (Long terme - Contexte)
        macro_analysis = self._analyze_macro(df)

        # LAYER 2 : MÉSO (Moyen terme - Zones)
        meso_analysis = self._analyze_meso(df, current_price, prev_price)

        # LAYER 3 : MICRO (Court terme - Exécution)
        micro_analysis = self._analyze_micro(df, current_price, prev_price)

        # 🤖 LAYER 4 : MACHINE LEARNING (Prédiction probabiliste - V2.4)
        ml_analysis = self._analyze_ml(df)

        # 🆕 V2.1: DÉTECTION POWER SIGNALS (signaux ultra-forts)
        power_signals = self._detect_power_signals(df, current_price, prev_price,
                                                     macro_analysis, meso_analysis, micro_analysis)

        # Calcule le APEX SCORE final (avec ML + power signals)
        apex_score = self._calculate_apex_score(
            macro_analysis,
            meso_analysis,
            micro_analysis,
            ml_analysis,
            power_signals
        )

        # Décision finale
        decision = self._make_decision(apex_score)

        return {
            'apex_score': apex_score,
            'decision': decision,
            'macro': macro_analysis,
            'meso': meso_analysis,
            'micro': micro_analysis,
            'ml': ml_analysis,
            'power_signals': power_signals,
            'market_regime': self.market_regime,
            'confidence': apex_score['total_score']
        }
    
    def _analyze_macro(self, df):
        """
        LAYER 1 : Analyse MACRO (contexte long terme)
        Timeframes : 1h, 4h, tendance générale
        """
        # Détecte le régime de marché
        self._detect_market_regime(df)
        
        # Analyse la tendance long terme
        trend_analysis = self._analyze_trend(df)
        
        # Analyse la volatilité
        volatility_analysis = self._analyze_volatility(df)
        
        macro_score = 0
        reasons = []
        
        # Score selon le régime
        if self.market_regime == 'trending_up':
            macro_score += 30
            reasons.append("Tendance haussière confirmée")
        elif self.market_regime == 'trending_down':
            macro_score -= 20
            reasons.append("Tendance baissière confirmée")
        elif self.market_regime == 'ranging':
            macro_score += 10
            reasons.append("Marché en range")
        elif self.market_regime == 'volatile':
            macro_score -= 15
            reasons.append("Marché très volatile")
        
        # Score selon la force de tendance
        macro_score += trend_analysis['strength'] * 0.3
        
        return {
            'score': min(max(macro_score, -30), 30),  # Limité à ±30
            'regime': self.market_regime,
            'trend': trend_analysis,
            'volatility': volatility_analysis,
            'reasons': reasons
        }
    
    def _analyze_meso(self, df, current_price, prev_price):
        """
        LAYER 2 : Analyse MÉSO (zones clés)
        Support/Résistance, Volume Profile, VWAP
        """
        # Volume Profile + VWAP
        vp_analysis = self.volume_engine.analyze_complete(df, current_price, prev_price)
        
        # Support/Résistance
        self.sr_detector.detect_levels(df)
        sr_signal = self.sr_detector.get_trading_signal(current_price, prev_price)
        
        meso_score = 0
        reasons = []
        
        # Score Volume Profile
        if vp_analysis:
            meso_score += vp_analysis['score'] * 0.5
            if vp_analysis['vwap_signal']['reason']:
                reasons.append(vp_analysis['vwap_signal']['reason'])
        
        # Score S/R
        if sr_signal:
            meso_score += sr_signal['score'] * 0.5
            if sr_signal['reason']:
                reasons.append(sr_signal['reason'])
        
        # Vérifie chemin dégagé
        target_price = current_price * 1.025  # +2.5%
        path_clear, path_msg = self.sr_detector.has_clear_path(current_price, target_price)
        
        if path_clear:
            meso_score += 15
            reasons.append("Chemin dégagé vers target")
        else:
            meso_score -= 10
            reasons.append(path_msg)
        
        return {
            'score': min(max(meso_score, -40), 40),  # Limité à ±40
            'vp_analysis': vp_analysis,
            'sr_signal': sr_signal,
            'path_clear': path_clear,
            'reasons': reasons
        }
    
    def _analyze_micro(self, df, current_price, prev_price):
        """
        LAYER 3 : Analyse MICRO (exécution)
        Price action, patterns, momentum instantané
        """
        # Scanne les patterns
        patterns = self.pattern_scanner.scan_all_patterns(df)
        pattern_scores = self.pattern_scanner.get_combined_score()
        
        # Analyse momentum
        momentum = AdvancedIndicators.get_momentum_score(df)
        
        # Analyse volume
        last_candle = df.iloc[-1]
        volume_spike = last_candle['volume'] / last_candle.get('volume_sma', last_candle['volume'])
        
        micro_score = 0
        reasons = []
        
        # Score patterns
        if pattern_scores['buy_score'] > pattern_scores['sell_score']:
            micro_score += pattern_scores['buy_score'] * 0.3
            reasons.append(f"{len([p for p in patterns if p['type']=='bullish'])} patterns haussiers")
        else:
            micro_score -= pattern_scores['sell_score'] * 0.3
            reasons.append(f"{len([p for p in patterns if p['type']=='bearish'])} patterns baissiers")
        
        # Score momentum
        micro_score += momentum['score'] * 0.3
        if momentum['reasons']:
            reasons.extend(momentum['reasons'][:2])  # Top 2
        
        # Score volume
        if volume_spike > config.VOLUME_SPIKE_THRESHOLD:
            micro_score += 20
            reasons.append(f"Volume spike ({volume_spike:.1f}x)")
        
        return {
            'score': min(max(micro_score, -30), 30),  # Limité à ±30
            'patterns': patterns,
            'pattern_scores': pattern_scores,
            'momentum': momentum,
            'volume_spike': volume_spike,
            'reasons': reasons
        }

    def _analyze_ml(self, df):
        """
        🤖 LAYER 4 : Analyse MACHINE LEARNING (V2.4)
        Prédiction probabiliste basée sur 50k+ exemples historiques

        Returns:
            dict: Prédiction ML + probabilité + confidence + poids dynamique
        """
        if not self.ml_enabled or self.ml_predictor is None:
            # ML désactivé ou pas de modèle
            return {
                'enabled': False,
                'score': 0,
                'prediction': None,
                'probability': 0.5,
                'confidence': 0,
                'weight': 0,
                'accuracy': 0,
                'reasons': ['ML désactivé (pas de modèle entraîné)']
            }

        try:
            # Obtient S/R pour contexte
            support_resistance = {
                'support_levels': self.sr_detector.support_levels,
                'resistance_levels': self.sr_detector.resistance_levels
            }

            # Prédiction ML
            ml_result = self.ml_predictor.predict(df, support_resistance)

            if ml_result is None:
                return {
                    'enabled': True,
                    'score': 0,
                    'prediction': None,
                    'probability': 0.5,
                    'confidence': 0,
                    'weight': 0,
                    'accuracy': self.ml_predictor.accuracy_rate * 100,
                    'reasons': ['Échec extraction features']
                }

            # Interprétation
            prediction = ml_result['prediction']
            probability = ml_result['probability']  # 0-1
            confidence = ml_result['confidence']    # 0-1 (ajusté par accuracy)
            ml_score = ml_result['ml_score']        # -100 à +100
            weight = ml_result['weight']            # 0.15 à 0.30

            reasons = []
            if prediction == 1:
                reasons.append(f"ML prédit WIN ({probability*100:.1f}% confiance)")
            else:
                reasons.append(f"ML prédit LOSS ({(1-probability)*100:.1f}% confiance)")

            # Ajoute info sur accuracy
            accuracy_pct = self.ml_predictor.accuracy_rate * 100
            if accuracy_pct >= 65:
                reasons.append(f"Accuracy élevée ({accuracy_pct:.1f}%) → Poids {weight*100:.0f}%")
            elif accuracy_pct < 50:
                reasons.append(f"Accuracy faible ({accuracy_pct:.1f}%) → Poids {weight*100:.0f}%")

            return {
                'enabled': True,
                'score': ml_score,              # -100 à +100
                'prediction': prediction,        # 0 ou 1
                'probability': probability,      # 0-1
                'confidence': confidence,        # 0-1
                'weight': weight,                # 0.15-0.30
                'accuracy': accuracy_pct,        # 0-100
                'reasons': reasons
            }

        except Exception as e:
            print(f"❌ Erreur ML prediction: {e}")
            return {
                'enabled': False,
                'score': 0,
                'prediction': None,
                'probability': 0.5,
                'confidence': 0,
                'weight': 0,
                'accuracy': 0,
                'reasons': [f'Erreur ML: {str(e)[:50]}']
            }

    def _detect_power_signals(self, df, current_price, prev_price, macro, meso, micro):
        """
        🔥 POWER SIGNALS - Détecte les signaux ULTRA-FORTS qui justifient un trade immédiat

        Ces signaux "overrident" partiellement les autres layers quand ils sont présents.
        En scalping 1m, un RSI à 20 + Order Flow à 95% = ACHAT, peu importe la tendance 4h !

        Returns:
            dict: Signaux détectés + boost à appliquer
        """
        signals_detected = []
        total_boost = 0

        last_candle = df.iloc[-1]

        # 1. RSI EXTRÊME (survente/surachat sévère)
        if 'rsi' in last_candle:
            rsi = last_candle['rsi']
            if rsi < 25:  # Survente EXTRÊME
                signals_detected.append(f"RSI Extrême Survente ({rsi:.1f})")
                total_boost += 25  # +25 points !
            elif rsi > 75:  # Surachat EXTRÊME
                signals_detected.append(f"RSI Extrême Surachat ({rsi:.1f})")
                total_boost -= 15  # Pénalité pour surachat

        # 2. VOLUME SPIKE MASSIF (> 2x la moyenne)
        volume_spike = micro.get('volume_spike', 1.0)
        if volume_spike > 2.0:
            signals_detected.append(f"Volume Spike Massif ({volume_spike:.1f}x)")
            total_boost += 15

        # 3. PATTERNS FORTS (3 soldiers, engulfing, hammer, etc.)
        patterns = micro.get('patterns', [])
        strong_bullish_patterns = [p for p in patterns
                                    if p['type'] == 'bullish' and p['reliability'] >= 70]
        if len(strong_bullish_patterns) >= 2:
            signals_detected.append(f"{len(strong_bullish_patterns)} Patterns Haussiers Forts")
            total_boost += 20

        # 4. MOMENTUM CONVERGENCE (RSI + MACD + Stoch alignés)
        momentum_signals = 0
        if 'rsi' in last_candle and last_candle['rsi'] < 35:
            momentum_signals += 1
        if 'macd' in last_candle and 'macd_signal' in last_candle:
            if last_candle['macd'] > last_candle['macd_signal']:
                momentum_signals += 1
        if 'stoch_k' in last_candle and last_candle['stoch_k'] < 30:
            momentum_signals += 1

        if momentum_signals >= 2:
            signals_detected.append(f"Convergence Momentum ({momentum_signals}/3 signaux)")
            total_boost += 18

        # 5. SUPERTREND + PRICE ACTION
        if 'supertrend' in last_candle and last_candle['supertrend'] > 0:  # Signal achat
            if current_price > prev_price:  # Prix en hausse
                signals_detected.append("SuperTrend BUY + Prix Hausse")
                total_boost += 12

        # 6. BOLLINGER BANDS EXTREMES
        if 'bb_lower' in last_candle and 'bb_upper' in last_candle:
            bb_position = (current_price - last_candle['bb_lower']) / (last_candle['bb_upper'] - last_candle['bb_lower'])
            if bb_position < 0.1:  # Prix très proche de la bande basse
                signals_detected.append("Prix à la Bollinger Basse (rebond potentiel)")
                total_boost += 15

        # Plafonne le boost total
        total_boost = min(total_boost, 50)  # Max +50 points

        return {
            'signals': signals_detected,
            'count': len(signals_detected),
            'total_boost': total_boost,
            'active': len(signals_detected) >= 2  # Activé si 2+ signaux
        }

    def evaluate_exit_conditions(self, df, current_price, position_info, entry_apex_score):
        """
        🚨 ÉVALUE LES CONDITIONS DE SORTIE DYNAMIQUE (V2.3 - Scalping intelligent!)

        Détecte si les conditions favorables se détériorent et suggère une sortie
        anticipée avant d'atteindre le stop-loss ou le target.

        🧠 V2.3: Mode scalping intelligent
        - Laisse respirer le trade 2-3 bougies minimum
        - Ne sort pas sur un seul signal (EMA9/MACD seuls)
        - Respecte les setups valides (rebond, bougie verte)
        - Exige convergence de plusieurs signaux négatifs

        Args:
            df: DataFrame avec indicateurs
            current_price: Prix actuel
            position_info: Info sur la position ouverte
            entry_apex_score: Score APEX à l'entrée du trade

        Returns:
            dict: {
                'should_exit': bool,
                'exit_type': 'full' | 'partial' | None,
                'exit_percent': float (0-1),
                'reasons': list[str],
                'urgency': 'critical' | 'high' | 'medium' | 'low'
            }
        """
        if not config.DYNAMIC_EXITS_ENABLED:
            return {'should_exit': False, 'exit_type': None, 'exit_percent': 0, 'reasons': [], 'urgency': 'low'}

        reasons = []
        urgency_score = 0  # Plus le score est élevé, plus c'est urgent
        exit_percent = 0

        last_candle = df.iloc[-1]
        entry_price = position_info['entry_price']
        pnl_percent = ((current_price - entry_price) / entry_price)

        # 🧠 PROTECTION 1: Laisse respirer le trade (minimum 2-3 bougies)
        from datetime import datetime
        entry_time = position_info.get('entry_time')
        if entry_time:
            time_in_position = (datetime.now() - entry_time).total_seconds()
            candles_in_position = time_in_position / 60  # 1 min par bougie

            if candles_in_position < config.MIN_CANDLES_IN_POSITION:
                # Trop tôt pour évaluer, sauf si APEX s'effondre (< 40)
                current_analysis = self.analyze_complete(df)
                if current_analysis:
                    current_apex = current_analysis['apex_score']['total_score']
                    if current_apex >= 40:  # Setup encore valide
                        return {'should_exit': False, 'exit_type': None, 'exit_percent': 0,
                               'reasons': [f"🧠 Trade respire ({candles_in_position:.0f}/{config.MIN_CANDLES_IN_POSITION} bougies)"],
                               'urgency': 'low'}

        # Ne pas sortir trop tôt si on n'a pas encore un minimum de profit
        has_min_profit = pnl_percent >= config.MIN_PROFIT_FOR_EARLY_EXIT

        # 🧠 PROTECTION 2: Détecte si setup initial encore valide (rebond en cours)
        setup_still_valid = False
        if config.SMART_EXIT_MODE:
            # Bougie verte récente = rebond en cours
            if last_candle['close'] > last_candle['open']:
                setup_still_valid = True
            # RSI encore en survente = setup retournement valide
            if 'rsi' in last_candle and last_candle['rsi'] < 30:
                setup_still_valid = True

        # Compte les bougies consécutives avec stoch > 90
        stoch_overbought_count = 0
        if 'stoch_k' in df.columns:
            for i in range(min(config.EXIT_STOCH_DURATION, len(df))):
                if df.iloc[-(i+1)]['stoch_k'] > config.EXIT_STOCH_OVERBOUGHT:
                    stoch_overbought_count += 1
                else:
                    break

        # ═══════════════════════════════════════════════════════════
        # 1. DÉTÉRIORATION DES CONDITIONS
        # ═══════════════════════════════════════════════════════════
        if config.EXIT_ON_DETERIORATION:
            deterioration_signals = 0

            # Stochastique en surachat prolongé
            if stoch_overbought_count >= config.EXIT_STOCH_DURATION:
                reasons.append(f"⚠️ Stochastique en surachat prolongé ({stoch_overbought_count} bougies >90)")
                deterioration_signals += 1
                urgency_score += 20

            # Order Flow négatif (si disponible dans l'analyse micro)
            # On devra passer l'analysis actuelle pour avoir ces infos

            # APEX critique ou stagnant
            current_analysis = self.analyze_complete(df)
            if current_analysis:
                current_apex = current_analysis['apex_score']['total_score']

                if current_apex < config.EXIT_APEX_CRITICAL:
                    reasons.append(f"🚨 APEX CRITIQUE ({current_apex:.0f} < {config.EXIT_APEX_CRITICAL})")
                    deterioration_signals += 1
                    urgency_score += 30

                elif current_apex < config.EXIT_APEX_STAGNANT and has_min_profit:
                    reasons.append(f"⚠️ APEX stagnant ({current_apex:.0f} < {config.EXIT_APEX_STAGNANT})")
                    deterioration_signals += 1
                    urgency_score += 15

            # Si 2+ signaux de détérioration → Sortie partielle ou totale
            if deterioration_signals >= 2:
                if has_min_profit:
                    exit_percent = 0.5 if deterioration_signals >= 3 else 0.3  # 50% ou 30%
                else:
                    exit_percent = 1.0  # Sortie totale si pas encore profitable

        # ═══════════════════════════════════════════════════════════
        # 2. PERTE DE MOMENTUM (🧠 Mode intelligent V2.3)
        # ═══════════════════════════════════════════════════════════
        if config.EXIT_ON_MOMENTUM_LOSS:
            momentum_signals = []

            # Prix repasse sous EMA9
            if config.EXIT_PRICE_UNDER_EMA and 'ema_fast' in last_candle:
                if current_price < last_candle['ema_fast']:
                    # 🧠 MAIS: Ne sort pas si setup encore valide (bougie verte/rebond)
                    if not setup_still_valid:
                        momentum_signals.append("Prix sous EMA9")
                        urgency_score += 15  # Réduit de 25 → 15

            # MACD devient négatif ou neutre
            if config.EXIT_MACD_BEARISH and 'macd' in last_candle and 'macd_signal' in last_candle:
                if last_candle['macd'] < last_candle['macd_signal']:
                    # 🧠 MAIS: Ne sort pas si setup encore valide
                    if not setup_still_valid:
                        momentum_signals.append("MACD baissier")
                        urgency_score += 12  # Réduit de 20 → 12

            # 🧠 EXIGE CONVERGENCE: Besoin de 2+ signaux momentum ou 1 signal + autre détérioration
            if config.REQUIRE_CONVERGENCE:
                # Sortie seulement si 2+ signaux négatifs convergent
                if len(momentum_signals) >= 2 or (len(momentum_signals) >= 1 and len(reasons) > 0):
                    for sig in momentum_signals:
                        reasons.append(f"📉 {sig} (perte momentum)")
                    if has_min_profit:
                        exit_percent = max(exit_percent, 0.5)  # Réduit de 70% → 50%
                    else:
                        exit_percent = max(exit_percent, 0.7)  # Réduit de 100% → 70%
            else:
                # Mode ancien (sans convergence): Sortie immédiate
                if len(momentum_signals) > 0:
                    for sig in momentum_signals:
                        reasons.append(f"📉 {sig}")
                    if has_min_profit:
                        exit_percent = max(exit_percent, 0.7)
                    else:
                        exit_percent = 1.0

        # ═══════════════════════════════════════════════════════════
        # 3. DÉGRADATION DU SCORE APEX
        # ═══════════════════════════════════════════════════════════
        if config.EXIT_ON_APEX_DROP and current_analysis:
            current_apex = current_analysis['apex_score']['total_score']
            apex_drop = current_apex - entry_apex_score

            if apex_drop <= config.EXIT_APEX_DROP_THRESHOLD:
                reasons.append(f"📊 APEX en chute ({apex_drop:+.0f} points vs entrée)")
                urgency_score += 35
                exit_percent = max(exit_percent, 0.8 if has_min_profit else 1.0)

            # Changement de régime de marché
            if config.EXIT_REGIME_CHANGE:
                if current_analysis['market_regime'] in ['ranging', 'neutral', 'trending_down']:
                    if self.market_regime == 'trending_up':  # On était en tendance haussière
                        reasons.append(f"🔄 Régime changé: {self.market_regime} → {current_analysis['market_regime']}")
                        urgency_score += 25
                        exit_percent = max(exit_percent, 0.5)

        # ═══════════════════════════════════════════════════════════
        # 4. TAKE-PROFIT PROGRESSIF (conditions neutres)
        # ═══════════════════════════════════════════════════════════
        if config.PROGRESSIVE_EXITS_ENABLED and pnl_percent > 0:
            # +1.0% → Sortie partielle si conditions neutres
            if pnl_percent >= config.PARTIAL_EXIT_2_PROFIT:
                if current_analysis and current_analysis['apex_score']['total_score'] < 70:
                    reasons.append(f"💰 TP progressif: +{pnl_percent*100:.1f}% avec conditions neutres")
                    exit_percent = max(exit_percent, 0.3)
                    urgency_score += 10

            # +0.5% → Sortie partielle si conditions se dégradent
            elif pnl_percent >= config.PARTIAL_EXIT_1_PROFIT:
                if len(reasons) > 0:  # Si d'autres signaux de dégradation
                    reasons.append(f"💰 TP progressif: +{pnl_percent*100:.1f}% avec dégradation")
                    exit_percent = max(exit_percent, 0.3)
                    urgency_score += 5

        # Détermine l'urgence
        if urgency_score >= 60:
            urgency = 'critical'
        elif urgency_score >= 40:
            urgency = 'high'
        elif urgency_score >= 20:
            urgency = 'medium'
        else:
            urgency = 'low'

        # Détermine le type de sortie
        should_exit = len(reasons) > 0 and exit_percent > 0
        exit_type = None
        if should_exit:
            if exit_percent >= 0.9:
                exit_type = 'full'
            elif exit_percent > 0:
                exit_type = 'partial'

        return {
            'should_exit': should_exit,
            'exit_type': exit_type,
            'exit_percent': exit_percent,
            'reasons': reasons,
            'urgency': urgency,
            'urgency_score': urgency_score
        }

    def _calculate_apex_score(self, macro, meso, micro, ml_analysis, power_signals=None):
        """
        Calcule le APEX SCORE final (0-100)
        Combine les 4 layers avec pondération

        🤖 NOUVELLE PONDÉRATION V2.4 (avec ML) :
        - Micro (patterns, timing) : 40%
        - Méso (zones clés) : 30%
        - ML (prédiction) : 15-30% (dynamique selon accuracy!)
        - Macro (contexte) : 15%
        + POWER SIGNALS : +50 points max si 2+ signaux forts détectés

        🧠 Le poids ML s'ajuste automatiquement:
        - Accuracy >65% → ML weight = 25-30%
        - Accuracy 50-65% → ML weight = 15%
        - Accuracy <50% → ML weight = 5-10%
        """
        # Pondération des layers (V2.4 - avec ML)
        ml_enabled = ml_analysis.get('enabled', False)
        ml_weight = ml_analysis.get('weight', 0) if ml_enabled else 0

        # Ajuste les autres poids pour garder total = 100%
        if ml_enabled:
            # ML actif: redistribue les poids
            remaining_weight = 1.0 - ml_weight
            macro_weight = 0.15 * remaining_weight
            meso_weight = 0.30 * remaining_weight
            micro_weight = 0.40 * remaining_weight
        else:
            # ML inactif: pondération classique V2.1
            macro_weight = 0.15
            meso_weight = 0.35
            micro_weight = 0.50

        # Scores pondérés
        weighted_macro = macro['score'] * macro_weight
        weighted_meso = meso['score'] * meso_weight
        weighted_micro = micro['score'] * micro_weight
        weighted_ml = ml_analysis.get('score', 0) * ml_weight

        # Score brut (-100 à +100)
        raw_score = weighted_macro + weighted_meso + weighted_micro + weighted_ml
        
        # Convertit en 0-100
        # -100 = 0 (très baissier)
        # 0 = 50 (neutre)
        # +100 = 100 (très haussier)
        apex_score = (raw_score + 100) / 2

        # 🆕 BOOST VOLUME : Si volume confirme le signal (+10 points max)
        volume_boost = 0
        if micro.get('volume_spike', 1.0) > 1.5:  # Volume > 150% de la moyenne
            volume_boost = min((micro['volume_spike'] - 1.0) * 10, 10)
            apex_score += volume_boost
            apex_score = min(apex_score, 100)  # Plafonné à 100

        # 🆕 AJUSTEMENT VOLATILITÉ : Score bonus/malus selon régime
        volatility_adjustment = macro.get('volatility', {}).get('adjustment', 0)
        apex_score += volatility_adjustment
        apex_score = min(max(apex_score, 0), 100)  # Borné entre 0 et 100

        # 🔥 POWER SIGNALS BOOST : Si 2+ signaux ultra-forts détectés
        power_boost = 0
        if power_signals and power_signals.get('active', False):
            power_boost = power_signals.get('total_boost', 0)
            apex_score += power_boost
            apex_score = min(apex_score, 100)  # Plafonné à 100

        # Ajustement selon la précision historique
        confidence_factor = 0.5 + (self.accuracy_rate * 0.5)
        apex_score *= confidence_factor

        return {
            'total_score': min(max(apex_score, 0), 100),
            'raw_score': raw_score,
            'macro_contribution': weighted_macro,
            'meso_contribution': weighted_meso,
            'micro_contribution': weighted_micro,
            'ml_contribution': weighted_ml,
            'ml_enabled': ml_enabled,
            'ml_weight': ml_weight,
            'volume_boost': volume_boost,
            'volatility_adjustment': volatility_adjustment,
            'power_boost': power_boost,
            'power_signals_count': power_signals.get('count', 0) if power_signals else 0,
            'confidence_factor': confidence_factor
        }
    
    def _make_decision(self, apex_score):
        """
        Prend la décision finale d'achat/vente/hold
        """
        score = apex_score['total_score']
        
        if score >= config.MIN_APEX_SCORE:
            return {
                'action': 'buy',
                'strength': self._get_signal_strength(score),
                'recommendation': 'ACHAT FORT' if score >= config.IDEAL_APEX_SCORE else 'ACHAT'
            }
        elif score <= (100 - config.MIN_APEX_SCORE):
            return {
                'action': 'sell',
                'strength': self._get_signal_strength(100 - score),
                'recommendation': 'VENTE FORTE' if score <= 15 else 'VENTE'
            }
        else:
            return {
                'action': 'hold',
                'strength': 'neutre',
                'recommendation': 'ATTENDRE'
            }
    
    def _get_signal_strength(self, score):
        """Détermine la force du signal"""
        if score >= 95:
            return 'extrême'
        elif score >= 90:
            return 'très fort'
        elif score >= 85:
            return 'fort'
        elif score >= 75:
            return 'modéré'
        else:
            return 'faible'
    
    def _detect_market_regime(self, df):
        """Détecte le régime de marché actuel"""
        if len(df) < 50:
            self.market_regime = 'neutral'
            return
        
        recent = df.tail(50)
        
        # Calcule le changement de prix
        price_change = (recent['close'].iloc[-1] - recent['close'].iloc[0]) / recent['close'].iloc[0]
        
        # Calcule la volatilité (ATR relatif)
        atr = recent['atr'].iloc[-1]
        avg_price = recent['close'].mean()
        volatility_ratio = atr / avg_price
        
        # Détecte le régime
        if volatility_ratio > 0.03:  # 3% ATR = très volatile
            self.market_regime = 'volatile'
            self.volatility_level = 'high'
        elif abs(price_change) > config.TRENDING_THRESHOLD:
            if price_change > 0:
                self.market_regime = 'trending_up'
            else:
                self.market_regime = 'trending_down'
            self.volatility_level = 'normal'
        elif abs(price_change) < config.RANGING_THRESHOLD:
            self.market_regime = 'ranging'
            self.volatility_level = 'low'
        else:
            self.market_regime = 'neutral'
            self.volatility_level = 'normal'
    
    def _analyze_trend(self, df):
        """Analyse la force de la tendance"""
        if 'ema_fast' not in df.columns:
            return {'strength': 0, 'direction': 'neutral'}
        
        last = df.iloc[-1]
        
        # Compare les EMAs
        ema_order_score = 0
        
        if last['ema_fast'] > last['ema_medium']:
            ema_order_score += 1
        if last['ema_medium'] > last['ema_slow']:
            ema_order_score += 1
        if last['ema_slow'] > last['ema_trend']:
            ema_order_score += 1
        
        # Score de tendance (-100 à +100)
        if ema_order_score == 3:
            trend_strength = 100  # Tendance haussière forte
            direction = 'bullish'
        elif ema_order_score == 0:
            trend_strength = -100  # Tendance baissière forte
            direction = 'bearish'
        else:
            trend_strength = (ema_order_score - 1.5) * 50
            direction = 'neutral'
        
        return {
            'strength': trend_strength,
            'direction': direction
        }
    
    def _analyze_volatility(self, df):
        """
        Analyse la volatilité avec adaptativité

        🆕 V2.0: Ajuste les attentes selon la volatilité
        - Haute volatilité: Être plus tolérant (signaux moins stricts)
        - Basse volatilité: Être plus exigeant (faux signaux fréquents)
        """
        if 'atr' not in df.columns:
            return {'level': 'unknown', 'score': 0, 'ratio': 1.0, 'adjustment': 0}

        recent_atr = df['atr'].tail(20)
        current_atr = recent_atr.iloc[-1]
        avg_atr = recent_atr.mean()

        volatility_ratio = current_atr / avg_atr

        # 🆕 Ajustement adaptatif du score selon volatilité
        if volatility_ratio > 1.5:
            # Très haute volatilité: +5 points (opportunités rapides)
            level = 'very_high'
            score = 5  # Bonus (mouvement rapide = opportunité)
            adjustment = +5
        elif volatility_ratio > 1.2:
            # Haute volatilité: +3 points
            level = 'high'
            score = 3
            adjustment = +3
        elif volatility_ratio < 0.7:
            # Très basse volatilité: -10 points (marché mort)
            level = 'very_low'
            score = -10  # Pénalité (faux signaux)
            adjustment = -10
        elif volatility_ratio < 0.9:
            # Basse volatilité: -5 points
            level = 'low'
            score = -5
            adjustment = -5
        else:
            # Volatilité normale: neutre
            level = 'normal'
            score = 0
            adjustment = 0

        return {
            'level': level,
            'ratio': volatility_ratio,
            'score': score,
            'adjustment': adjustment  # Utilisé pour ajuster MIN_APEX_SCORE dynamiquement
        }
    
    def update_accuracy(self, prediction_correct):
        """Met à jour le taux de précision de l'IA"""
        self.predictions_history.append(1 if prediction_correct else 0)
        
        # Garde les 50 dernières prédictions
        if len(self.predictions_history) > 50:
            self.predictions_history.pop(0)
        
        if self.predictions_history:
            self.accuracy_rate = sum(self.predictions_history) / len(self.predictions_history)
    
    def print_analysis(self, analysis):
        """Affiche l'analyse de manière ultra-détaillée"""
        if not analysis:
            return
        
        print("\n" + "="*70)
        print("🧠 ANALYSE INTELLIGENCE ARTIFICIELLE APEX".center(70))
        print("="*70)
        
        # APEX SCORE
        apex = analysis['apex_score']
        score = apex['total_score']
        
        # Barre de progression visuelle
        bar_length = 50
        filled = int((score / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        color_emoji = "🔴" if score < 30 else "🟡" if score < 60 else "🟢" if score < 85 else "🔥"
        
        print(f"\n{color_emoji} APEX SCORE: {score:.1f}/100")
        print(f"[{bar}]")
        print(f"\n📊 Contributions:")
        print(f"   Macro (contexte):  {apex['macro_contribution']:+.1f}")
        print(f"   Méso (zones):      {apex['meso_contribution']:+.1f}")
        print(f"   Micro (exécution): {apex['micro_contribution']:+.1f}")

        # 🤖 Affichage ML si activé
        if apex.get('ml_enabled', False):
            ml_contrib = apex.get('ml_contribution', 0)
            ml_weight_pct = apex.get('ml_weight', 0) * 100
            print(f"   🤖 ML (prédiction): {ml_contrib:+.1f} ({ml_weight_pct:.0f}% poids)")

        # 🔥 POWER SIGNALS (si actifs)
        power_signals = analysis.get('power_signals', {})
        if power_signals.get('active', False):
            print(f"\n🔥 POWER SIGNALS ACTIFS ({power_signals.get('count', 0)} détectés):")
            for signal in power_signals.get('signals', []):
                print(f"   ⚡ {signal}")
            print(f"   💥 Boost total: +{apex.get('power_boost', 0):.0f} points")

        # DÉCISION
        decision = analysis['decision']
        action_emoji = "🟢" if decision['action'] == 'buy' else "🔴" if decision['action'] == 'sell' else "⚪"
        
        print(f"\n{action_emoji} DÉCISION: {decision['recommendation']}")
        print(f"   Action: {decision['action'].upper()}")
        print(f"   Force: {decision['strength'].upper()}")
        
        # RÉGIME DE MARCHÉ
        regime_emoji = {
            'trending_up': '📈',
            'trending_down': '📉',
            'ranging': '↔️',
            'volatile': '⚡',
            'neutral': '⚪'
        }.get(analysis['market_regime'], '⚪')
        
        print(f"\n{regime_emoji} Régime: {analysis['market_regime'].upper().replace('_', ' ')}")

        # 🤖 MACHINE LEARNING (si activé)
        ml_info = analysis.get('ml', {})
        if ml_info.get('enabled', False):
            print(f"\n🤖 MACHINE LEARNING:")
            prediction = ml_info.get('prediction')
            probability = ml_info.get('probability', 0.5) * 100
            accuracy = ml_info.get('accuracy', 0)
            ml_score = ml_info.get('score', 0)

            pred_emoji = "🟢" if prediction == 1 else "🔴"
            pred_text = "WIN" if prediction == 1 else "LOSS"

            print(f"   {pred_emoji} Prédiction: {pred_text} ({probability:.1f}% confiance)")
            print(f"   📊 ML Score: {ml_score:+.1f}")
            print(f"   🎯 Accuracy historique: {accuracy:.1f}%")

            # Affiche les raisons ML
            for reason in ml_info.get('reasons', []):
                print(f"   • {reason}")

        # TOP RAISONS
        print(f"\n💡 TOP RAISONS:")
        
        all_reasons = []
        all_reasons.extend(analysis['macro']['reasons'])
        all_reasons.extend(analysis['meso']['reasons'][:2])
        all_reasons.extend(analysis['micro']['reasons'][:2])
        
        for i, reason in enumerate(all_reasons[:5], 1):
            print(f"   {i}. {reason}")
        
        # PATTERNS
        patterns = analysis['micro']['patterns']
        if patterns:
            print(f"\n🔍 Patterns détectés: {len(patterns)}")
            for p in patterns[:3]:
                emoji = "🟢" if p['type'] == 'bullish' else "🔴" if p['type'] == 'bearish' else "⚪"
                print(f"   {emoji} {p['name']} ({p['reliability']}%)")
        
        print("="*70)


# Test du module
if __name__ == "__main__":
    print("🚀 Test de l'IA APEX")
    
    ai = ApexAI()
    
    print("\n✅ IA APEX opérationnelle")
    print("🧠 Architecture Multi-Layer:")
    print("  Layer 1 : MACRO (contexte long terme)")
    print("  Layer 2 : MÉSO (zones clés)")
    print("  Layer 3 : MICRO (exécution)")
    print("  → APEX SCORE final (0-100)")
