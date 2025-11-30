# IUT-Colmar-TPSupervision

## Startup ENV PROF

``` bash
docker compose -f docker-compose.prof.yaml up
```
## Startup ENV ETU

``` bash
docker compose -f docker-compose.etu.yaml up
```
Démarrer tous les containers
## Progress List

- [ ] Démarrer tous les containers Zabbix sans erreur
- [ ] Connexion au portail web de zabbix
- [ ] Faire un ping depuis le serveur vers l'agent avec zabbix_get
- [ ] Faire une découverte du réseau zabbix
- [ ] Faire une découverte du réseau prof (icmp, web, snmp)
- [ ] Monitorer les machines trouvées avec les services associés
- [ ] Monitorer SNMP
- [ ] Monitorer les vulnérabilités du server xxx
- [ ] Envoyer les alertes sur un webhook

## Architecture Zabbix en containers
![alt text](src/Zabbix-Containers.drawio.svg)

## Se connecter sur le container zbx-web sur le port 8080
 * User : Admin (avec un A maj)
 * Password : zabbix

## Ping de l'agent depuis le serveur

### Se connecter à la console du serveur
Utiliser l'utilitaire docker ou 
``` bash
docker exec -it zbx-server /bin/bash
```

### Ping via Zabbix
Depuis le serveur :

```bash
zabbix_get -s <IP_de_l'agent> -k agent.ping
```

Résultat attendu :

```
1
```

Cela confirme que :

✔ L’agent répond
✔ Le port 10050 est ouvert
✔ Le hostname est correct
✔ Le serveur Zabbix communique avec l’agent

### Récupération de la version de l'agent
Depuis le serveur :

```bash
zabbix_get -s <IP_de_l'agent> -k agent.version
```

Résultat attendu :

```
7.4.x (7.4.5)
```

 ## Discovery
 > **_NOTE:_** On va utiliser la fonction de découverte Zabbix pour faire une découverte de l'infrastructure zabbix (sur votre poste) + de l'infrastructure du prof (distante).
  * Utiliser les commandes docker pour récuperer l'adresse du réseau utilisé par les containers.
  ```
  docker network ls
  docker network inspect {name}
  ```
  * Aller dans le menu Discovery et renseigner au point 5 l'adresse de votre réseau zabbix + l'adresse du réseau du prof
  * Au point 7 renseigner les ports 
  > [!TIP]
  > On peut utiliser ICMP pour faire la découverte
  
  > [!CAUTION]
  > Renseigner les ports
  
  ![Menu Discovery](image.png)

## Utilisation de Zabbix agent2

### **🧠 Concept : Pourquoi passer à l'Agent 2 ?**

Avant de migrer, comprenons l'évolution.

* **Zabbix Agent (Legacy \- C) :** L'ancien standard. Léger et stable, mais limité.  
* **Zabbix Agent 2 (Moderne \- Go) :** C'est la nouvelle norme. Écrit en langage **Go**, il est beaucoup plus performant car il gère les vérifications en parallèle (un check lent ne bloque pas les autres). De plus, il supporte nativement des **plugins** (PostgreSQL, Docker, MongoDB) sans scripts complexes.

### **🧠 Concept : Passif vs Actif (Le choix crucial)**

* **Mode Passif (Serveur ➔ Agent) :** Le serveur demande "Quelle est ta CPU ?". L'agent répond. Simple, mais bloqué par le NAT.  
* **Mode Actif (Agent ➔ Serveur) :** L'agent contacte le serveur : *"Bonjour, donne-moi ma configuration"*. Le serveur envoie la liste des items. L'agent envoie ensuite les données de lui-même (Push).  
  * *Avantage :* Traverse les pare-feux/NAT et soulage le serveur Zabbix.  
  * *Bonne pratique :* Toujours privilégier le **mode Actif**.

Voici le texte formaté en Markdown, prêt à être intégré dans votre support de cours. J'ai ajouté des éléments visuels (code blocks, listes, citations) pour faciliter la lecture par les apprenants.

-----

### 🔌 Mode Passif ou Mode Actif ?

Pour l'Agent 2 (que ce soit sur Linux ou Windows), la recommandation est claire :

> **🏆 Le Mode ACTIF est le grand gagnant.**
>
> C'est la recommandation officielle pour 95% des infrastructures modernes, surtout avec Zabbix 7.4.

Voici pourquoi, expliqué simplement pour vos apprenants :

#### 1\. La raison n°1 : Les Pare-feux et le NAT

C'est l'argument décisif.

  * **Mode Passif** (Serveur ➔ Agent) :

      * Le serveur Zabbix essaie d'entrer chez le client (`Serveur -> Port 10050`).
      * 🔴 **Problème :** Si votre Windows ou Linux est derrière une Box Internet, un routeur NAT, ou dans le Cloud (AWS/Azure), ça bloque. Vous devez ouvrir des ports et faire du "Port Forwarding" partout.

  * **Mode Actif** (Agent ➔ Serveur) :

      * L'agent sort vers le serveur (`Agent -> Port 10051`).
      * 🟢 **Avantage :** La plupart des pare-feux autorisent le trafic sortant par défaut. **Ça marche immédiatement**, sans toucher au réseau.

#### 2\. La "Mémoire Tampon" (Buffer) - Vital \!

C'est une fonctionnalité exclusive au mode Actif.

  * **Scénario :** Votre connexion internet coupe pendant 1 heure.
  * **En Passif :** Le serveur n'a pas pu contacter l'agent. Il y a un "trou" dans les graphiques. La donnée est perdue à jamais.
  * **En Actif :** L'Agent 2 stocke les données en mémoire (Buffer). Dès que la connexion revient, il envoie tout l'historique d'un coup. **Aucune perte de données.**

#### 3\. La Performance (Scalabilité)

  * **En Passif :** Le serveur Zabbix doit gérer un chronomètre pour chaque hôte (*"Est-ce que c'est l'heure de demander la CPU à Windows ?"*). Si le réseau est lent, le serveur "attend" et ses processus s'engorgent.
  * **En Actif :** Le serveur envoie juste la liste des courses (la config) au début. Ensuite, c'est l'Agent qui gère son propre timing. Le serveur ne fait que "recevoir et stocker". C'est beaucoup plus léger pour le serveur Zabbix.

-----

### ⚠️ Attention à la configuration

Pour que le mode Actif fonctionne, il faut impérativement vérifier deux choses :

#### 1\. Côté Fichier de config (`zabbix_agent2.conf`)

Vous devez remplir le champ `ServerActive`.

```ini
# Le mode Passif utilise ce champ
Server=ip_nginx #(ex: 172.18.0.4)

# Le mode Actif utilise OBLIGATOIREMENT ce champ (et le précédent - bug)
ServerActive=ip_nginx #(ex: 172.18.0.4)

# Indispensable en Actif : Le nom de l'agent doit être EXACTEMENT celui dans l'interface Web
Hostname=nginx
```
⚠️ Penser à redémarrer le service zabbix_agent2
``` bash
/etc/init.d/zabbix-agent2 restart
```
#### 2\. Côté Interface Web (Templates)

C'est l'erreur classique des débutants. Si vous configurez l'agent en actif mais que vous appliquez un template passif, rien ne remontera.

  * ❌ **Ne prenez pas :** `Windows by Zabbix agent` (Souvent passif par défaut).
  * ✅ **Prenez :** `Windows by Zabbix agent active`.

> **📝 Résumé pour l'atelier :**
> "Pour vous simplifier la vie avec le réseau et ne pas perdre de données, configurez toujours vos serveurs en **Mode Actif** et choisissez les templates finissant par **'Active'**."

😎 Les agents2 sont déjà installé sur certains hôtes.

### Installation zabbix agent2 (sur pc prof)
``` bash
docker exec -it iut-colmar-tpsupervision-nginx-1 bash
apt update && apt install zabbix-agent2
```
### Ajout de l'hote dans Zabbix
 ![Nginx Add Host](src/Nginx-Add-Host.png)

  ## TIPS
  **Liste des containers**
  * zbx-web
  * zbx-server
  * zbx-postgres

  ### DOCKER TIPS
   * Connection à un système docker en bash
   ``` bash
   docker exec -it <name> bash
   ```

   ### ENV PROF TIPS
   * Connection du server Zabbix au lab_network
   ``` bash
   docker network connect lab_network zbx-server
   ```