#!/usr/bin/env python3
"""src/app.html + data.json + world.json + fonts -> build/index.html (self-contained).
Placeholders in app.html: /*__DATA__*/ /*__WORLD__*/ /*__FONTS__*/
Fonts come from src/fonts.json: [{"family":"X","weight":400,"style":"normal","file":"geo/node_modules/@fontsource/x/files/x-latin-400-normal.woff2"}]"""
import json,base64,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
h=open(R+'src/app.html',encoding='utf8').read()
d=open(R+'src/data.json',encoding='utf8').read(); w=open(R+'src/world.json').read()
css=''
if os.path.exists(R+'src/fonts.json'):
  for f in json.load(open(R+'src/fonts.json')):
    b=base64.b64encode(open(R+f['file'],'rb').read()).decode()
    css+="@font-face{font-family:'%s';font-weight:%s;font-style:%s;font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2')}\n"%(f['family'],f['weight'],f.get('style','normal'),b)
h=h.replace('/*__FONTS__*/',css).replace('/*__DATA__*/',d).replace('/*__WORLD__*/',w)
open(R+'build/index.html','w',encoding='utf8').write(h)
# Standalone page for regular web hosting (Vercel): adds the doctype and viewport
page='<!doctype html>\n<html lang="en">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'+h
open(R+'index.html','w',encoding='utf8').write(page)
print('build/index.html and index.html',os.path.getsize(R+'index.html')//1024,'KB')
