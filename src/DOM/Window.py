#!/usr/bin/env python
#
# Window.py
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA  02111-1307  USA

import os
import sched
import time
import logging
import PyV8
import traceback
import hashlib
import pefile
import bs4 as BeautifulSoup
import W3C.w3c as w3c

from Personality import Personality
from Navigator import Navigator
from Location import Location
from Screen import Screen
from History import History
from ActiveX.ActiveX import _ActiveXObject
from AST.AST import AST
from Debugger import Shellcode, Global
from Java.java import java

sched = sched.scheduler(time.time, time.sleep)
log = logging.getLogger("Thug")

class Window(PyV8.JSClass):

    class Timer(object):
        def __init__(self, window, code, delay, repeat, lang = 'JavaScript'):
            self.window  = window
            self.code    = code
            self.delay   = float(delay) / 1000
            self.repeat  = repeat
            self.lang    = lang
            self.running = True

        def start(self):
            self.event = sched.enter(self.delay, 1, self.execute, ())
            try:
                sched.run()
            except:
                pass

        def stop(self):
            self.running = False
            if self.event in sched.queue:
                sched.cancel(self.event)

        def execute(self):
            if not self.running:
                return

            log.debug(str(self.code))
            self.code.__call__()
            if self.repeat:
                self.start()
        
    def __init__(self, url, dom_or_doc, navigator = None, personality = 'xpie61', name="", 
                 target='_blank', parent = None, opener = None, replace = False, screen = None, 
                 width = 800, height = 600, left = 0, top = 0, **kwds):

        self.url = url
        self.doc = w3c.getDOMImplementation(dom_or_doc, **kwds) if isinstance(dom_or_doc, BeautifulSoup.BeautifulSoup) else dom_or_doc
        
        self.doc.window        = self
        self.doc.contentWindow = self
         
        self._navigator = navigator if navigator else Navigator(personality, self)
        self._location  = Location(self)
        self._history   = History(self)
        self._history.update(url, replace)

        #self.doc.location = self._location
        self.doc.location = property(self.getLocation, self.setLocation)

        self._target = target
        self._parent = parent
        self._opener = opener
        self._screen = screen or Screen(width, height, 32)
        self._closed = False
        
        self._personality = personality
        self.__init_personality()

        self.name          = name
        self.defaultStatus = ""
        self.status        = ""
        self._left         = left
        self._top          = top
        self.innerWidth    = width
        self.innerHeight   = height
        self.outerWidth    = width
        self.outerHeight   = height
        self.timers        = []
        self.java          = java()

    def __getattr__(self, name):
        if name == 'constructor':
            return PyV8.JSClassConstructor(self.__class__)

        #if name == 'prototype':
        #    return PyV8.JSClassPrototype(self.__class__)

        prop = self.__dict__.setdefault('__properties__', {}).get(name, None)

        if prop and callable(prop[0]):
            return prop[0]()

        raise AttributeError(name)

    @property 
    def closed(self):
        return self._closed

    def close(self):
        self._closed = True

    @property
    def this(self):
        return self

    @property
    def window(self):
        return self

    @property
    def self(self):
        return self

    @property
    def top(self):
        return self

    @property
    def document(self):
        return self.doc

    def _findAll(self, tags):
        return self.doc.doc.find_all(tags, recursive = True)

    @property
    def frames(self):
        """an array of all the frames (including iframes) in the current window"""
        return w3c.HTMLCollection(self.doc, [self.doc.createHTMLElement(self.doc, f) for f in self._findAll(['frame', 'iframe'])])

    @property
    def length(self):
        """the number of frames (including iframes) in a window"""
        return len(self._findAll(['frame', 'iframe']))

    @property
    def history(self):
        """the History object for the window"""
        return self._history

    def getLocation(self):
        """the Location object for the window"""
        return self._location

    def setLocation(self, location):
        self._location.href = location

    location = property(getLocation, setLocation)

    @property
    def navigator(self):
        """the Navigator object for the window"""
        return self._navigator

    @property
    def opener(self):
        """a reference to the window that created the window"""
        return self._opener

    @property
    def pageXOffset(self):
        return 0

    @property
    def pageYOffset(self):
        return 0

    @property
    def parent(self):
        return self._parent

    @property
    def screen(self):
        return self._screen
        
    @property
    def screenLeft(self):
        return self._left

    @property
    def screenTop(self):
        return self._top

    @property
    def screenX(self):
        return self._left

    @property
    def screenY(self):
        return self._top

    def ActiveXObject(self, cls, type = 'name'):
        return _ActiveXObject(self, cls, type = 'name')

    # Window object methods
    #
    # escape        Encodes a string.
    # sizeToContent Sizes the window according to its content.
    # unescape      Unencodes a value that has been encoded in hexadecimal (e.g., a cookie).

    def alert(self, text):
        """
        Display an alert dialog with the specified text.
        Syntax

        window.alert(text) 

        Parameters

        text is a string of the text you want displayed in the alert dialog.
        """
        log.warning('[Window] Alert Text: %s' % (str(text), ))

    def back(self):
        """
        Returns the window to the previous item in the history.
        Syntax

        window.back() 

        Parameters

        None.
        """
        pass

    def blur(self):
        """
        Shifts focus away from the window.
        Syntax

        window.blur() 

        Parameters

        None.
        """
        pass

    def captureEvents(self, eventType):
        """
        Registers the window to capture all events of the specified type.
        Syntax

        window.captureEvents(Event.eventType) 

        Parameters

        eventType is a string
        """
        self.alert("[Captured Event] %s" % (eventType, ))

    def clearInterval(self, intervalID):
        """
        Clears a delay that's been set for a specific function.
        Syntax

        window.clearInterval(intervalID) 

        Parameters

        intervalID is the ID of the specific interval you want to clear.
        """
        self.timers[intervalID].stop()

    def clearTimeout(self, timeoutID):
        """
        Clears the delay set by window.setTimeout().
        Syntax

        window.clearTimeout(timeoutID) 

        Parameters

        timeoutID is the ID of the timeout you wish you clear.
        """
        self.timers[timeoutID].stop()
    
    def confirm(self, text):
        """
        Displays a dialog with a message that the user needs to respond to.
        Syntax

        result = window.confirm(text) 

        Parameters

        text is a string.

        result is a boolean value indicating whether OK or Cancel was selected.
        """
        return True

    def dump(self, text):
        """
        Prints messages to the console.
        Syntax

        window.dump(text) 

        Parameters

        text is a string.
        """
        self.alert(text)

    def focus(self):
        """
        Sets focus on the window.
        Syntax

        window.focus() 

        Parameters

        None.
        """
        pass
    
    def forward(self):
        """
        Moves the window one document forward in the history.
        Syntax

        window.forward() 

        Parameters

        None.
        """
        self._history.forward()

    def GetAttention(self):
        """
        Flashes the application icon to get the user's attention.
        Syntax

        window.GetAttention() 

        Parameters

        None.
        """
        pass

    def getSelection(self):
        """
        Returns the selection (generally text).
        Syntax

        selection = window.getSelection() 

        Parameters

        selection is a selection object.
        """
        return None

    def home(self):
        """
        Returns the window to the home page.
        Syntax

        window.home() 

        Parameters

        None.
        """
        self.open()

    def moveBy(self, deltaX, deltaY):
        """
        Moves the current window by a specified amount.
        Syntax

        window.moveBy(deltaX, deltaY) 

        Parameters

        deltaX is the amount of pixels to move the window horizontally.
        deltaY is the amount of pixels to move the window vertically.
        """
        pass

    def moveTo(self, x, y):
        """
        Moves the window to the specified coordinates.
        Syntax

        window.moveTo(x, y) 

        Parameters

        x is the horizontal coordinate to be moved to.
        y is the vertical coordinate to be moved to.
        """
        pass
    
    def prompt(self, text):
        """
        Returns the text entered by the user in a prompt dialog. 
        """
        return text

    def releaseEvents(self, eventType):
        """
        Releases the window from trapping events of a specific type.
        Syntax

        window.releaseEvents(Event.eventType) 

        Parameters

        eventType is a string
        """
        self.alert("[Released Event] %s" % (eventType, ))

    def resizeBy(self, xDelta, yDelta):
        """
        Resizes the current window by a certain amount.
        Syntax

        window.resizeBy(xDelta, yDelta) 

        Parameters

        xDelta is the number of pixels to grow the window horizontally.
        yDelta is the number of pixels to grow the window vertically.
        """
        pass

    def resizeTo(self, iWidth, iHeight):
        """
        Dynamically resizes window.
        Syntax

        window.resizeTo(iWidth, iHeight) 

        Parameters

        iWidth is an integer representing the new width in pixels.
        iHeight is an integer value representing the new height in pixels.
        """
        pass

    def scroll(self, x, y):
        """
        Scrolls the window to a particular place in the document.
        Syntax

        window.scroll(x-coord, y-coord) 

        Parameters

        x-coord is the pixel along the horizontal axis of the document that
        you want displayed in the upper left.
        y-coord is the pixel along the vertical axis of the document that you
        want displayed in the upper left.
        """
        pass

    def scrollBy(self, xDelta, yDelta):
        """
        Scrolls the document in the window by the given amount.
        Syntax

        window.scrollBy(xDelta, yDelta) 

        Parameters

        xDelta is the amount of pixels to scroll horizontally.

        yDelta is the amount of pixels to scroll vertically.
        """
        pass
    
    def scrollByLines(self, lines):
        """
        Scrolls the document by the given number of lines.
        Syntax

        window.scrollByLines(lines) 

        Parameters

        lines is the number of lines.
        """
        pass

    def scrollByPages(self, pages):
        """
        Scrolls the current document by the specified number of pages.
        Syntax

        window.scrollByPages(pages) 

        Parameters

        pages is the number of pages to scroll.
        """
        pass

    def scrollTo(self, x, y):
        """
        Scrolls to a particular set of coordinates in the document.
        Syntax

        window.scrollTo(x-coord, y-coord) 

        Parameters

        x-coord is the pixel along the horizontal axis of the document that you
        want displayed in the upper left.

        y-coord is the pixel along the vertical axis of the document that you
        want displayed in the upper left.
        """
        pass

    def setCursor(self, s):
        pass

    def setInterval(self, f, delay, lang = 'JavaScript'):
        """
        Set a delay for a specific function.
        Syntax

        ID = window.setInterval("funcName", delay)

        Parameters

        funcName is the name of the function for which you want to set a
        delay.

        delay is the number of milliseconds (thousandths of a second)
        that the function should be delayed.

        ID is the interval ID.
        """
        timer = Window.Timer(self, f, delay, True, lang)
        self.timers.append(timer)
        timer.start()

        return len(self.timers) - 1 

    def setTimeout(self, f, delay, lang = 'JavaScript'):
        """
        Sets a delay for executing a function.
        Syntax

        ID = window.setTimeout("funcName", delay) 

        Parameters

        funcName is the name of the function for which you want to set a
        delay.

        delay is the number of milliseconds (thousandths of a second)
        that the function should be delayed.

        ID is the interval ID.
        """
        timer = Window.Timer(self, f, delay, False, lang)
        self.timers.append(timer)
        timer.start()

        return len(self.timers) - 1

    def stop(self):
        """
        This method stops window loading.
        Syntax

        window.stop() 

        Parameters

        None.
        """
        pass

    # Windows Script Host Run method documentation at
    # http://msdn.microsoft.com/en-us/library/d5fk67ky(v=vs.85).aspx
    def _Run(self, strCommand, intWindowStyle = 0, bWaitOnReturn = False):
        log.warning("[Windows Script Host Run] Command: \n%s\n", strCommand)
        if not 'http' in strCommand:
            return

        self._doRun(strCommand, 1)

    def _doRun(self, p, stage):
        if not isinstance(p, str):
            return

        try:
            pe = pefile.PE(data = p, fast_load = True)
            return
        except:
            pass

        log.ThugLogging.add_code_snippet(p, 'VBScript', 'Contained_Inside')
        log.warning("[Windows Script Host Run - Stage %d] Code:\n%s" % (stage, p, ))

        while True:
            try:
                index = p.index('"http')
            except ValueError:
                break

            p = p[index + 1:]
            s = p.split('"')
            if len(s) < 2:
                break

            url = s[0]
            log.warning("[Windows Script Host Run - Stage %d] Downloading from URL %s" % (stage, url, ))

            try:
                response, content = self._navigator.fetch(url)
            except:
                continue

            if response.status == 404:
                continue

            md5 = hashlib.md5()
            md5.update(content)
            log.warning("[Windows Script Host Run - Stage %d] Saving file %s" % (stage, md5.hexdigest()))
            p = '"'.join(s[1:])
            
            self._doRun(content, stage + 1)
                
    def _attachEvent(self, sEvent, fpNotify):
        log.debug("[attachEvent] %s %s" % (sEvent, fpNotify, ))
        fpNotify.__call__()

    def _detachEvent(self, sEvent, fpNotify):
        log.debug("[detachEvent] %s %s" % (sEvent, fpNotify, ))

    def _addEventListener(self, type, listener, useCapture = False):
        log.debug("[addEventListener] %s %s %s" % (type, listener, useCapture, ))

    def _removeEventListener(self, type, listener, useCapture = False):
        log.debug("[removeEventListener] %s %s %s" % (type, listener, useCapture, ))

    def _CollectGarbage(self):
        pass

    def __init_personality(self):
        if self._personality.startswith(('xpie', 'w2kie')):
            self.attachEvent    = self._attachEvent
            self.detachEvent    = self._detachEvent
            self.Run            = self._Run
            self.CollectGarbage = self._CollectGarbage

        if self._personality.startswith('firefox'):
            self.addEventListener    = self._addEventListener
            self.removeEventListener = self._removeEventListener

    def eval(self, script):
        return self.evalScript(script)

    @property
    def context(self):
        if not hasattr(self, '_context'):
            self._context = PyV8.JSContext(self)
            with self._context as ctxt:
                thug_js = os.path.join(os.path.dirname(os.path.abspath(__file__)), "thug.js")
                ctxt.eval(open(thug_js, 'r').read())

        return self._context

    def evalScript(self, script, tag = None):
        result = 0
        
        if tag:
            self.doc.current = tag
        else:
            try:
                body = self.doc.body
            except:
                # This code is for when you are desperate :)
                body = self.doc.getElementsByTagName('body')[0]

            if body:
                self.doc.current = body.tag.contents[-1]
            else:
                self.doc.current = self.doc.doc.contents[-1]

        with self.context as ctxt:
            try:
                ast = AST(script)
            except:
                log.debug(traceback.format_exc())
                return result

            if self._personality.startswith(('xpie', 'w2kie')):
                script = script.replace('@cc_on!@', '*/!/*')

            shellcode = Shellcode.Shellcode(ctxt, ast, script)
            result    = shellcode.run()

        return result

    def fireOnloadEvents(self):
        #for tag in self._findAll('script'):
        #   self.evalScript(tag.string, tag = tag)
        for tag in self._findAll('object'):
            classid = tag.get('classid', None)
            id      = tag.get('id', None)
            if not classid or not id:
                continue

            setattr(self, id, _ActiveXObject(self, classid, 'id'))

        index = 0
        tags  = self._findAll('script')
        while index < len(self._findAll('script')):
            tag = self._findAll('script')[index]
            if not tag.string:
                src = tag.get('src', None)
                if src:
                    try:
                        response, js = self._navigator.fetch(src)
                    except:
                        continue

                    if response.status == 404:
                        continue

                    tag.setString(js)
            try:
                self.evalScript(tag.string, tag = tag)
            except:
                log.debug(traceback.format_exc())

            index += 1

        body = self.doc.body
        if body and body.tag.has_attr('onload'):
            self.evalScript(body.tag['onload'], tag = body.tag.contents[-1])

        if hasattr(self, 'onload'):
            self.evalScript(self.onload)

    def Image(self, width = 800, height = 600):
        return self.doc.createElement('img')

    def XMLHttpRequest(self):
        return _ActiveXObject(self, 'microsoft.xmlhttp')

    def open(self, url = None, name = '_blank', specs = '', replace = False):
        if url:
            try:
                response, html = self._navigator.fetch(url)
            except:
                return None

            if response.status == 404:
                return None

            if 'content-type' in response and response['content-type'] in ('application/pdf', ):
                return None

            # Log response here
            kwds = { 'referer' : self.url }
            if 'set-cookie' in response:
                kwds['cookie'] = response['set-cookie']
            if 'last-modified' in response:
                kwds['lastModified'] = response['last-modified']
        else:
            url  = 'about:blank'
            html = ''
            kwds = {}
       
        dom = BeautifulSoup.BeautifulSoup(html, "html5lib")
        
        for spec in specs.split(','):
            spec = [s.strip() for s in spec.split('=')]

            if len(spec) == 2:
                if spec[0] in ['width', 'height', 'left', 'top']:
                    kwds[spec[0]] = int(spec[1])

            if name in ['_blank', '_parent', '_self', '_top']:
                kwds['target'] = name
                name = ''
            else:
                kwds['target'] = '_blank'

        return Window(url, dom, navigator = None, personality = self._personality, 
                        name = name, parent = self, opener = self, replace = replace, **kwds)


import unittest

TEST_URL = 'http://localhost:8080/path?query=key#frag'
TEST_HTML = """
<html>
<head>
    <title></title>
</head>
<body onload='load()'>
    <frame src="#"/>
    <iframe src="#"/>
    <script>

    function load()
    {
        window.innerWidth = 1;
    }

    document.write("<p id='hello'>world</p>");
    </script>
</body>
</html>
"""

TEST_SETINTERVAL = """
<html>
<head>
    <title></title>
</head>
<body>
    <script>
    var i = 0;
    var intervalID = 0;

    function f()
    {
        intervalID = setInterval("test();", 10);
    }

    function test()
    {
        i += 1;
        if (i > 3) {
            var timeoutStr = "<p id='hello'>" + i +"</p>";
            document.write(timeoutStr);
            clearInterval(intervalID);
        }
    }

    f();
    </script>
</body>
</html>
"""

TEST_SETTIMEOUT = """
<html>
<head>
    <title></title>
</head>
<body>
    <script>
    var i = 0;
    var timeoutID = 0;

    function f()
    {
        timeoutID = setTimeout("test();", 100);
    }

    function test()
    {
        i += 1;
        var timeoutStr = "<p id='hello'>" + i +"</p>";
        document.write(timeoutStr);
    }

    f();
    </script>
</body>
</html>
"""


class WindowTest(unittest.TestCase):
    def setUp(self):
        self.doc = w3c.parseString(TEST_HTML)
        self.win = Window(TEST_URL, self.doc)

    def testWindow(self):
        self.assertEquals(self.doc, self.win.document)
        self.assertEquals(self.win, self.win.window)
        self.assertEquals(self.win, self.win.self)

        self.assertFalse(self.win.closed)
        self.win.close()
        self.assert_(self.win.closed)

        self.assertEquals(2, self.win.frames.length)
        self.assertEquals(2, self.win.length)

        self.assertEquals(1, self.win.history.length)

        loc = self.win.location

        self.assert_(loc)
        self.assertEquals("frag", loc.hash)
        self.assertEquals("localhost:8080", loc.host)
        self.assertEquals("localhost", loc.hostname)
        self.assertEquals(TEST_URL, loc.href)
        self.assertEquals("/path", loc.pathname)
        self.assertEquals(8080, loc.port)
        self.assertEquals("http", loc.protocol)
        self.assertEquals("query=key", loc.search)

    def testOpen(self):
        url = 'http://www.google.com'
        win = self.win.open(url, specs="width=640, height=480")
        self.assertEquals(url, win.url)

        self.assert_(win.document)
        self.assertEquals(url, win.document.URL)
        self.assertEquals('www.google.com', win.document.domain)
        self.assertEquals(640, win.innerWidth)
        self.assertEquals(480, win.innerHeight)

    def testScript(self):
        self.win.fireOnloadEvents()

        tag = self.doc.getElementById('hello')
        self.assertEquals(u'P', tag.nodeName)
        self.assertEquals(1, self.win.innerWidth)

    def testSetInterval(self):
        doc = w3c.parseString(TEST_SETINTERVAL)
        win = Window(TEST_URL, doc)
        
        win.fireOnloadEvents()
        tag = doc.getElementById('hello')
        self.assertEquals(4, int(tag.firstChild.data))

    def testSetTimeout(self):
        doc = w3c.parseString(TEST_SETTIMEOUT)
        win = Window(TEST_URL, doc)

        win.fireOnloadEvents()
        tag = doc.getElementById('hello')
        self.assertEquals(1, int(tag.firstChild.data))


if __name__ == '__main__':
    unittest.main()
