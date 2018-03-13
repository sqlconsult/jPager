def main():

    res_words = [ 'and', 'del', 'from', 'not', 'while', 'as', 'elif', 'global', 'or',
                  'with', 'assert', 'else', 'if', 'pass', 'yield', 'break', 'except',
                  'import', 'print', 'class', 'exec', 'in', 'raise', 'continue',
                  'finally', 'is', 'return','def', 'for', 'lambda', 'try',
                  'structure', 'index', 'request']
    numbers = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' ]

    names_to_write = []
    with open('namespace.md', 'r') as g:
        for line in g:
            newline = line[:-1]
            name = newline
            if name in res_words:
                name = name + '_1'

            if name[0] in numbers:
                name = '_' + name

            stem = ''.join([ c if c.isalnum() else '_1' for c in name ])

            if stem not in names_to_write:
                names_to_write.append(stem)

    names_to_write.sort()
    with open('namespace.txt', 'w+') as f:
        for n in names_to_write:
            f.write(n + '\n')

if __name__ == '__main__':
    main()
