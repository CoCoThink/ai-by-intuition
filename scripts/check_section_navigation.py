#!/usr/bin/env python3
"""Check section/page ownership and keep semantic diagrams with their captions.

A figure and a subsection can both be valid destinations while lying on different
pages. The old undefined-reference gate therefore could not catch this regression.
"""
from __future__ import annotations
import argparse
from html import unescape
from pathlib import Path
import re
import subprocess
from check_chapter_crossrefs import uncomment
from generate_chapter_navigation import argument

ROOT=Path(__file__).resolve().parents[1]


def section_targets(sources):
    result=set()
    for body in sources.values():
        for match in re.finditer(r'\\subsection\{', body):
            _,end=argument(body,match.end()-1)
            remainder=body[end:]
            prefix=re.match(r'(?:\s|\\phantomsection|\\label\{[^}]+\})*',remainder)[0]
            result.update(re.findall(r'\\label\{([^}]+)\}',prefix))
    return result


def source_errors(body, targets):
    errors=[]
    for target in re.findall(r'\\sectionentry\{([^}]+)\}',body):
        if '#' not in target and target not in targets:
            errors.append(f'Section entry points to a non-section: {target}')
    # Regression shape: referring to an elective but printing a figure's page.
    for match in re.finditer(r'(?:节|选读)[^。\n]{0,45}?\\pageref\*?\{([^}]+)\}',body):
        if match[1].startswith('fig:'):
            errors.append('Section/elective page reference points to a figure instead of its heading')
    if re.search(r'第[\s~]*\d+[\s~]*页',body):
        errors.append('Literal page number: use an automatic page reference')
    return errors


def figure_page_sets(reader):
    """Resolve actual MCR page associations, including inherited /Pg entries."""
    page_numbers={page.indirect_reference.idnum:i+1 for i,page in enumerate(reader.pages)}
    def pages(obj):
        if hasattr(obj,'get_object'):obj=obj.get_object()
        if isinstance(obj,list):return set().union(*(pages(child) for child in obj))
        if not isinstance(obj,dict):return set()
        found=set()
        if '/Pg' in obj:
            ref=obj.raw_get('/Pg')
            if hasattr(ref,'idnum'):found.add(page_numbers[ref.idnum])
        return found | pages(obj.get('/K',[]))
    def walk(obj):
        if hasattr(obj,'get_object'):obj=obj.get_object()
        if isinstance(obj,list):
            for child in obj:yield from walk(child)
        elif isinstance(obj,dict):
            if obj.get('/S')=='/Figure':yield (str(obj.get('/Alt','')), pages(obj))
            yield from walk(obj.get('/K',[]))
    return list(walk(reader.trailer['/Root']['/StructTreeRoot']))


def caption_errors(figures):
    return [f'Figure/caption split across PDF pages {sorted(pages)}: {alt[:70]}'
            for alt,pages in figures if len(pages)!=1]


def agent_intro_errors(pages):
    """Reject the concrete orphaned lead-in above the Agent pseudocode.

    Figure checks do not cover prose: the flowchart fit with its caption, but
    left one line of the following introduction behind on the previous page.
    """
    normalized=[re.sub(r'\s+','',page) for page in pages]
    intro=[i+1 for i,page in enumerate(normalized)
           if '前面的工具例子只展示了一次调用。' in page]
    code=[i+1 for i,page in enumerate(normalized)
          if 'messages=[system_message,user_message]' in page]
    if len(intro)!=1 or len(code)!=1 or intro!=code:
        return [f'Agent pseudocode lead-in/code split or missing: intro pages {intro}, code pages {code}']
    return []


def toc_folio_errors(entries, folio_targets):
    return [f'TOC page number is not independently linked to {target} (page {page})'
            for page,target in entries if target not in folio_targets]


def ellipse_rect_intersects(ellipse, rect):
    """Whether an axis-aligned text rectangle touches an ellipse's boundary."""
    cx,cy,rx,ry=ellipse
    x0,y0,x1,y1=rect
    dx=0 if x0<=cx<=x1 else min(abs(x0-cx),abs(x1-cx))
    dy=0 if y0<=cy<=y1 else min(abs(y0-cy),abs(y1-cy))
    nearest=(dx/rx)**2+(dy/ry)**2
    farthest=(max(abs(x0-cx),abs(x1-cx))/rx)**2+(max(abs(y0-cy),abs(y1-cy))/ry)**2
    return nearest<=1<=farthest


def contour_label_errors(reader, path, labels):
    """Check actual text/curve clearance in the two-parameter loss figure.

    Bounds/page checks missed a white-backed coordinate label erasing part of
    the inner ellipse. Read the rendered paths and text, with 1pt clearance
    around text to allow for the curve's stroke; interior labels remain valid.
    """
    from pypdf.generic import ContentStream
    dest=labels['fig:loss-two-parameter-contours'][3]
    page_index=reader.get_destination_page_number(reader.named_destinations[dest])
    page=reader.pages[page_index]
    ops=ContentStream(page.get_contents(),reader).operations
    matrix=(1,0,0,1,0,0);stack=[];ellipses=[]
    for i,(values,op) in enumerate(ops):
        if op==b'q':stack.append(matrix)
        elif op==b'Q':matrix=stack.pop()
        elif op==b'cm':
            a,b,c,d,e,f=matrix
            aa,bb,cc,dd,ee,ff=map(float,values)
            matrix=(a*aa+c*bb,b*aa+d*bb,a*cc+c*dd,b*cc+d*dd,
                    a*ee+c*ff+e,b*ee+d*ff+f)
        elif op==b'm' and [v[1] for v in ops[i+1:i+6]]==[b'c']*4+[b'h']:
            a,b,c,d,e,f=matrix
            points=[values]+[v[0][-2:] for v in ops[i+1:i+5]]
            xs=[a*float(x)+c*float(y)+e for x,y in points]
            ys=[float(page.mediabox.height)-(b*float(x)+d*float(y)+f) for x,y in points]
            rx=(max(xs)-min(xs))/2;ry=(max(ys)-min(ys))/2
            if rx>10 and ry>10:  # Exclude the small circular point markers.
                ellipses.append(((min(xs)+max(xs))/2,(min(ys)+max(ys))/2,rx,ry))
    if len(ellipses)!=2:
        return [f'Loss contour audit expected two rendered ellipses, found {len(ellipses)}']
    bbox=subprocess.check_output(['pdftotext','-f',str(page_index+1),'-l',str(page_index+1),
                                  '-bbox-layout',str(path),'-'],text=True)
    errors=[]
    for attrs,word in re.findall(r'<word\s+([^>]+)>(.*?)</word>',bbox,re.S):
        bounds=dict(re.findall(r'(xMin|yMin|xMax|yMax)="([^"]+)"',attrs))
        x0,y0,x1,y1=(float(bounds[key]) for key in ('xMin','yMin','xMax','yMax'))
        rect=(x0-1,y0-1,x1+1,y1+1)
        if any(ellipse_rect_intersects(ellipse,rect) for ellipse in ellipses):
            errors.append(f'Loss contour text/curve collision on PDF page {page_index+1}: {unescape(word)}')
    if not errors:print(f'Loss contour QA: text clears both rendered ellipses on page {page_index+1}')
    return errors


def check_toc_folios(reader, aux, labels):
    """Require right-column folio links, not merely clickable TOC titles."""
    reading=labels['front:reading-routes'][3]
    reading_page=reader.get_destination_page_number(reader.named_destinations[reading])
    entries=[]
    for line in aux.with_suffix('.toc').read_text().splitlines():
        match=re.match(r'\\contentsline\s*\{',line)
        if not match:continue
        pos=match.end()-1;fields=[]
        for _ in range(4):
            while line[pos].isspace():pos+=1
            value,pos=argument(line,pos);fields.append(value)
        kind,_,page,target=fields
        if kind not in ('section','part'):continue
        actual=reader.get_destination_page_number(reader.named_destinations[target])+1
        if actual!=int(page):raise SystemExit(f'TOC folio {page} does not match actual {actual}: {target}')
        entries.append((int(page),target))
    folio_targets=set()
    # Cover and copyright each own one leaf; routes begin after the printed TOC.
    for page in reader.pages[2:reading_page]:
        for ref in page.get('/Annots',[]):
            annot=ref.get_object();action=annot.get('/A')
            if not action:continue
            action=action.get_object()
            if action.get('/S')=='/GoTo' and float(annot['/Rect'][0])>.80*float(page.mediabox.width):
                folio_targets.add(str(action.get('/D')))
    errors=toc_folio_errors(entries,folio_targets)
    if len(entries)<45:errors.append('TOC audit expected at least 45 chapter/part entries')
    if errors:raise SystemExit('\n'.join(errors))
    print(f'TOC folio QA: all {len(entries)} printed page numbers have their own correct destination link')


def check_pdf(path, aux, used):
    from pypdf import PdfReader
    reader=PdfReader(path)
    failures=caption_errors(figure_page_sets(reader))
    raw_text=subprocess.check_output(['pdftotext',str(path),'-'],text=True)
    failures.extend(agent_intro_errors(raw_text.split('\f')))
    text=re.sub(r'\s+','',raw_text)
    labels={}
    for line in aux.read_text().splitlines():
        match=re.match(r'\\newlabel\{([^}]+)\}\{',line)
        if not match:continue
        args,_=argument(line,match.end()-1)
        fields=[];start=0
        while start<len(args) and args[start]=='{':
            value,start=argument(args,start);fields.append(value)
        if len(fields)>=4:labels[match[1]]=fields
    check_toc_folios(reader,aux,labels)
    failures.extend(contour_label_errors(reader,path,labels))
    for target,count in used.items():
        if target not in labels:
            failures.append(f'Missing built label: {target}');continue
        number,page,_,dest=labels[target][:4]
        if not re.fullmatch(r'\d+\.\d+',number) or not dest.startswith('subsection.'):
            failures.append(f'Wrong section destination type: {target}: {number}/{dest}');continue
        target_page=reader.get_destination_page_number(reader.named_destinations[dest])+1
        if target_page!=int(page):failures.append(f'{target}: label page {page} != actual destination {target_page}')
        printed=re.findall(re.escape(number)+r'节[（(]第(\d+)页[）)]',text)
        if len(printed)<count or any(int(x)!=target_page for x in printed):
            failures.append(f'{target}: expected {count} consistent section/page entries for {number}/{target_page}, found {printed}')
    if failures:raise SystemExit('\n'.join(failures))
    print(f'Section/PDF QA: {len(used)} heading targets have matching automatic folios; all {len(figure_page_sets(reader))} diagrams and captions share a page')


def self_test():
    source=r'\subsection{Elective}\label{elective:test}\begin{center}\captionof{figure}{Image}\label{fig:test}'
    targets=section_targets({'demo':source})
    assert targets=={'elective:test'}
    assert not source_errors(r'\sectionentry{elective:test}',targets)
    assert source_errors(r'\sectionentry{fig:test}',targets)
    assert source_errors(r'选读（第~\pageref*{fig:test}~页）',targets)
    assert source_errors('见第 65 页',targets)
    assert not caption_errors([('kept together',{50})])
    assert caption_errors([('old RNN diagram regression',{50,51})])
    intro='前面的工具例子只展示了一次调用。'
    code='1 messages = [system_message, user_message]'
    assert not agent_intro_errors([intro+'\n'+code])
    assert agent_intro_errors([intro,code])
    assert agent_intro_errors([intro])
    assert not toc_folio_errors([(64,'subsection.21.7')],{'subsection.21.7'})
    assert toc_folio_errors([(64,'subsection.21.7')],set())
    ellipse=(0,0,4,2)
    assert not ellipse_rect_intersects(ellipse,(-1,-.5,1,.5))  # Interior label.
    assert not ellipse_rect_intersects(ellipse,(5,0,6,1))     # Exterior label.
    assert ellipse_rect_intersects(ellipse,(3.5,-.5,5,.5))    # Mask across curve.
    assert ellipse_rect_intersects(ellipse,(-5,-3,5,3))        # Boundary enclosed.
    assert ellipse_rect_intersects(ellipse,(4,0,5,1))         # Touching curve.
    print('Section/figure regressions passed: wrong targets, literal folios, split captions, orphaned code introductions and contour collisions are rejected')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--self-test',action='store_true');p.add_argument('--pdf',type=Path);p.add_argument('--aux',type=Path);a=p.parse_args()
    if a.self_test:self_test()
    main=uncomment((ROOT/'book/main.tex').read_text());sources={'main':main}
    for name in re.findall(r'\\input\{chapters/([^}]+)\}',main):sources[name]=uncomment((ROOT/'book/chapters'/f'{name}.tex').read_text())
    targets=section_targets(sources);used={};errors=[]
    for name,body in sources.items():
        # Source diagrams and bibliography page ranges are not section entries.
        errors.extend(f'{name}: {e}' for e in source_errors(body,targets))
        for target in re.findall(r'\\sectionentry\{([^}]+)\}',body):
            if '#' not in target:used[target]=used.get(target,0)+1
    if r'\sectionentry{elective:original-paper}' not in sources['23a-from-toy-to-gpt']:
        errors.append('Real-model chapter must link to original-paper subsection, not its diagram')
    if r'\sectionentry{elective:original-paper}' not in main:
        errors.append('Contents elective entry must use the same heading/page macro as the real-model chapter')
    if 'linktoc=all' not in main:
        errors.append('Enable links on both TOC titles and page numbers')
    if errors:raise SystemExit('\n'.join(errors))
    print('Section navigation source QA passed')
    if a.pdf:
        if not a.aux:p.error('--pdf requires the final --aux')
        check_pdf(a.pdf,a.aux,used)


if __name__=='__main__':main()
