from kafka import KafkaProducer
import time
import logging

# On ne crée pas l'instance ici globalement pour éviter le crash au boot
_produceur = None

def get_producer():
    global _produceur
    if _produceur is None:
        # Tentative de connexion avec plusieurs essais
        for i in range(5):
            try:
                _produceur = KafkaProducer(
                    bootstrap_servers="kafka:9092",
                    api_version=(3, 0, 0) # Forcer la version évite l'auto-check qui crash
                )
                return _produceur
            except Exception as e:
                print(f"Connexion Kafka échouée (essai {i+1}/5)...")
                time.sleep(5)
        raise Exception("Kafka est injoignable.")
    return _produceur

def sendData(topic, data):
    try:
        p = get_producer()
        p.send(topic, value=str(data).encode('utf-8'))
    except Exception as e:
        print(f"Erreur d'envoi Kafka : {e}")