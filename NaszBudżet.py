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

REGEXP_NUMBER = re.compile(r'^(\*\*)?(-?[0-9,]+)(\[\^.+\])?(\*\*)?$')

def readYaml(fpath):
    with open(fpath) as f:
        txt = f.read()
    return yaml.load(txt, Loader=yaml.FullLoader)

def emitDocHeader():
    return f'''# Nasz budżet

Prywatne[^prywatne] wydatki roczne w CAD **nominalnych**    
([see inflation adjusted version](NaszBudżet-cpi))
'''

def emitEmptyTableRow(nn):
    return f'''{'|      ' * nn}|\n'''

def emitTableHeader(yrs, dd_data):
    txt = ""
    txt += "\n"
    txt += f'''| Rok | {' | '.join([str(x) for x in yrs])} |\n'''
    txt += f'''| ---- | {'  | '.join(["---:" for x in yrs])}  |\n'''
    vals = [dd_data["CPI"][y] for y in yrs]
    txt += f'''| [CPI](https://www.bankofcanada.ca/rates/price-indexes/cpi/)[^cpi] | {' | '.join([str(x) for x in vals])} |\n'''
    return txt

def trimDictAndZeroNones(dd, yrs):
    # Trim dictionary to the range of years and replace 'None' values with zeros:
    keys = list(dd)
    for k in keys:
        if k not in yrs:
            del dd[k]
    return {key:value for key, value in zip(list(dd), [0 if v is None else v for v in list(dd.values())])}

def summarizeCategoriesInGroupByYears(lista_grupy, yrs):

    # Add initial dictionary of group summary values:
    if len(lista_grupy[0]) == 1:
        # Dictionary of group summary values is not yet present.
        dd_grupy = {key:value for key, value in zip(yrs, [0 for k in yrs])}
        lista_grupy[0].append(dd_grupy)
    else:
        # Dictionary of group summary values is already present.
        lista_grupy[0][1] = trimDictAndZeroNones(lista_grupy[0][1], yrs)

    # For each category, add values to the dictionary of expenses in the group:
    for ll_category in lista_grupy[1:]:
        dd_category_values = ll_category[1]
        dd_category_values = trimDictAndZeroNones(dd_category_values, yrs)
        for year in dd_category_values:
            group_value_for_year = lista_grupy[0][1][year]
            category_value_for_year = dd_category_values[year]
            if type(category_value_for_year) == type(""):
                # Category value for this year is annotated.
                # Extract integer value from this string:
                try:
                    val = category_value_for_year[:category_value_for_year.index("[")]
                except ValueError: # substring "[" not found.
                    print(f'''category_value_for_year: {category_value_for_year}''')
                    print()
                    raise
                    sys.exit()
                category_value_for_year = int(val)
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

def generateCipAdjustedTableLines(table_rows, cpi_mul):
    # 'table_rows' is a list of lists of table columns
    table_lines = []
    table_lines.append(    f'''{" | ".join(table_rows[0]).strip()}'''    )
    table_lines.append(    f'''{" | ".join(table_rows[1]).strip()}'''    )
    #
    for cols in table_rows[3:]:
        ll = [adjustNumber(tt) for tt in listOfTuples(cols[2:-1], cpi_mul)]
        ll = cols[:2] + ll + cols[-1:]
        ll = [f' {x} ' for x in ll]
        table_lines.append(    f'''{"|".join(ll).lstrip()}'''    )
    return table_lines

def generateTableLinesWithAverages(table_rows):
    # 'table_rows' is a list of lists of table columns
    #
    table_lines = []
    #
    del table_rows[0][2:5] # drop the first 3 years columns to make room for 3 added summary columns.
    table_lines.append(    f'''{" | ".join(table_rows[0]).strip()} 3YAVG | 5YAVG | 10YAVG |'''    )
    #
    del table_rows[1][2:5] # drop the first 3 years columns to make room for 3 added summary columns.
    table_lines.append(    f'''{" | ".join(table_rows[1]).strip()} ---:  | ---:  | ---:   |'''    )
    #
    for cols in table_rows[2:]:
        vals = []
        if cols[1].strip():
            # Not empty row (row name found in the first column).
            vals = cols[2:-1]
            for i in range(len(vals)):
                w = vals[i]
                mo = re.match(REGEXP_NUMBER, w)
                if mo:
                    snum = mo.group(2)
                    snum = snum.replace(',','') # Remove group separators, if any.
                    num = Decimal(snum)
                    vals[i] = num
                else:
                    pass # w is Not a number.
            if len(vals) == 10:
                # 10 numerical values are expected in each not empty table row. 
                y10avg = f'''{int(sum(vals) / Decimal(10)):,}'''
                y5avg = f'''{int(sum(vals[-5:]) / Decimal(5)):,}'''
                y3avg = f'''{int(sum(vals[-3:]) / Decimal(3)):,}'''
            else:
                raise "Dupa blada!"
        else:
            # Empty row.
            y10avg = ""
            y5avg = ""
            y3avg = ""

        ll = cols[2+3:-1] # drop the first 3 years columns to make room for 3 added summary columns.
        ll = cols[:2] + ll + [y3avg, y5avg, y10avg ] + cols[-1:]
        ll = [f' {x} ' for x in ll]

        table_lines.append(    f'''{"|".join(ll).lstrip()}'''    )
    return table_lines

def generateCpiAdjusted(txt):
    lines = txt.split("\n")
    head_rows, table_rows, tail_rows = getTableRows(lines)
    cpi_mul = getCpiMultipliers(table_rows)
    #
    table_lines_cpi_adjusted = generateCipAdjustedTableLines(table_rows, cpi_mul)
    #
    head_rows[0] += " (inflation adjusted)"
    head_rows[2] = head_rows[2].replace(" CAD **nominalnych**", f" CAD **y{getLastYear(table_rows)}**    ")
    head_rows[3] = "([see nominal version](NaszBudżet))    "
    head_rows.insert(3, "([see version with averages](NaszBudżet-cpi-avg))    ")
    ll = head_rows + table_lines_cpi_adjusted + tail_rows
    return "\n".join(ll)

def generateWithAverages(txt):
    lines = txt.split("\n")
    head_rows, table_rows, tail_rows = getTableRows(lines)
    #
    table_lines = generateTableLinesWithAverages(table_rows)
    #
    head_rows[0] = head_rows[0].replace("(inflation adjusted)", "(inflation adjusted, with averages)")
    head_rows[2] += "    " # Markdown 'linebreak'
    head_rows[3] = "([see inflation adjusted version](NaszBudżet-cpi))    "
    ll = head_rows + table_lines + tail_rows
    return "\n".join(ll)

def getListOfYears(dd, maxnum):
    # Get list of years for rendering:
    dcpi = dd["CPI"]
    yrs = list(dcpi)
    yrs.sort()
    if len(yrs) > maxnum:
        yrs = yrs[len(yrs) - maxnum:]
    return yrs

def processSupergroup(key, dd_data, yrs):
    # TODO: Refactor into a function:
    txt = ""
    ll = []
    for lista_grupy in dd_data[key]:
        lista_grupy = summarizeCategoriesInGroupByYears(lista_grupy, yrs)
        txt += emitGroup(lista_grupy)
        ll.append(lista_grupy)
    return [[key, summarizeGroups(ll)]], txt

def main():
    dd_data = readYaml(os.path.join(APPHOME, 'NaszBudżet.yaml'))

    # GitHub will not render wider table in our case .
    # (11 columns wih our data is the max that the GitHub styling will handle without clipping the rightmost part of the table)
    MAX_YRS = 10 

    yrs = getListOfYears(dd_data, MAX_YRS)

    wreg_total, txt_wreg = processSupergroup("Wydatki regularne", dd_data, yrs)

    wnreg_total, txt_wnreg = processSupergroup("Wydatki duże i nieregularne[^dniereg]", dd_data, yrs)

    wrazem = [["Wydatki razem", summarizeGroups([wreg_total, wnreg_total])]]

    txt = ""
    txt += emitDocHeader()
    txt += emitTableHeader(yrs, dd_data)
    txt += emitGroup(wrazem)
    txt += emitGroup(wreg_total)
    txt += txt_wreg
    txt += emitGroup(wnreg_total)
    txt += txt_wnreg
    txt += emitAnnotations(dd_data)
    txt += emitTimestamp()

    # print(txt)
    writeTextToFile(txt, os.path.join(APPHOME, 'NaszBudżet.md'))
    txt = generateCpiAdjusted(txt)
    writeTextToFile(txt, os.path.join(APPHOME, 'NaszBudżet-cpi.md'))
    writeTextToFile(generateWithAverages(txt), os.path.join(APPHOME, 'NaszBudżet-cpi-avg.md'))

if __name__ == "__main__":
    sys.exit(main())
