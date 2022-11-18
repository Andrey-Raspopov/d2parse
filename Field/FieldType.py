import re


class FieldType:
    def __init__(self, name):
        itemCounts = {"MAX_ITEM_STOCKS": 8,
                      "MAX_ABILITY_DRAFT_ABILITIES": 48
                      }

        p = re.compile('([^\<\[\*]+)(\<\s(.*)\s\>)?(\*)?(\[(.*)\])?')
        searches = p.search(name)

        ss = searches.groups()

        self.base_type = ss[0]
        self.pointer = ss[3] == "*"
        self.generic_type = None
        self.count = 0

        if ss[2] != None:
            self.generic_type = FieldType(name=ss[2])

        if ss[5] in itemCounts:
            self.count = itemCounts[ss[5]]
        elif ss[5] != None:
            if int(ss[5]) > 0:
                self.count = int(ss[5])
            else:
                self.count = 1024
