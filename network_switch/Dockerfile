# Utiliser une image de base Alpine Linux légère
FROM alpine:latest

# Mettre à jour le cache des paquets et installer net-snmp et les outils associés
# net-snmp-mibs installe les fichiers MIB standards, ce qui peut aider l'agent
RUN apk add --no-cache net-snmp net-snmp-tools net-snmp-libs

# Créer les répertoires nécessaires pour la configuration et les données persistantes de snmpd
RUN mkdir -p /etc/snmp /var/net-snmp

# Copier le fichier de configuration snmpd.conf personnalisé dans le conteneur
COPY snmpd.conf /etc/snmp/snmpd.conf

# Exposer le port SNMP standard (UDP 161)
EXPOSE 161/udp

# Commande pour démarrer l'agent snmpd
# -f: exécute au premier plan (nécessaire pour Docker)
# -LS0-7e: redirige les logs vers stderr avec tous les niveaux de priorité (de 0 à 7)
# -C: ne pas lire les configurations par défaut des emplacements standards
# -c /etc/snmp/snmpd.conf: spécifie le fichier de configuration à utiliser
# -Doverride,read_config,mib_init: active le débogage pour les directives 'override', la lecture de la config et l'initialisation des MIBs (utile pour le dépannage)
CMD ["snmpd", "-f", "-Le", "-C", "-c", "/etc/snmp/snmpd.conf", "-Doverride,read_config,mib_init"]