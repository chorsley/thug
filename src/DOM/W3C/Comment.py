#!/usr/bin/env python
from __future__ import with_statement

from DOMException import DOMException
from CharacterData import CharacterData


class Comment(CharacterData):
    @property
    def nodeName(self):
        return "#comment"

    @property
    def nodeType(self):
        return Node.COMMENT_NODE

    def getNodeValue(self):
        return self.data

    def setNodeValue(self, data):
        self.data = data

    nodeValue = property(getNodeValue, setNodeValue)

