import io
import os
import sys

from pytigon_lib.schindent.html2ihtml import Html2IhtmlParser

cwd = os.getcwd()
file_name = sys.argv[-1]
if file_name.endswith(".ihtml"):
    if file_name.startswith("//") or ":" in file_name:
        file_name2 = file_name
    else:
        file_name2 = os.path.join(cwd, file_name)
    file_name3 = file_name2.replace(".ihtml", ".html")
    with open(file_name3, "rt", encoding="utf-8") as f:
        buf = f.read()
        print(buf)
        out = io.StringIO()
        parser = Html2IhtmlParser(out)
        parser.feed(buf)
        parser.close()
        output = out.getvalue()
        with open(file_name2, "wt", encoding="utf-8") as f2:
            f2.write(output)
