
import logging
log = logging.getLogger("Thug")

def SetWksPictureInterface(self, val):
    self.__dict__['WksPictureInterface'] = val

    log.ThugLogging.add_behavior_warn('[MicrosoftWorks7 ActiveX] Overflow in WksPictureInterface property')

