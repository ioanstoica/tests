# Pornire server:
python dns.py

# Testare server:
nslookup infoarena.ro 127.0.0.1

# Informatii utile:
netstat -aon | findstr :53   //afiseaza daca portul 53 e ocupat:

Pentru schimbarea serverului de DNS pe Windows: 
  Manage Network Adapter settings -> Network adapters -> expand curent network -> View additional properties -> DNS server assignment Edit -> change Automatic to Manual ->  turn on IPv4 -> Prefferred DNS: 127.0.0.1 and Alternate DNS: 127.0.0.1 -> Save

Alte liste de addservere: https://github.com/blocklistproject/Lists.git

