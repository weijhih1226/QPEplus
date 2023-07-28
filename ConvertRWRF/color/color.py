from pathlib import Path
homeDir = r'C:\Users\Showlong\Documents\QPEplus\color'
def read_colors(name):
    inPath = Path(fr'{homeDir}\{name}.color')
    with open(inPath) as f:
        colors = []
        line = f.readline().strip()
        while line:
            colors.append(line)
            line = f.readline().strip() 
    return colors

def main(name = 'dbz_65'):
    colors = read_colors(name)
    print(colors)

if __name__ == '__main__':
    name = 'dbz_65'
    main(name)