import re

from csv import decode_csv

report = input("Report?\t")
output = input("Target?\t")
clients = input("Clients?\t")
#pricing = input("Pricing?\t")

report = open(report)
output = open(output, 'a')
clients = open(clients)
#pricing = open(pricing)

report = report.read()
clients = clients.read()
#pricing = pricing.read()


def split(text, delimiter):
    lines = []
    text = text[:]
    while True:
        match = re.search(delimiter, text)
        if match is not None:
            line = text[text.find(match.group(0)):]
            end = re.search(delimiter, line[len(match.group(0)):])
            if end is not None:
                line = line[0: line.find(end.group(0))]
            text = text[text.find(match.group(0)) + len(match.group(0)):]
            line = line.replace("\n", " ")
            lines.append(line)
        else:
            break
    return lines


def sanitise(table):
    lines = []
    for line in table:
        if "used" in line:
            line = re.sub(r'\t *used *\t', r'\t', line)
            line = re.sub(r' *\t *', r'\t', line)
            line = line.split("\t")[:4]
            #line.remove(line[3])
            #line.remove(line[1])
            line[1] = re.sub(r' => .*', r'', line[1])
            lines.append(line)
    return lines


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


def format(table, seperator=','):
    output = ""
    for line in table:
        for cell in line:
            output += str(cell)
            if not cell == line[-1]:
                output += seperator
        output += "\n"
    return output

clients = decode_csv(clients, ';')
output.write(format(sanitise(split(report, r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"))))
