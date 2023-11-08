#!/usr/bin/python3
# coding: utf-8

'''
Publishing generated .md pages:

    $ cd /media/veracrypt1/zr/timeline/md/rogowskz.github.io

    $ python3 NaszBudżet.py
    $ git add NaszBudżet.md NaszBudżet-cpi.md NaszBudżet.yaml NaszBudżet.py 
    $ git commit -m "Updated NaszBudżet"

    # git push ... to the remote git repository on GitHub (instrukcje są w HasłaLista)


TODO: Update 'gh' cli client:
    A new release of gh is available: 2.14.2 → 2.38.0
    https://github.com/cli/cli/releases/tag/v2.38.0

'''

import sys
import os
from datetime import datetime
from decimal import Decimal
import re

import yaml

cwd = os.getcwd()
APPHOME, _ = os.path.split(sys.argv[0])
APPHOME = os.path.abspath(APPHOME)

REGEXP_NUMBER = re.compile(r'^(\*\*)?([0-9,]+)(\[\^.+\])?(\*\*)?$')

def readYaml(fpath):
    with open(fpath) as f:
        txt = f.read()
    return yaml.load(txt, Loader=yaml.FullLoader)

def emitDocHeader(dd):
    return f'''# Nasz budżet

Prywatne[^prywatne] wydatki roczne w CAD **nominalnych**    
([see inflation adjusted version](NaszBudżet-cpi))
'''

def emitEmptyTableRow(nn):
    return f'''{'|      ' * nn}|\n'''

def emitTableHeader(dd):

    dcpi = dd["CPI"]
    yrs = list(dcpi)
    yrs.sort()
    yrs = [str(x) for x in yrs]

    txt = ""
    txt += "\n"
    txt += f'''| Rok | {' | '.join(yrs)} |\n'''
    txt += f'''| --- | {'  | '.join(["--:" for x in yrs])}  |\n'''
    txt += f'''| [CPI](https://www.bankofcanada.ca/rates/price-indexes/cpi/)[^cpi] | {' | '.join([str(x) for x in list(dcpi.values())])} |\n'''

    return txt

def summarizeCategoriesInGroupByYears(lista_grupy):

    # Add initial dictionary of group summary values:
    if len(lista_grupy[0]) == 1:
        # Dictionary of group summary values is not yet present.
        keys = list(lista_grupy[1][1])
        dd_grupy = {key:value for key, value in zip(keys, [0 for k in keys])}
        lista_grupy[0].append(dd_grupy)
    else:
        # Dictionary of group summary values is already present.
        #
        # Replace 'None' values with zeros:
        dd_grupy = lista_grupy[0][1]
        dd_grupy = {key:value for key, value in zip(list(dd_grupy), [0 if v is None else v for v in list(dd_grupy.values())]  )}
        lista_grupy[0][1] = dd_grupy

    # For each category, add values to the dictionary of expenses in the group:
    for ll_category in lista_grupy[1:]:
        dd_category_values = ll_category[1]
        # Replace 'None' values with zeros:
        dd_category_values = {key:value for key, value in zip(list(dd_category_values), [0 if v is None else v for v in list(dd_category_values.values())]  )}
        for year in dd_category_values:
            group_value_for_year = lista_grupy[0][1][year]
            category_value_for_year = dd_category_values[year]
            if type(category_value_for_year) == type(""):
                # Category value for this year is annotated.
                # Extract integer value from this string:
                category_value_for_year = int(category_value_for_year[:category_value_for_year.index("[")])
            if type(group_value_for_year) == type(0):
                # Group value for this year is NOT annotated.
                # Can add integer category value:
                lista_grupy[0][1][year] += category_value_for_year 
            else:
                # Group value for this year is annotated.
                # Extract curent group value from this string, add category value and assemble updated group value with annotation again:
                idx = group_value_for_year.index("[")
                head = group_value_for_year[:idx]
                tail = group_value_for_year[idx:]
                lista_grupy[0][1][year] = f'''{int(head)+category_value_for_year}{tail}'''

    #
    return lista_grupy

def emitAnnotations(dd):
    return f'''\n{"""
""".join(dd["Annotacje"])}'''

def emitTimestamp():
    return f'''\n\nUpdated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'''

def formatAnnotatedIntegerValue(x):
    idx = x.index("[")
    head = x[:idx]
    tail = x[idx:]
    return f'''{int(head):,}{tail}'''

def formatIntegerValue(x):
    if type(x) == type(0):
        # Format integer value:
        return f'''{x:,}'''
    else:
        # Format annotated integer value:
        return formatAnnotatedIntegerValue(x)

def emitGroup(lista_grupy):

    nazwa_grupy = lista_grupy[0][0]
    dd_grupy = lista_grupy[0][1]

    txt = ""
    txt += emitEmptyTableRow(len(dd_grupy)+1)

    # Emit group header row (group name and group summary values for years):
    values = []
    for x in list(dd_grupy.values()):
        values.append(formatIntegerValue(x))
    values = [f'''**{x}**''' for x in values]
    txt += f'''| **{nazwa_grupy}** | {' | '.join(values)} |\n'''

    # Emit group category rows (category name and category values for years):
    for kategoria in lista_grupy[1:]:
        nazwa_kategorii = kategoria[0]
        dd_kategorii = kategoria[1]
        values = []
        for x in [x if x is not None else 0 for x in list(dd_kategorii.values())]:
            values.append(formatIntegerValue(x))
        txt += f'''| {nazwa_kategorii} | {' | '.join(values)} |\n'''

    return txt

def summarizeGroups(list_of_groups):
    keys = list(list_of_groups[0][0][1])
    ddd = {key:value for key, value in zip(keys, [0 for k in keys])}
    for x in list_of_groups:
        dd = x[0][1]
        for k in dd:
            val = dd[k]
            if type(val) == type(""):
                val = int(val[:val.index("[")])
            ddd[k] += val
    return ddd

def writeTextToFile(txt, fpath):
    with open(fpath, 'w') as f:
        f.write(txt)

def getTableRows(lines):
    head_rows = []
    table_rows = [] 
    tail_rows = []

    for line in lines:
        line = line.strip()
        if line.startswith("|"):
            table_rows.append([x.strip() for x in line.split("|")])
        else:
            if not table_rows:
                head_rows.append(line)
            else:
                tail_rows.append(line)
    return head_rows, table_rows, tail_rows

def getCpiMultipliers(table):
    lcpi = table[2]
    cpi_last = Decimal(lcpi[-2])
    return [cpi_last/Decimal(x) for x in lcpi[2:-1]]

def getLastYear(table):
    return table[0][-2].strip()

def listOfTuples(l1, l2):
    return list(map(lambda x, y:(x,y), l1, l2))

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

def generateCpiAdjusted(txt):
    lines = txt.split("\n")
    head_rows, table_rows, tail_rows = getTableRows(lines)
    cpi_mul = getCpiMultipliers(table_rows)
    table_lines_cpi_adjusted = getCipAdjustedTableLines(table_rows, cpi_mul)
    #
    head_rows[0] += " (inflation adjusted)"
    head_rows[2] = head_rows[2].replace(" CAD **nominalnych**", f" CAD **y{getLastYear(table_rows)}**    ")
    head_rows[3] = "([see nominal version](NaszBudżet))"
    ll = head_rows + table_lines_cpi_adjusted + tail_rows
    return "\n".join(ll)

def main():
    dd = readYaml(os.path.join(APPHOME, 'NaszBudżet.yaml'))

    # TODO: Refactor into a function:
    txt_wreg = ""
    ll = []
    for lista_grupy in dd["Wydatki regularne"]:
        lista_grupy = summarizeCategoriesInGroupByYears(lista_grupy)
        txt_wreg += emitGroup(lista_grupy)
        ll.append(lista_grupy)
    wreg_total = [["Wydatki regularne", summarizeGroups(ll)]]

    # TODO: Refactor into a function:
    txt_wnreg = ""
    ll = []
    for lista_grupy in dd["Wydatki duże i nieregularne[^dniereg]"]:
        lista_grupy = summarizeCategoriesInGroupByYears(lista_grupy)
        txt_wnreg += emitGroup(lista_grupy)
        ll.append(lista_grupy)
    wnreg_total = [["Wydatki duże i nieregularne[^dniereg]", summarizeGroups(ll)]]

    wrazem = [["Wydatki razem", summarizeGroups([wreg_total, wnreg_total])]]

    txt = ""
    txt += emitDocHeader(dd)
    txt += emitTableHeader(dd)
    txt += emitGroup(wrazem)
    txt += emitGroup(wreg_total)
    txt += txt_wreg
    txt += emitGroup(wnreg_total)
    txt += txt_wnreg
    txt += emitAnnotations(dd)
    txt += emitTimestamp()

    # print(txt)
    writeTextToFile(txt, os.path.join(APPHOME, 'NaszBudżet.md'))
    writeTextToFile(generateCpiAdjusted(txt), os.path.join(APPHOME, 'NaszBudżet-cpi.md'))

if __name__ == "__main__":
    sys.exit(main())
