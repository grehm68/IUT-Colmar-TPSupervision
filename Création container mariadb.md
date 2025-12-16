# Création container mariadb

```bash
docker pull mariadb:10.11
docker run --name mariadb -e MYSQL_ROOT_PASSWORD=password -d -p 3306:3306 mariadb:latest
docker network connect zbx-net mariadb

```

## Installation agent zabbix

### ajout repo zabbix
```bash
wget https://repo.zabbix.com/zabbix/7.4/release/ubuntu/pool/main/z/zabbix-release/zabbix-release_latest_7.4+ubuntu24.04_all.deb
dpkg -i zabbix-release_latest_7.4+ubuntu24.04_all.deb
apt update && apt install zabbix-agent2
```

### Configuration agent (identique)
* Utiliser le template Mysql Active
* Spécifier le user et le password via les macros