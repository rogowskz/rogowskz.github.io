#!/usr/bin/python3
# coding: utf-8

'''
Publishing generated .md pages:

    $ cd /media/veracrypt1/zr/timeline/md/rogowskz.github.io

    $ python3 NaszBudżet.py > NaszBudżet.md
    $ git add NaszBudżet.md
    $ git commit -m "Updated NaszBudżet.md"

    $  echo "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" | gh auth login --with-token
    $ git push https://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@github.com/rogowskz/rogowskz.github.io.git


TODO: Update 'gh' cli client:
    A new release of gh is available: 2.14.2 → 2.38.0
    https://github.com/cli/cli/releases/tag/v2.38.0

'''

import sys
import os
import yaml

cwd = os.getcwd()
APPHOME, _ = os.path.split(sys.argv[0])
APPHOME = os.path.abspath(APPHOME)

LBRK = "    "

def readYaml(fpath):
    with open(fpath) as f:
        txt = f.read()
    return yaml.load(txt, Loader=yaml.FullLoader)

def emitDocHeader(dd):
    txt = ""
    txt += dd["Text"]["Para_nom_1"] + "\n"
    txt += "\n"
    txt += dd["Text"]["Para_nom_2"] + LBRK + "\n"
    txt += dd["Text"]["Para_nom_3"] + "\n"
    return txt

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
    txt += f'''| {dd["Text"]["Para_cpi"]} | {' | '.join([str(x) for x in list(dcpi.values())])} |\n'''

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

def main():
    dd = readYaml(os.path.join(APPHOME, 'NaszBudżet.yaml'))

    # TODO: Refactor into a function:
    txt_wreg = ""
    ll = []
    for lista_grupy in dd["Wydatki regularne"]: # TODO: Wziąc tekst z yaml
        lista_grupy = summarizeCategoriesInGroupByYears(lista_grupy)
        txt_wreg += emitGroup(lista_grupy)
        ll.append(lista_grupy)
    wreg_total = [["Wydatki regularne", summarizeGroups(ll)]] # TODO: Wziąc tekst z yaml

    # TODO: Refactor into a function:
    txt_wnreg = ""
    ll = []
    for lista_grupy in dd["Wydatki duże i nieregularne[^dniereg]"]: # TODO: Wziąc tekst z yaml
        lista_grupy = summarizeCategoriesInGroupByYears(lista_grupy)
        txt_wnreg += emitGroup(lista_grupy)
        ll.append(lista_grupy)
    wnreg_total = [["Wydatki duże i nieregularne[^dniereg]", summarizeGroups(ll)]] # TODO: Wziąc tekst z yaml

    wrazem = [["Wydatki razem", summarizeGroups([wreg_total, wnreg_total])]] # TODO: Wziąc tekst z yaml

    txt = ""
    txt += emitDocHeader(dd)
    txt += emitTableHeader(dd)
    txt += emitGroup(wrazem)
    txt += emitGroup(wreg_total)
    txt += txt_wreg
    txt += emitGroup(wnreg_total)
    txt += txt_wnreg
    txt += emitAnnotations(dd)

    print(txt)

if __name__ == "__main__":
    sys.exit(main())
