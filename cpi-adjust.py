#!/usr/bin/python3

"""
Generate inflation-adjusted version of NaszBudżet.md 

Usaage:
        ./cpi-adjust.py NaszBudżet.md > NaszBudżet-cpi.md
"""

import sys
import os
from decimal import Decimal
import re

def readLines():
    ipath = sys.argv[1]
    f = open(ipath)
    lines = f.readlines()
    f.close()
    return lines

def getTableRows(lines):
    head = []
    table = [] 
    tail = []

    for line in lines:
        line = line.strip()
        if line.startswith("|"):
            table.append([x.strip() for x in line.split("|")])
        else:
            if not table:
                head.append(line)
            else:
                tail.append(line)
    return head, table, tail

def getCpiMultipliers(table):
    lcpi = table[2]
    cpi_last = Decimal(lcpi[-2])
    return [cpi_last/Decimal(x) for x in lcpi[2:-1]]

def getLastYear(table):
    return table[0][-2].strip()

def listOfTuples(l1, l2):
    return list(map(lambda x, y:(x,y), l1, l2))

REGEXP_NUMBER = re.compile(r'^(\*\*)?([0-9,]+)(\[\^.+\])?(\*\*)?$')

def adjustNumber(tt):
    w, mul = tt
    mo = re.match(REGEXP_NUMBER, w)
    snum = mo.group(2) if mo else w
    if mo:
        snum = mo.group(2)
        snum = snum.replace(',','') # Remove group separators, if any.
        num = Decimal(snum) * mul
        # TODO: Restore original formatting:
        g1 = mo.group(1) if mo.group(1) else ""
        g3 = mo.group(3) if mo.group(3) else ""
        g4 = mo.group(4) if mo.group(4) else ""
        num = f'''{g1}{num.quantize(Decimal('1.')):,}{g3}{g4}'''
        return num
    else:
        return w # Not a number.

def getCipAdjustedTableLines(table, cpi_mul):
    table_lines = []
    table_lines.append(" | ".join(table[0]).strip())
    table_lines.append(" | ".join(table[1]).strip())
    for ww in table[3:]:
        ll = [adjustNumber(tt) for tt in listOfTuples(ww[2:-1], cpi_mul)]
        ll = ww[:2] + ll + ww[-1:]
        ll = [f' {x} ' for x in ll]
        table_lines.append("|".join(ll).lstrip())
    return table_lines

def main():
    lines = readLines()
    head, table, tail = getTableRows(lines)
    cpi_mul = getCpiMultipliers(table)
    table_lines_cpi_adjusted = getCipAdjustedTableLines(table, cpi_mul)

    head[0] += " (inflation adjusted)"
    head[2] = head[2].replace(" CAD **nominalnych**:", f" CAD **y{getLastYear(table)}**:")
    head[3] = "([see nominal version](NaszBudżet))"
    ll = head + table_lines_cpi_adjusted + tail
    for x in ll:
        print(x)

if __name__ == "__main__":
    sys.exit(main())
