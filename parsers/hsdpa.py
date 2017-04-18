import re

from parsers.csv import decode_csv, encode_csv, drop_field, truncate_table


def sanitise(table):
    table = table[:]
    table = truncate_table(table, 12)
    table = drop_field(table, 6, 5, 4, 3, 1, 0)
    return table


def bill(table):
    lines = []
    for line in table:
        if "No Service" in line[1]:
            line.append(18.42)
        elif "Hard Cap" in line[1]:
            cap = [int(s) for s in re.findall(r'\b\d+', line[1])][0]
            line.append(cap * 14.2)
        elif "Consumer Connect" in line[1]:
            speed = [int(s) for s in re.findall(r'\b\d+', line[1])][0]
            if speed >= 4096:
                line.append(587.07)
                line.remove(line[1])
            elif speed >= 2048:
                line.append(491.23)
                line.remove(line[1])
            elif speed >= 1024:
                line.append(491.23)
                line.remove(line[1])
            elif speed >= 512:
                line.append(491.23)
                line.remove(line[1])
        line.remove(line[1])
        lines.append(line)
    return lines


delimiter = ';'

# Ask for file locations
report = input("Report?\t")
# output = input("Target?\t")
clients = input("Clients?\t")
# pricing = input("Pricing?\t")

# Open files
report = open(report)
# output = open(output, 'a')
clients = open(clients)
# pricing = open(pricing)

# Read files
report = report.read()
clients = clients.read()
# pricing = pricing.read()

# Decode files
report = decode_csv(report, delimiter)
clients = decode_csv(clients, delimiter)

report = sanitise(report)
for r in report:
    for c in clients:
        for cell in c:
            if r[0] in cell:
                r[0] = c[0]

# Encode files
report = encode_csv(report, delimiter)


print(report)
