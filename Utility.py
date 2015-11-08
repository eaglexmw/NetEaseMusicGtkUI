# coding=utf8

import hashlib
import os


def md5(src):
    m = hashlib.md5()
    m.update(src)
    return m.hexdigest()


def toast(str):
    os.system("dbus-send --type=method_call --dest=org.freedesktop.Notifications "
              "/org/freedesktop/Notifications org.freedesktop.Notifications.SystemNoteInfoprint string:'%s'" % str)
