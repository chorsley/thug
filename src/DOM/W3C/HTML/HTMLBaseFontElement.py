#!/usr/bin/env python
from __future__ import with_statement

from HTMLElement import HTMLElement
from attr_property import attr_property

class HTMLBaseFontElement(HTMLElement):
    def __init__(self, doc, tag):
        HTMLElement.__init__(self, doc, tag)

    color           = attr_property("color")
    face            = attr_property("face")
    size            = attr_property("size", long)
