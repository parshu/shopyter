import sys, os

def toutf8(any_string, encoding='utf-8'):
    if encoding == None:
        encoding = 'utf-8'
    if isinstance(any_string, basestring):
        if not isinstance(any_string, unicode):
            return unicode(any_string, encoding, errors='ignore').encode('utf-8')
        else:
            return any_string.encode('utf-8')
    return any_string
