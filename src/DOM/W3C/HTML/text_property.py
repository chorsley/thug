#!/usr/bin/env python
from __future__ import with_statement

import bs4 as BeautifulSoup

def text_property(readonly = False):
    def getter(self):
        return str(self.tag.string)
    
    def setter(self, text):
        if self.tag.string:
            self.tag.contents[0] = BeautifulSoup.NavigableString(text)
        else:
            self.tag.append(text)
                    
        self.tag.string = self.tag.contents[0]
        
    return property(getter) if readonly else property(getter, setter)

