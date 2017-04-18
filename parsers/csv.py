def decode_csv(text, delimiter=','):
    table = [line.split(delimiter) for line in text.split('\n')]
    if len(table[-1][-1]) == 0:
        table.remove(table[-1])
    return table


def encode_csv(table, delimiter=','):
    output = "sep=" + delimiter + "\n"
    for line in table:
        for cell in line:
            output += str(cell)
            if not cell == line[-1]:
                output += delimiter
        output += "\n"
    return output


def drop_field(table, *num):
    table = table[:]
    for line in table:
        for f in num:
            line.remove(line[f])
    return table


def truncate_table(table, length):
    table = [line[:length] for line in table[:]]
    return table
