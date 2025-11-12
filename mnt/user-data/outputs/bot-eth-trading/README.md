# 🤖 Bot de Trading ETH/USDT

Bot de trading automatique pour Ethereum utilisant des indicateurs techniques (RSI, MACD, EMA, Bollinger Bands).

## ⚠️ AVERTISSEMENT

**Le trading de crypto-monnaies comporte des risques importants de perte en capital.**
- Ce bot est fourni à titre éducatif
- Ne tradez qu'avec de l'argent que vous pouvez vous permettre de perdre
- Testez TOUJOURS en mode simulation avant d'utiliser de l'argent réel
- Les performances passées ne garantissent pas les résultats futurs

## 📋 Prérequis

- Python 3.8 ou supérieur
- Un compte Binance vérifié
- Capital de départ (recommandé: minimum 100€)

## 🚀 Installation

### 1. Installer les dépendances

```bash
pip install ccxt pandas ta python-telegram-bot requests
```

### 2. Configurer les clés API Binance

1. Connecte-toi sur Binance
2. Va dans **Profil → API Management**
3. Crée une nouvelle clé API avec **uniquement** ces permissions:
   - ✅ Enable Reading
   - ✅ Enable Spot & Margin Trading
   - ❌ **JAMAIS** Enable Withdrawals
4. Copie ta **API Key** et ton **Secret Key**

### 3. Configurer le bot

Ouvre `config.py` et modifie:

```python
BINANCE_API_KEY = "ta_vraie_clé_api"
BINANCE_SECRET_KEY = "ton_vrai_secret"
INITIAL_CAPITAL = 100  # Ton capital de départ en USDT
```

## 🧪 Étape 1: Test de connexion

Vérifie que tout fonctionne:

```bash
python data_collector.py
```

Tu devrais voir le prix ETH et ton solde.

## 📊 Étape 2: Backtest (OBLIGATOIRE)

**NE SAUTE JAMAIS CETTE ÉTAPE!**

Teste la stratégie sur l'historique:

```bash
python backtest.py
```

Le backtest te montre:
- Si la stratégie est rentable sur le passé
- Le ROI (Return On Investment)
- Le win rate (% de trades gagnants)
- Le drawdown maximum (perte maximale)

**⚠️ Si le backtest n'est pas rentable, NE LANCE PAS le bot en réel!**

## 🎯 Étape 3: Simulation (Paper Trading)

Active le mode simulation dans `config.py`:

```python
DRY_RUN = True  # Mode simulation
```

Lance le bot:

```bash
python main.py
```

Le bot va:
- Analyser le marché toutes les 5 minutes
- Afficher les signaux d'achat/vente
- Simuler les trades (sans argent réel)

**Laisse tourner au minimum 1-2 semaines en simulation!**

## 💰 Étape 4: Trading réel (Avancé)

**Seulement si le backtest ET la simulation sont concluants!**

1. Change dans `config.py`:
```python
DRY_RUN = False  # Mode réel
INITIAL_CAPITAL = 50  # Commence TRÈS petit!
```

2. Lance le bot:
```bash
python main.py
```

3. **Surveille TOUS LES JOURS** pendant le premier mois

## 📁 Structure du projet

```
bot-eth-trading/
├── config.py           # Configuration (MODIFIER EN PREMIER)
├── data_collector.py   # Récupération des prix
├── indicators.py       # Calcul des indicateurs techniques
├── strategy.py         # Logique de trading
├── trader.py          # Exécution des ordres
├── risk_manager.py    # Gestion du risque
├── main.py            # Bot principal (LANCER CELUI-CI)
├── backtest.py        # Test sur historique
└── README.md          # Ce fichier
```

## ⚙️ Configuration avancée

Dans `config.py`, tu peux modifier:

### Capital et positions
```python
INITIAL_CAPITAL = 100          # Capital de départ
POSITION_SIZE_PERCENT = 0.05   # 5% du capital par trade
MIN_ORDER_SIZE = 10            # Taille minimum d'ordre
```

### Gestion du risque
```python
STOP_LOSS_PERCENT = 0.02       # Stop-loss à 2%
TAKE_PROFIT_PERCENT = 0.04     # Take-profit à 4%
MAX_DAILY_LOSS_PERCENT = 0.10  # Arrêt si perte de 10%
```

### Indicateurs techniques
```python
RSI_OVERSOLD = 30    # Signal d'achat
RSI_OVERBOUGHT = 70  # Signal de vente
SMA_SHORT = 20       # Moyenne mobile courte
SMA_LONG = 50        # Moyenne mobile longue
```

## 🔍 Commandes utiles

```bash
# Test de connexion
python data_collector.py

# Voir les indicateurs actuels
python indicators.py

# Tester la stratégie
python strategy.py

# Backtest
python backtest.py

# Lancer le bot
python main.py
```

## 📊 Comprendre les signaux

Le bot utilise plusieurs indicateurs:

- **RSI < 30**: Survente (signal d'achat)
- **RSI > 70**: Surachat (signal de vente)
- **MACD croisement haussier**: Signal d'achat
- **MACD croisement baissier**: Signal de vente
- **EMA courte > EMA longue**: Tendance haussière
- **Prix sur bande basse Bollinger**: Support (achat)
- **Prix sur bande haute Bollinger**: Résistance (vente)

Le bot combine tous ces signaux pour décider.

## 🛡️ Sécurité

✅ **À FAIRE:**
- Toujours activer l'authentification 2FA sur Binance
- Ne jamais partager tes clés API
- Utiliser des clés API sans droit de withdrawal
- Commencer avec un capital minimal
- Tester en simulation d'abord

❌ **À NE JAMAIS FAIRE:**
- Donner le droit de withdrawal aux clés API
- Committer les clés API sur Git
- Trader plus que tu peux perdre
- Laisser le bot sans surveillance au début
- Modifier le code sans comprendre

## 📈 Optimisation

Si les résultats ne sont pas satisfaisants:

1. Ajuste les paramètres dans `config.py`
2. Relance le backtest
3. Si meilleur, teste en simulation
4. Puis seulement passe en réel

Paramètres à essayer:
- RSI_OVERSOLD: 25-35
- STOP_LOSS_PERCENT: 0.015-0.03
- POSITION_SIZE_PERCENT: 0.03-0.10

## ❓ FAQ

**Q: Le bot peut perdre de l'argent?**
R: Oui, absolument. Aucune stratégie n'est rentable à 100%.

**Q: Combien je peux gagner?**
R: Impossible à prédire. Les résultats varient énormément.

**Q: Le bot fonctionne 24/7?**
R: Oui, mais tu dois le laisser tourner sur un PC/VPS allumé en permanence.

**Q: Je peux utiliser d'autres cryptos?**
R: Oui, change `SYMBOL` dans config.py (ex: "BTC/USDT", "SOL/USDT")

**Q: Le bot s'arrête si grosse perte?**
R: Oui, il a un stop automatique à 10% de perte journalière.

**Q: Je peux modifier la stratégie?**
R: Oui, édite `strategy.py`, mais teste toujours en backtest d'abord!

## 🆘 Support

En cas de problème:

1. Vérifie que tes clés API sont correctes
2. Vérifie que tu as des USDT sur Binance
3. Regarde les logs d'erreur
4. Teste chaque module individuellement

## 📝 Logs

Le bot affiche tout dans le terminal. Pour sauvegarder les logs:

```bash
python main.py > logs.txt 2>&1
```

## 🎓 Pour aller plus loin

- Ajoute plus d'indicateurs dans `indicators.py`
- Crée des stratégies plus complexes dans `strategy.py`
- Implémente le trailing stop-loss
- Ajoute les notifications Telegram
- Teste sur plusieurs paires en parallèle

## ⚖️ Licence

Ce code est fourni à titre éducatif. Utilise-le à tes propres risques.

## 🙏 Bon trading!

Sois prudent, patient, et ne trade jamais plus que tu ne peux te permettre de perdre!
