#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2017 emijrp <emijrp@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import sys
import time

import pwb
import pywikibot
from wikidatafun import *

def main():
    targetlang = 'es'
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    
    i = 0
    if len(sys.argv) > 1:
        i = int(sys.argv[1])
    
    skip = ''
    for n in range(i*1000000, (i+1)*1000000):
        q = 'Q%s' % (n)
        print('==', q, '==')
        if skip:
            if skip != q:
                print('Skiping until', skip)
                continue
            else:
                skip = ''
        
        item = pywikibot.ItemPage(repo, q)
        try: #to detect Redirect because .isRedirectPage fails
            item.get()
        except:
            print('Error while .get()')
            continue
        aliases = item.aliases
        labels = item.labels
        if not targetlang in labels:
            print('Not label %s found' % (targetlang))
            continue
        
        names = [labels[targetlang]]
        if targetlang in aliases:
            [names.append(x) for x in aliases[targetlang]]
        
        plainnames = []
        for name in names:
            if not re.search(r'(?i)[^a-záéíóú\.\- ]', name):
                #avoid producing names like Carlos I de España->Espana
                plainnames.append(removeAccents(name))
            else:
                print('Filtering: %s' % (name.encode('utf-8')))
        
        missingnames = []
        for plainname in plainnames:
            if not plainname.lower() in [x.lower() for x in names] and \
               not plainname.lower() in [y.lower() for y in missingnames]:
                if targetlang in aliases.keys():
                    aliases[targetlang].append(plainname)
                else:
                    aliases[targetlang] = [plainname]
                missingnames.append(plainname)
        
        if missingnames:
            data = { 'aliases': aliases }
            missingnames.sort()
            summary = "BOT - Adding %s aliases (%s): %s" % (len(missingnames), targetlang, ', '.join(missingnames))
            print(summary.encode('utf-8'))
            try:
                item.editEntity(data, summary=summary)
            except:
                print('Error while saving')
                continue
    
    print("Finished successfully")
        
if __name__ == "__main__":
    main()
