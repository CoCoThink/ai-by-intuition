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
    if re.search(r'\\hyperref\[app:[^]]+\]\{附录[\s~]*[A-G]\.\d+',body):
        errors.append('Appendix link prints a literal subsection number: use the target label')
    for match in re.finditer(r'\\hyperref\[(app:[^]]+)\]\{附录[\s~]*\\ref\*?\{([^}]+)\}',body):
        if match[1]!=match[2]:
            errors.append(f'Appendix link prints a different target number: {match[1]}/{match[2]}')
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


def caption_structure_errors(root, roles=None):
    """Check actual caption ownership, including transparent layout wrappers.

    Custom unbreakable tcolorboxes once leaked their titles into the enclosing
    section through a Div. Same-page figure checks could not detect that error.
    """
    roles=roles or {}
    def resolve(obj):
        return obj.get_object() if hasattr(obj,'get_object') else obj
    def children(obj):
        kids=resolve(obj.get('/K',[]))
        if not isinstance(kids,list):kids=[kids]
        for child in kids:
            child=resolve(child)
            if not isinstance(child,dict) or '/S' not in child:continue
            role=str(roles.get(child['/S'],child['/S']))
            if role in ('/Div','/NonStruct'):yield from children(child)
            else:yield child
    errors=[]
    def walk(obj):
        obj=resolve(obj)
        if isinstance(obj,list):
            for child in obj:walk(child)
        elif isinstance(obj,dict):
            kids=list(children(obj))
            for i,child in enumerate(kids):
                role=str(roles.get(child['/S'],child['/S']))
                if role=='/Caption' and i not in (0,len(kids)-1):
                    errors.append(f'Caption must be the first or last semantic child of {obj.get("/S")}; found child {i+1}/{len(kids)}')
            walk(obj.get('/K',[]))
    walk(root)
    return errors


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


def softmax_note_errors(pages):
    """Keep this short numerical-stability box together. Chapter density checks
    missed its single concluding line stranded above the next subsection."""
    compact=[re.sub(r'\s+','',page) for page in pages]
    markers=('计算机怎样避免指数溢出？',r'1\.3133',
             r'(?:使用同样的减最大值技巧|也先减去最大值|减少下溢风险)。')
    found=[[i+1 for i,page in enumerate(compact) if re.search(marker,page)] for marker in markers]
    if len(found[0])!=1 or any(locations!=found[0] for locations in found[1:]):
        return [f'Softmax stability note split or missing: heading/formula/conclusion pages {found}']
    return []


def attention_boundary_errors(pages):
    """A valid table/figure layout can still split this short explanatory box."""
    compact=[re.sub(r'\s+','',page) for page in pages]
    markers=('零参数点积的匹配规则是固定的：','训练无法让模型学会“按哪些特征匹配”。')
    found=[[i+1 for i,page in enumerate(compact) if marker in page] for marker in markers]
    if len(found[0])!=1 or found[1]!=found[0]:
        return [f'Zero-parameter attention boundary split or missing: start/end pages {found}']
    return []


def ellipse_rect_intersects(ellipse, rect):
    """Whether an axis-aligned text rectangle touches an ellipse's boundary."""
    cx,cy,rx,ry=ellipse
    x0,y0,x1,y1=rect
    dx=0 if x0<=cx<=x1 else min(abs(x0-cx),abs(x1-cx))
    dy=0 if y0<=cy<=y1 else min(abs(y0-cy),abs(y1-cy))
    nearest=(dx/rx)**2+(dy/ry)**2
    farthest=(max(abs(x0-cx),abs(x1-cx))/rx)**2+(max(abs(y0-cy),abs(y1-cy))/ry)**2
    return nearest<=1<=farthest


def iteration_legend_errors(lines, page_width):
    """Bounds and same-page gates miss a legend continuing beside the picture."""
    legend=[row for row in lines if '右图虚线为候选' in row[0]]
    axis=[row for row in lines if row[0].startswith('更新步数')]
    if len(legend)!=1 or '点线为已知最小损失' not in legend[0][0]:
        return ['Iteration legend must occupy one complete line below the plot']
    _,left,top,right,_=legend[0]
    if abs((left+right)/2-page_width/2)>12:
        return ['Iteration legend must be centered below the plot']
    if len(axis)!=1 or top<=axis[0][4]:
        return ['Iteration legend must follow the plot axis label vertically']
    return []


def check_iteration_legend(reader, path, labels):
    import xml.etree.ElementTree as ET
    destination=reader.named_destinations[labels['fig:gradient-iteration-path'][3]]
    page=reader.get_destination_page_number(destination)+1
    xml=subprocess.check_output(['pdftotext','-f',str(page),'-l',str(page),'-bbox-layout',str(path),'-'])
    tree=ET.fromstring(xml);lines=[]
    for node in tree.iter():
        if node.tag.rsplit('}',1)[-1]!='line':continue
        lines.append((re.sub(r'\s+','',''.join(node.itertext())),
                      *(float(node.get(key)) for key in ('xMin','yMin','xMax','yMax'))))
    errors=iteration_legend_errors(lines,float(reader.pages[page-1].mediabox.width))
    if not errors:print(f'Iteration legend QA: one centered line below the plot on page {page}')
    return errors


def activation_label_errors(words):
    errors=[]
    labels=[row for row in words if row[0] in ('正数保留','负数归零')]
    if len(labels)!=2:return ['ReLU figure must have two identifiable branch labels']
    for label in labels:
        for other in words:
            if other is label:continue
            if (min(label[3],other[3])-max(label[1],other[1])>.5 and
                    min(label[4],other[4])-max(label[2],other[2])>.5):
                errors.append(f'ReLU branch label overlaps rendered text: {label[0]} / {other[0]}')
    return errors


def check_activation_labels(reader, path, labels):
    import xml.etree.ElementTree as ET
    destination=reader.named_destinations[labels['fig:relu-function'][3]]
    page=reader.get_destination_page_number(destination)+1
    xml=subprocess.check_output(['pdftotext','-f',str(page),'-l',str(page),'-bbox-layout',str(path),'-'])
    words=[(''.join(node.itertext()),*(float(node.get(key)) for key in ('xMin','yMin','xMax','yMax')))
           for node in ET.fromstring(xml).iter() if node.tag.rsplit('}',1)[-1]=='word']
    errors=activation_label_errors(words)
    if not errors:print(f'ReLU label QA: both branch annotations clear all rendered text on page {page}')
    return errors


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


def page_span_union(spans):
    pages=set()
    for first,last in spans:
        if not 1<=first<=last:raise ValueError(f'Invalid reading page span: {first}/{last}')
        pages.update(range(first,last+1))
    return pages


def reading_ranges(source):
    return {key:[pair.split('/') for pair in ranges.split(',')]
            for key,ranges in re.findall(r'\\setroutebudget\{(quick|standard|hands)\}\{([^{}]+)\}',source)}


def check_reading_budgets(reader,labels):
    """Count actual PDF destination spans and compare with the printed budgets."""
    ranges=reading_ranges((ROOT/'book/chapters/00g-reading-routes.tex').read_text())
    failures=[];counts={}
    for key,pairs in ranges.items():
        spans=[]
        for pair in pairs:
            pages=[]
            for label in pair:
                fields=labels[label]
                actual=reader.get_destination_page_number(reader.named_destinations[fields[3]])+1
                if actual!=int(fields[1]):failures.append(f'Reading endpoint {label}: label/destination mismatch')
                pages.append(actual)
            spans.append(pages)
        counts[key]=len(page_span_union(spans))
    first=reader.get_destination_page_number(reader.named_destinations[labels['front:reading-routes'][3]])
    text=re.sub(r'\s+','',''.join(page.extract_text() for page in reader.pages[first:first+3]))
    for key,title in [('quick','速读'),('standard','标准'),('hands','动手')]:
        found=re.findall(title+r'，约(\d+)页',text)
        if found!=[str(counts[key])]:failures.append(f'{title}: printed budget {found} differs from actual deduplicated {counts[key]} pages')
    if counts['quick']>=counts['standard']:failures.append('Quick reading route must cover fewer pages than standard reading')
    if not failures:print(f'Reading budget QA: printed quick/standard/hands match actual deduplicated page spans {counts}')
    return failures


def check_forward_appendix_link(reader, path, labels):
    """Inspect the printed text inside the actual link to the full parameter table."""
    import xml.etree.ElementTree as ET
    target='app:transformer-intermediates'
    number,folio,_,dest=labels[target][:4]
    actual_page=reader.get_destination_page_number(reader.named_destinations[dest])+1
    if actual_page!=int(folio):return [f'{target}: label/destination page mismatch']
    source=reader.get_destination_page_number(reader.named_destinations[labels['intro:22b-token-to-output'][3]])
    page=reader.pages[source]
    xml=subprocess.check_output(['pdftotext','-f',str(source+1),'-l',str(source+1),
                                 '-bbox-layout',str(path),'-'])
    words=[node for node in ET.fromstring(xml).iter() if node.tag.rsplit('}',1)[-1]=='word']
    fragments=[]
    for ref in page.get('/Annots',[]):
        annot=ref.get_object();action=annot.get('/A')
        if action is None:continue
        action=action.get_object()
        if action.get('/S')!='/GoTo' or str(action.get('/D'))!=dest:continue
        left,bottom,right,top=map(float,annot['/Rect']);height=float(page.mediabox.height)
        for word in words:
            x=(float(word.get('xMin'))+float(word.get('xMax')))/2
            y=(float(word.get('yMin'))+float(word.get('yMax')))/2
            if left-1<=x<=right+1 and height-top-1<=y<=height-bottom+1:
                fragments.append(''.join(word.itertext()))
    printed=re.sub(r'\s+','',''.join(fragments))
    if not re.search(r'(?<![A-Za-z0-9.])'+re.escape(number)+r'(?![0-9.])',printed):
        return [f'Forward parameter link must print actual appendix {number}; found {printed!r} on page {source+1}']
    print(f'Forward appendix link QA: printed {number} resolves to its actual parameter-table page {actual_page}')
    return []


def printed_exercise_errors(found, expected):
    return [] if found==expected else [f'Printed exercise sequence differs: {found[:8]} ... (expected {len(expected)} entries, found {len(found)})']


def check_exercise_destinations(reader,path,labels):
    from generate_exercise_bank import load_exercises,printed_regular
    data,_,titles=load_exercises()
    rows=printed_regular(data,titles)
    failures=[]
    pages=subprocess.check_output(['pdftotext','-layout',str(path),'-'],text=True).split('\f')
    for prefix in ('exercise:','solution:'):
        first=reader.get_destination_page_number(reader.named_destinations[labels[prefix+rows[0]['id']][3]])
        last=reader.get_destination_page_number(reader.named_destinations[labels[prefix+rows[-1]['id']][3]])
        found=re.findall(r'(?m)^\s*(C-\d{3})\.', '\n'.join(pages[first:last+1]))
        failures.extend(printed_exercise_errors(found,[r['id'] for r in rows]))
        # Check the actual destination page for each question/answer, not only the labels' existence.
        for row in rows:
            key=prefix+row['id'];fields=labels[key]
            page=reader.get_destination_page_number(reader.named_destinations[fields[3]])
            if page+1!=int(fields[1]) or not re.search(r'(?m)^\s*'+re.escape(row['id'])+r'\.',pages[page]):
                failures.append(f'{key}: destination does not show the matching printed exercise')
    if not failures:print(f'Printed exercise QA: {len(rows)} continuous C numbers and matching actual question/answer destinations')
    return failures


def check_reproduction_and_definitions(reader,labels):
    """Verify actual page contents and the executable-code link, beyond valid labels."""
    failures=[]
    expected={
        'concept:dot-product':('同位置相乘','点积'),
        'concept:cosine-similarity':('余弦相似度','长度'),
        'concept:vit':('ViT','Transformer'),
        'concept:patch':('Patch','局部'),
        'concept:clip':('CLIP','配对'),
        'concept:test-time-compute':('冻结参数','验证器'),
        'concept:mamba':('Mamba','状态空间'),
        'concept:yarn':('YaRN','RoPE'),
        'concept:qk-norm':('QK-Norm','尺度'),
        'concept:cross-correlation':('互相关','翻转'),
        'concept:gqa':('GQA','共享一组'),
        'concept:mla':('多头潜在注意力','潜在向量'),
        'concept:linear-attention':('固定大小','Softmax','外积'),
        'example:gqa-budget':('真实配置','Qwen2.5-0.5B'),
        'app:data-map':('算例数据地图','三维贯通主例','四维双头'),
        'sec:toy-real-model-comparison':('可训练参数','99','GPT-2small'),
    }
    for label,words in expected.items():
        dest=reader.named_destinations[labels[label][3]]
        page=reader.get_destination_page_number(dest)
        text=re.sub(r'\s+','',reader.pages[page].extract_text())
        if any(word not in text for word in words):
            failures.append(f'{label}: definition words {words} absent at actual destination page {page+1}')
    code_targets={
        'https://colab.research.google.com/github/CoCoThink/ai-by-intuition/blob/':'notebooks/pytorch_starter.ipynb',
        'https://github.com/CoCoThink/ai-by-intuition/blob/':'scripts/pytorch_starter.py',
    }
    links={suffix:[] for suffix in code_targets.values()}
    for page in reader.pages:
        for ref in page.get('/Annots',[]):
            action=ref.get_object().get('/A')
            if action is not None:
                uri=str(action.get_object().get('/URI',''))
                for prefix,suffix in code_targets.items():
                    if uri.startswith(prefix) and uri.endswith('/'+suffix):
                        links[suffix].append(uri[len(prefix):-(len(suffix)+1)])
    copyright_text=re.sub(r'\s+','',reader.pages[1].extract_text())
    for suffix,revisions in links.items():
        if revisions:
            if len(revisions)!=1:failures.append(f'Expected one versioned code destination: {suffix}')
            for sha in revisions:
                if not re.fullmatch(r'[0-9a-f]{40}',sha) or sha[:12] not in copyright_text:
                    failures.append(f'Code revision differs from PDF copyright source: {suffix}: {sha}')
        elif '编译来源为Git提交' in copyright_text:
            failures.append(f'PDF has Git provenance but lacks a matching versioned code link: {suffix}')
    if not failures:print(f'Reproduction/lookup QA: Notebook/script SHAs match copyright; {len(expected)} actual destinations contain their definitions')
    return failures


def rendered_line_segments(reader,page):
    """Read stroked lines after applying the actual PDF coordinate transforms."""
    from pypdf.generic import ContentStream
    matrix=(1,0,0,1,0,0);width=1;stack=[];point=None;lines=[];found=[]
    def transform(x,y):
        a,b,c,d,e,f=matrix
        return a*x+c*y+e,b*x+d*y+f
    for values,op in ContentStream(page.get_contents(),reader).operations:
        if op==b'q':stack.append((matrix,width))
        elif op==b'Q':matrix,width=stack.pop()
        elif op==b'cm':
            a,b,c,d,e,f=matrix;aa,bb,cc,dd,ee,ff=map(float,values)
            matrix=(a*aa+c*bb,b*aa+d*bb,a*cc+c*dd,b*cc+d*dd,a*ee+c*ff+e,b*ee+d*ff+f)
        elif op==b'w':width=float(values[0])
        elif op==b'm':point=transform(*map(float,values));lines=[]
        elif op==b'l':
            end=transform(*map(float,values))
            if point is not None:lines.append((point,end))
            point=end
        elif op in (b'S',b's'):
            for (x0,y0),(x1,y1) in lines:
                found.append((width,x0,y0,x1,y1))
            lines=[]
        elif op in (b'n',b'f',b'f*',b'B',b'B*'):lines=[]
    return found


def chapter_divider_positions(reader,page):
    """Find the actual full-width .55pt chapter rules in PDF coordinates."""
    return [float(page.mediabox.height)-(y0+y1)/2
            for width,x0,y0,x1,y1 in rendered_line_segments(reader,page)
            if abs(width-.548)<.01 and abs(y0-y1)<.1 and abs(x1-x0)>.7*float(page.mediabox.width)]


def normalization_arrow_errors(segments):
    """Both copies of q must point up and right within their own panels.

    A named TikZ point outside a translated scope once made the right-hand
    arrow reach back into the left panel. Correct literal coordinates and
    same-page captions alone did not reveal the rendered connection.
    """
    diagonals=[(x1-x0,y1-y0) for _,x0,y0,x1,y1 in segments
               if abs(x1-x0)>12 and abs(y1-y0)>12]
    if len(diagonals)!=2 or any(not(15<dx<40 and 20<dy<50 and abs(dx/dy-.75)<.03)
                                for dx,dy in diagonals):
        return [f'Normalization figure: demand arrows must stay in their own panels, got {diagonals}']
    return []


def check_normalization_arrows(reader,path,labels):
    import xml.etree.ElementTree as ET
    dest=reader.named_destinations[labels['fig:dot-product-length'][3]]
    page_index=reader.get_destination_page_number(dest);page=reader.pages[page_index]
    xml=subprocess.check_output(['pdftotext','-f',str(page_index+1),'-l',str(page_index+1),
                                 '-bbox-layout',str(path),'-'])
    lines=[(re.sub(r'\s+','',''.join(node.itertext())),float(node.get('yMin')))
           for node in ET.fromstring(xml).iter() if node.tag.rsplit('}',1)[-1]=='line']
    top=[y for text,y in lines if '整体放大，方向不变' in text]
    bottom=[y for text,y in lines if '放大B会提高原始点积' in text]
    if len(top)!=1 or len(bottom)!=1:return ['Normalization figure: actual panel/caption bounds missing']
    height=float(page.mediabox.height)
    segments=[line for line in rendered_line_segments(reader,page)
              if all(top[0]<height-y<bottom[0] for y in (line[2],line[4]))]
    errors=normalization_arrow_errors(segments)
    if not errors:print(f'Normalization arrow QA: both rendered demand arrows stay within their panels on page {page_index+1}')
    return errors


def check_chapter_dividers(reader,labels):
    failures=[];seen=set();top_count=0;mixed_count=0
    for label,fields in labels.items():
        if not label.startswith('intro:') or not re.fullmatch(r'section\.\d+',fields[3]):continue
        target=fields[3]
        if target in seen:continue
        seen.add(target)
        dest=reader.named_destinations[target];page_number=reader.get_destination_page_number(dest)
        page=reader.pages[page_number];heading_top=float(page.mediabox.height)-float(dest.top)
        rules=chapter_divider_positions(reader,page)
        above=[y for y in rules if y<=heading_top+2]
        body_baselines=[]
        def collect(text,cm,tm,font,size):
            if text.strip():body_baselines.append(float(page.mediabox.height)-(cm[1]*tm[4]+cm[3]*tm[5]+cm[5]))
        page.extract_text(visitor_text=collect)
        # Use actual earlier body text, not a heading-height threshold: the
        # redundant rule itself used to push a fresh-page heading downward.
        # The 22mm text margin is the geometry setting in book/main.tex.
        mixed=any(22*72/25.4-1<=y<heading_top-2 for y in body_baselines)
        if not mixed:
            top_count+=1
            if above:failures.append(f'{label}: redundant chapter divider above page-opening heading on page {page_number+1}')
        else:
            mixed_count+=1
            if not any(0<=heading_top-y<=60 for y in above):
                failures.append(f'{label}: missing divider before mixed-page chapter heading on page {page_number+1}')
    if not failures:print(f'Chapter divider QA: {top_count} page-opening headings have no duplicate rule; {mixed_count} mixed-page headings retain separation')
    return failures


def check_pdf(path, aux, used):
    from pypdf import PdfReader
    reader=PdfReader(path)
    failures=caption_errors(figure_page_sets(reader))
    root=reader.trailer['/Root']['/StructTreeRoot']
    failures.extend(caption_structure_errors(root,root.get('/RoleMap',{})))
    raw_text=subprocess.check_output(['pdftotext',str(path),'-'],text=True)
    failures.extend(agent_intro_errors(raw_text.split('\f')))
    failures.extend(softmax_note_errors(raw_text.split('\f')))
    failures.extend(attention_boundary_errors(raw_text.split('\f')))
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
    for primary,legacy in (
        ('intro:00-functions','intro:16-loss-gradient'),
        ('intro:21c-naive-attention','intro:21b-why-attention'),
        ('intro:23c-post-training','intro:23cc-test-time-compute'),
        ('intro:04-key-value-outer-product','intro:06-better-linear-memory'),
        ('intro:09-nonlinearity-and-memory','intro:13-capacity'),
        ('check:00-functions','check:16-loss-analytic'),
        ('check:21c-naive-attention','check:21b-why-attention'),
        ('check:23c-post-training','check:23cc-test-time-compute'),
        ('check:04-key-value-outer-product','check:06-better-linear-memory'),
        ('check:09-nonlinearity-and-memory','check:13-capacity'),
    ):
        if primary not in labels or legacy not in labels or labels[primary][3]!=labels[legacy][3]:
            failures.append(f'Merged compatibility link resolves to a different destination: {primary}/{legacy}')
    failures.extend(check_exercise_destinations(reader,path,labels))
    failures.extend(check_reproduction_and_definitions(reader,labels))
    failures.extend(check_chapter_dividers(reader,labels))
    failures.extend(check_reading_budgets(reader,labels))
    check_toc_folios(reader,aux,labels)
    failures.extend(check_forward_appendix_link(reader,path,labels))
    failures.extend(contour_label_errors(reader,path,labels))
    failures.extend(check_iteration_legend(reader,path,labels))
    failures.extend(check_activation_labels(reader,path,labels))
    failures.extend(check_normalization_arrows(reader,path,labels))
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
    assert page_span_union([(3,5),(5,7),(3,3)])==set(range(3,8))
    assert reading_ranges(r'\setroutebudget{quick}{a/b,c/d}')=={'quick':[['a','b'],['c','d']]}
    assert not printed_exercise_errors(['C-001','C-002'],['C-001','C-002'])
    assert printed_exercise_errors(['C-001','C-120','C-002'],['C-001','C-002','C-003'])
    source=r'\subsection{Elective}\label{elective:test}\begin{center}\captionof{figure}{Image}\label{fig:test}'
    targets=section_targets({'demo':source})
    assert targets=={'elective:test'}
    assert not source_errors(r'\sectionentry{elective:test}',targets)
    assert source_errors(r'\sectionentry{fig:test}',targets)
    assert source_errors(r'选读（第~\pageref*{fig:test}~页）',targets)
    assert source_errors('见第 65 页',targets)
    assert source_errors(r'\hyperref[app:full]{附录 B.1 的参数}',targets)
    assert not source_errors(r'\hyperref[app:full]{附录~\ref*{app:full} 的参数}',targets)
    assert source_errors(r'\hyperref[app:rational-mini]{附录~\ref*{app:transformer-intermediates}}',targets)
    assert not caption_errors([('kept together',{50})])
    assert caption_errors([('old RNN diagram regression',{50,51})])
    leaked={'/S':'/Sect','/K':[{'/S':'/H2'},{'/S':'/Div','/K':[{'/S':'/Caption'}]},{'/S':'/P'}]}
    assert caption_structure_errors(leaked)
    owned={'/S':'/Sect','/K':[{'/S':'/H2'},{'/S':'/Sect','/K':[{'/S':'/Caption'},{'/S':'/P'}]},{'/S':'/P'}]}
    assert not caption_structure_errors(owned)
    assert not caption_structure_errors({'/S':'/Figure','/K':[{'/S':'/P'},{'/S':'/Caption'}]})
    intro='前面的工具例子只展示了一次调用。'
    code='1 messages = [system_message, user_message]'
    assert not agent_intro_errors([intro+'\n'+code])
    assert agent_intro_errors([intro,code])
    assert agent_intro_errors([intro])
    note='计算机怎样避免指数溢出？'
    result='1.3133'
    ending='这种 LogSumExp 写法避免先算极小概率再取对数，减少下溢风险。'
    assert not softmax_note_errors([note+result+ending])
    assert softmax_note_errors([note+result,ending])
    assert softmax_note_errors([note+ending])
    attention_start='零参数点积的匹配规则是固定的：'
    attention_end='训练无法让模型学会“按哪些特征匹配”。'
    assert not attention_boundary_errors([attention_start+attention_end])
    assert attention_boundary_errors([attention_start,attention_end])
    assert attention_boundary_errors([attention_start])
    assert not toc_folio_errors([(64,'subsection.21.7')],{'subsection.21.7'})
    assert toc_folio_errors([(64,'subsection.21.7')],set())
    ellipse=(0,0,4,2)
    assert not ellipse_rect_intersects(ellipse,(-1,-.5,1,.5))  # Interior label.
    assert not ellipse_rect_intersects(ellipse,(5,0,6,1))     # Exterior label.
    assert ellipse_rect_intersects(ellipse,(3.5,-.5,5,.5))    # Mask across curve.
    assert ellipse_rect_intersects(ellipse,(-5,-3,5,3))        # Boundary enclosed.
    assert ellipse_rect_intersects(ellipse,(4,0,5,1))         # Touching curve.
    legend=('右图虚线为候选B，点线为已知最小损失',100,300,500,312)
    axis=('更新步数t',400,280,480,292)
    assert not iteration_legend_errors([legend,axis],600)
    assert iteration_legend_errors([('右图虚线为候选',500,300,590,312),axis],600)
    assert iteration_legend_errors([(legend[0],300,300,590,312),axis],600)
    assert iteration_legend_errors([legend,('更新步数t',400,310,480,322)],600)
    positive=('正数保留',335,63,375,78)
    negative=('负数归零',220,138,260,153)
    assert activation_label_errors([positive,negative,('ReLU(t)',303,68,340,78)])
    assert not activation_label_errors([positive,negative,('ReLU(t)',280,68,320,78)])
    demand_arrows=[(1,100,200,127,236),(1,330,200,357,236)]
    assert not normalization_arrow_errors(demand_arrows)
    assert normalization_arrow_errors([demand_arrows[0],(1,330,200,127,236)])
    print('Section/figure regressions passed: wrong targets, literal folios, split captions/Softmax/attention notes, orphaned code introductions, contour collisions, displaced legends, ReLU label overlaps and cross-panel arrows are rejected')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--self-test',action='store_true');p.add_argument('--pdf',type=Path);p.add_argument('--aux',type=Path);a=p.parse_args()
    if a.self_test:self_test()
    main=uncomment((ROOT/'book/main.tex').read_text());sources={'main':main}
    for name in re.findall(r'\\input\{chapters/([^}]+)\}',main):sources[name]=uncomment((ROOT/'book/chapters'/f'{name}.tex').read_text())
    targets=section_targets(sources);used={};errors=[]
    ranges=reading_ranges(sources['00g-reading-routes'])
    if set(ranges)!={'quick','standard','hands'}:
        errors.append('All three reading routes need explicit page ranges and a printed budget')
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
