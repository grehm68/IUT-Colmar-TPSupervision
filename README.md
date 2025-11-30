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
- [ ] Montorer SNMP
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