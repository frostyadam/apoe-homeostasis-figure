#!/usr/bin/env python
"""Embed figdata.json into page_template.html -> apoe_endocytosis_atlas.html (self-contained)."""
import json, os
H=os.path.dirname(os.path.abspath(__file__))
data=json.dumps(json.load(open(f"{H}/figdata.json")),separators=(",",":")).replace("</","<\\/")
page=open(f"{H}/page_template.html").read()
assert page.count("/*__DATA__*/null")==1
open(f"{H}/apoe_endocytosis_atlas.html","w").write(page.replace("/*__DATA__*/null",data))
print(f"wrote apoe_endocytosis_atlas.html ({os.path.getsize(f'{H}/apoe_endocytosis_atlas.html')/1024:.0f} KB)")
