import getopt, sys
import re
from pathlib import Path
from fontTools.ttLib import TTFont

includeStr=""
excludeStr=""
include = None
exclude = None

def extract_unicode_ranges(font_path):
    font = TTFont(font_path)
    cmap = font['cmap']
    unicode_ranges = []

    for table in cmap.tables:
        if table.isUnicode():
            for code, name in table.cmap.items():
                if (unicode_allowed(code)):
                    unicode_ranges.append(code)

    unicode_ranges = sorted(unicode_ranges)
    hex_ranges = [f'{code:04X}' for code in unicode_ranges]

    return hex_ranges

def unicode_allowed(integer):
    if (include != None and integer not in include):
        return False
    elif (exclude != None and integer in exclude):
        return False
    return True

def group_into_ranges(hex_ranges):
    if not hex_ranges:
        return []

    ranges = []
    start = prev = int(hex_ranges[0], 16)

    for hex_code in hex_ranges[1:]:
        code = int(hex_code, 16)
        if code != prev + 1 and code != prev:
            ranges.append(f'{start:04X}-{prev:04X}' if start != prev else f'{start:04X}')
            start = code
        prev = code

    ranges.append(f'{start:04X}-{prev:04X}' if start != prev else f'{start:04X}')
    return ranges

def parseUnicodes(str):
    result = set()
    separations = str.split(',')
    for sep in separations:
        r = re.split(r'-|—',sep)
        start = int(r[0], 16)
        if len(r) > 1:
            end = int(r[1], 16)
            intRange = end + 1 - start
            for i in range(intRange):
                result.add(start + i)
        else:
            result.add(start)

    return result

if __name__ == "__main__":
    arg_len = len(sys.argv)
    if arg_len < 2:
        print("Usage: python extract_unicode_ranges.py path/to/font.ttf")
        sys.exit(1)

    arguments, values = getopt.getopt(sys.argv[2:], "i:e:", ["include", "exclude"])
    
    # checking each argument
    for currentArgument, currentValue in arguments:
        if currentArgument in ("-i", "--include"):
            includeStr = currentValue.replace(" ", "")
            include = parseUnicodes(includeStr)
            print(f"Including only {includeStr}")
        elif currentArgument in ("-e", "--exclude"):
            excludeStr = currentValue.replace(" ", "")
            exclude = parseUnicodes(excludeStr)
            print(f"Exclude values {excludeStr}")

    font_path = sys.argv[1]
    hex_ranges = extract_unicode_ranges(font_path)
    unicode_ranges = group_into_ranges(hex_ranges)
    range_str = ','.join(unicode_ranges)
    file_name = f"unicode_range-{Path(font_path).stem}.txt"
    f = open(file_name, "w")
    f.write(range_str)
    f.close()

    print('Unicode Ranges:\n', range_str, '\n\n Saved to: ', file_name)