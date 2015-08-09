#!/usr/bin/env python

CMD_GROUPS = [['p', "'", '!', '.', '0', '3'],
              ['b', 'c', 'e', 'f', 'y', '2'],
              ['a', 'g', 'h', 'i', 'j', '4'],
              ['l', 'm', 'n', 'o', ' ', '5'],
              ['d', 'q', 'r', 'v', 'z', '1'],
              ['k', 's', 't', 'u', 'w', 'x'],
]

SUBST = {}

for cmds in CMD_GROUPS:
    for cmd in cmds:
        SUBST[cmd] = set(cmds)

def search(cmdstr, phrase):
    pl = len(phrase)
    if pl > len(cmdstr):
        return None
    for ci in range(len(cmdstr) - pl + 1):
        for pi in range(pl):
            if phrase[pi] in SUBST[cmdstr[ci + pi]]:
                if pi + 1 == pl:
                    return ci
            else:
                break
    return None

def subst(cmdstr, phrase):
    p = phrase.lower()
    pl = len(p)
    s = []
    ci = search(cmdstr, p)
    while ci is not None:
        s.append(cmdstr[:ci])
        s.append(p)
        cmdstr = cmdstr[ci+pl:]
        ci = search(cmdstr, p)
    s.append(cmdstr)
    return ''.join(s)
