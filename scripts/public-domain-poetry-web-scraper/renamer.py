# -*- coding: utf-8 -*-
from glob import glob
import re
import os
from pipes import quote

for txtfile in glob("poems/*"):
    txtfile = txtfile
    if re.search(u'\ufffd',txtfile.decode("utf-8")):
        newfile = txtfile.decode("utf-8").replace(u'\ufffd', u"")
        cmd = u"mv %s %s" % (quote(txtfile.decode("utf-8")), quote(newfile))
        os.system(cmd.encode("utf-8"))
        print newfile
