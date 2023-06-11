# Create a Add Blocker DNS server 
import socket
from scapy.all import IP, UDP,sr1, DNS, DNSQR, DNSRR
from concurrent.futures import ThreadPoolExecutor 

# Extrage domeniul targetat din request-ul DNS
# Source: https://github.com/howCodeORG/howDNS/blob/master/dns.py - functia getquestiondomain
def extract_domain(data):
    data = data[12:]
    state = 0
    expected_length = 0
    domain_string = ''
    domain_parts = []
    x = 0
    for byte in data:
        if state == 1:
            if byte != 0:
                domain_string += chr(byte)
            x += 1
            if x == expected_length:
                domain_parts.append(domain_string)
                domain_string = ''
                state = 0
                x = 0
            if byte == 0:
                domain_parts.append(domain_string)
                break
        else:
            state = 1
            expected_length = byte
    
    return '.'.join(domain_parts[:-1]) # domain_parts = a list like  ['api', 'github', 'com', '']

# Get the IP address of a hostname
# Source: curs - https://github.com/senisioi/computer-networks/tree/2023/capitolul6#exemplu-dns-request
def get_ip_address(hostname):
    try:
        # DNS request către google DNS
        ip = IP(dst = '8.8.8.8')
        transport = UDP(dport = 53)
        dns = DNS(rd = 1)  # rd = 1 cod de request

        # query pentru a afla entry de tipul 
        byte_hostname= hostname.encode()
        dns_query = DNSQR(qname=byte_hostname, qtype=1, qclass=1)
        dns.qd = dns_query

        answer = sr1(ip / transport / dns)

        return answer[DNS].an.rdata
    except Exception as e:
        print("Failed to retrieve the IP address of", hostname, "with socket.gaierror", e)
        return '0.0.0.0'


# Solve the DNS request
# Source: curs - https://github.com/senisioi/computer-networks/tree/2023/capitolul6#micro-dns-server 
def dns_thread(request, source_address, socket_udp, blacklist):
    # converitm payload-ul in pachet scapy
    packet = DNS(request)
    dns = packet.getlayer(DNS)

    # Verificam daca este un request valid
    if dns is None or dns.opcode != 0:  
        print("Invalid DNS request")
        return

    # Extragem domeniul interogat
    domain =  extract_domain(request) # domain is like 'api.github.com'
    print("Domain request:" , domain)

    # Obtinem IP-ul pentru domeniul interogat
    if domain in blacklist:
        print(f"Domain {domain} is blacklisted")
        with open("blacklist.log", "a") as f:
            f.write(f"{domain}\n")
        response_ip = "0.0.0.0"
    else:
        response_ip = get_ip_address(domain)
        with open("whitelist.log", "a") as f:
            f.write(f"{domain} -> {response_ip}\n")

    print("Qry -> Ans:" , domain, "->" ,response_ip)
   
    # Construim raspunsul
    dns_answer = DNSRR(  # DNS Reply
        rrname=dns.qd.qname,  # for question
        ttl=330,  # DNS entry Time to Live
        type="A",
        rclass="IN",
        rdata=response_ip,
    ) 

    dns_response = DNS(
        id=packet[DNS].id,  # DNS replies must have the same ID as requests
        qr=1,  # 1 for response, 0 for query
        aa=0,  # Authoritative Answer
        rcode=0,  # 0, nicio eroare http://www.networksorcery.com/enp/protocol/dns.htm#Rcode,%20Return%20code
        qd=packet.qd,  # request-ul original
        an=dns_answer,
    )  # obiectul de reply

    # Trimitem raspunsul
    socket_udp.sendto(bytes(dns_response), source_address)


# Create a DNS server
# That will block adservers
def dns_add_blocker_server():
    host = "127.0.0.1"
    port = 53

    # Citim lista de domenii blacklistate
    blacklist = []
    with open("adservers.txt", "r") as f:
        for line in f:
            blacklist.append(line.strip())

    # Create a socket object and bind it to a port
    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
    socket_udp.bind((host, port))

    print("DNS server started at host:", host, "port:", port)

    # Listen for incoming requests, and handle them in a separate thread
    # Creeaza un thread pool cu 100 de threaduri
    with ThreadPoolExecutor(max_workers=100) as executor:
        while True:
            try:
                # Wait for a request
                request, source_address = socket_udp.recvfrom(65535)

                # Handle the request in a separate thread
                executor.submit(dns_thread, request, source_address, socket_udp, blacklist)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print("Exception:", e)
                continue

    # Close the socket when done 
    socket_udp.close()

# Run the DNS server
if __name__ == "__main__":
    dns_add_blocker_server()