# board = {}
# want to see weights
def visualize_board(weight, width, height):
    # header
    header = '  '
    line = '--'
    for w in range(width):
        header += (str(w) + ' ') if w > 10 else (' ' + str(w) + ' ')
        line += '---'
    print(header)
    print(line)

    for i in range(height):
        s = str(i) + '|'
        for j in range(width):
            if (j, i) not in weight:
                s += '00 '
            elif weight[(j,i)] < 10:
                s += '0' + str(weight[(j,i)]) + ' '
            else:
                s += str(weight[(j,i)]) + ' '
        s.strip()
        print(s)