#!/usr/bin/env python3
"""Render Q/K/V color proofs using Machado (2009) simulations via colorspacious.

The distance floor is a project regression threshold, not an accessibility
certification. Letter labels and line styles remain necessary redundancies.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from colorspacious import cspace_convert
from generate_chapter_navigation import argument

ROOT=Path(__file__).resolve().parents[1]
MODES=('normal','protanomaly','deuteranomaly','tritanomaly')


def simulate(rgb,mode):
    if mode=='normal':return rgb
    return np.clip(cspace_convert(rgb,{'name':'sRGB1+CVD','cvd_type':mode,'severity':100},'sRGB1'),0,1)


def palette_proof(output):
    source=(ROOT/'book/main.tex').read_text()
    colors=[re.search(r'\\definecolor\{'+name+r'\}\{HTML\}\{([A-Fa-f0-9]{6})\}',source)[1] for name in ('blue','teal','orange')]
    rgb=np.array([[int(c[i:i+2],16)/255 for i in (0,2,4)] for c in colors])
    font=ImageFont.truetype('DejaVuSans.ttf',22)
    img=Image.new('RGB',(850,390),'white');draw=ImageDraw.Draw(img)
    distances={}
    for row,mode in enumerate(MODES):
        sim=simulate(rgb,mode);ucs=cspace_convert(sim,'sRGB1','CAM02-UCS')
        distances[mode]={a+b:float(np.linalg.norm(ucs[i]-ucs[j])) for i,j,a,b in [(0,1,'Q','K'),(0,2,'Q','V'),(1,2,'K','V')]}
        if min(distances[mode].values())<10:
            raise SystemExit(f'Q/K/V palette regressed below project simulation distance floor: {mode}: {distances[mode]}')
        draw.text((12,row*95+25),mode,fill='black',font=font)
        for col,name in enumerate('QKV'):
            left=230+col*190;top=row*95+10
            draw.rectangle((left,top,left+145,top+65),fill=tuple(np.rint(sim[col]*255).astype(int)))
            draw.text((left+10,top+15),name,fill='white',font=font)
    img.save(output/'qkv-palette.png')
    return {'colors':dict(zip('QKV',colors)), 'method':'colorspacious 1.1.2; Machado et al. 2009, severity 100; clipped sRGB then CAM02-UCS distances',
            'distance_floor':10,'distances':distances,
            'limitation':'Project regression check; simulation does not replace reader testing. Labels and line styles required.'}


def pdf_proofs(pdf,aux,output):
    pages={}
    for line in aux.read_text().splitlines():
        match=re.match(r'\\newlabel\{([^}]+)\}\{',line)
        if not match:continue
        body,_=argument(line,match.end()-1);_,end=argument(body,0);page,_=argument(body,end)
        if page.isdigit():pages[match[1]]=int(page)
    selected={}
    for label in ('fig:why-qkv','fig:attention-weights','fig:mha-gqa-mqa'):
        page=pages[label];selected[label]=page;prefix=output/(label.replace(':','-')+'-original')
        subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-scale-to','900','-png','-singlefile',str(pdf),str(prefix)],check=True,capture_output=True)
        original=Image.open(str(prefix)+'.png').convert('RGB');arr=np.asarray(original,dtype=float)/255
        # A contact sheet compares the same page and labels in all four modes.
        sheet=Image.new('RGB',(original.width*4,original.height+24),'white');draw=ImageDraw.Draw(sheet)
        for i,mode in enumerate(MODES):
            proof=Image.fromarray(np.rint(simulate(arr,mode)*255).astype('uint8'))
            sheet.paste(proof,(i*original.width,24));draw.text((i*original.width+5,4),mode,fill='black')
        sheet.save(output/(label.replace(':','-')+'-cvd.png'))
    return selected


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pdf',type=Path);p.add_argument('--aux',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True);summary=palette_proof(a.output)
    if a.pdf:
        if not a.aux:p.error('--pdf requires --aux')
        summary['selected_pdf_pages']=pdf_proofs(a.pdf,a.aux,a.output)
        summary['pdf_sha256']=hashlib.sha256(a.pdf.read_bytes()).hexdigest()
    (a.output/'color-role-audit.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('Color proof generated: normal plus three severity-100 simulations; Q/K/V regression distances >= 10; retain label/line redundancy')


if __name__=='__main__':main()
