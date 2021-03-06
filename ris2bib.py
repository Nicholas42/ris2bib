#!/usr/bin/env python3
# encoding: utf-8

"""
ris2bib.py

Copyright (C) 2011, 2012 Daniel O'Hanlon	

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
Takes .ris files as first argument in the form 'name.ris' and outputs files
in the bibtex format in the form 'name.bib'. Currently assuming Nature article
format for ease of programming.

Uses .ris tag information from: http://en.wikipedia.org/wiki/RIS_(file_format)

Usage is ris2bib.py [FILE] [-v]

D.P O'Hanlon
Sun 13 May 2012 14:10:52 BST

"""

import sys
import os
import re
import argparse
from pathlib import Path

def main(argv):
    if not argv.outfile:
        argv.outfile = argv.inputs[0].with_suffix(".bib")

    data = []
    for i in argv.inputs:
        data.append(r2b_read(i, argv))

    r2b_write(data, argv.outfile)

def get_value_ris(line):
    return line.partition("-")[2].strip()

def r2b_read(ris, args):
    """
    Reads in a .ris file and returns a .bib format 'entries' dictionary with the appropriate information.
    """

    entries = dict()
    entries['authors']=list() # Allows for multiple authors
    unparsed_lines = 0
    
    with open(ris) as f:
        for line in f:
            val = get_value_ris(line)
            if re.match("PY",line):
                    entries['year'] = val
            elif re.match("AU",line):
                    entries['authors'].append(val) # minus one to remove newline
            elif re.match("VL",line):
                    entries['volume'] = val
            elif re.match("TI",line) or re.match("T1",line):
                    entries['title'] = val
            elif re.match("JA",line) or re.match("JO",line):
                    entries['journal'] = val
            elif re.match("IS",line):
                    entries['number'] = val
            elif re.match("SP",line):
                    entries['startpage'] = val
            elif re.match("EP",line):
                    entries['endpage'] = val
            elif re.match("UR",line):
                    entries['url'] = val
            elif re.match("DO", line):
                    entries["doi"] = val
            elif re.match("ID", line):
                    entries["id"] = val
            elif re.match("SN", line):
                    entries["issn"] = val
            elif re.match("DA", line):
                    entries["year"], entries["month"], entries["day"] = val.split("/") 
            else:
                unparsed_lines += 1
                if args.verbose:
                    print ('Unparsed line: ' + line[:-1])

    if unparsed_lines and not args.quiet:
        print('%s unparsed lines in file %s.'%(unparsed_lines, ris))
    return entries
    	
def r2b_write(data, bib_filename):
    """
    Writes the .bib formatted dictionary to file using .bib file syntax.
    """

    with open(bib_filename,'a') as bib: # strip and replace extension
        for entries in data:
            if "startpage" in entries:
                entries["pages"] = entries.pop("startpage") + "-" + entries.pop("endpage")

            ident = entries.get("id", entries['authors'][0][:entries['authors'][0].index(',')] + (entries['year'] if ('year' in entries) else ''))

            bib.write('@ARTICLE{' + ident + ",") 
            bib.write('\n\tauthor=\t{'+" and ".join(entries.pop('authors')))
            bib.write("},")
            for k,v in entries.items():
                bib.write('\n\t%s=\t{%s},'%(k,v))
        bib.write("\n}\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Show each unused line.", action="store_true")
    parser.add_argument("-q", "--quiet", help="Do not report number of unused lines.", action="store_true")
    parser.add_argument("-o", "--outfile", help="File to write to. Defaults to first input with .bib extension.", type=Path)
    parser.add_argument("-w", "--overwrite", help="Overwrite output instead of appending. Use with care.", type=str)
    parser.add_argument("inputs", nargs="+", type=Path)

    argv = parser.parse_args()
    main(argv)	
