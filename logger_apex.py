# logger_apex.py - Système de logging pour APEX (V2.4 - Sans duplication)

import logging
from datetime import datetime
import os

class ApexLogger:
    """
    Logger personnalisé pour le bot APEX

    V2.4: Protection contre la duplication de handlers
    - Vérifie si des handlers existent déjà avant d'en ajouter
    - Instance singleton garantie via get_logger()
    """

    def __init__(self, log_to_file=True, log_to_console=True):
        """Initialise le logger"""
        self.logger = logging.getLogger("ApexPredator")
        self.logger.setLevel(logging.INFO)

        # 🔧 PROTECTION: Évite la duplication de handlers
        # Si le logger a déjà des handlers, on ne les recrée pas
        if self.logger.handlers:
            return

        # Crée le dossier logs s'il n'existe pas
        if log_to_file and not os.path.exists('logs'):
            os.makedirs('logs')

        # Format des logs
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler fichier
        if log_to_file:
            log_filename = f"logs/apex_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_filename, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Handler console (optionnel)
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)  # Seulement warnings en console
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def info(self, message):
        """Log niveau INFO"""
        self.logger.info(message)

    def warning(self, message):
        """Log niveau WARNING"""
        self.logger.warning(message)

    def error(self, message):
        """Log niveau ERROR"""
        self.logger.error(message)

    def trade(self, action, price, quantity, reason=""):
        """Log spécial pour les trades"""
        msg = f"TRADE | {action.upper()} | Price: ${price:.2f} | Qty: {quantity:.6f}"
        if reason:
            msg += f" | Reason: {reason}"
        self.logger.info(msg)

    def signal(self, apex_score, decision, confidence):
        """Log spécial pour les signaux"""
        msg = f"SIGNAL | APEX: {apex_score:.1f} | Decision: {decision.upper()} | Confidence: {confidence:.0f}%"
        self.logger.info(msg)


# Instance globale
_apex_logger = None

def get_logger():
    """Retourne l'instance du logger"""
    global _apex_logger
    if _apex_logger is None:
        _apex_logger = ApexLogger()
    return _apex_logger


# Test
if __name__ == "__main__":
    logger = get_logger()
    logger.info("Test du logger APEX")
    logger.trade("BUY", 3420.50, 0.029, "APEX Score > 85")
    logger.signal(87.5, "buy", 89)
    print("✅ Logger testé - Vérifie le fichier logs/apex_YYYYMMDD.log")
