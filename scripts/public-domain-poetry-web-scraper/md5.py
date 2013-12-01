import hashlib
from glob import glob
from codecs import open
poems_path = "poems/"

def md5_check():
    md5s = []
    for txtfile in glob(poems_path + "*.txt" ):
        md5 = hashlib.md5(open(txtfile, "r", "utf-8").read().encode("utf-8")).hexdigest()
        if md5 in md5s:
            print txtfile
        else:
            md5s.append(md5)

md5_check()


