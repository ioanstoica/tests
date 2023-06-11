from collections import defaultdict

def extract_domain(address):
    parts = address.split('.')
    return parts[-2] if len(parts) > 1 else parts[0]

# Citirea fisierului
with open('blacklist.log', 'r') as file:
    lines = file.readlines()

total_lines = len(lines)

# Crearea dictionarului
domain_dict = defaultdict(int)

for line in lines:
    domain = line.split('->')[0].strip()
    key = extract_domain(domain)
    domain_dict[key] = 0  # initializarea valorilor dictionarului cu 0

for key in domain_dict.keys():
    for line in lines:
        if key in line:
            domain_dict[key] += 1  # incrementarea valorilor dictionarului atunci cand cheia se gaseste in linia respectiva


# Crearea fisierului de statistici
with open('stats_blacklist.log', 'w') as file:
    for key, value in sorted(domain_dict.items(), key=lambda item: item[1], reverse=True):
        percent = (value / total_lines) * 100
        file.write(f"{key} {value}/{total_lines} = {percent:.2f}%\n")
