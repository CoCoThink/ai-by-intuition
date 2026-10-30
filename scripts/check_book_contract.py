#!/usr/bin/env python3
"""Semantic and pedagogical source gates, independent of TeX compilation.

Existence of a reference is insufficient: validate the training/generation roles,
chapter ownership, unique self-checks, notation, source dates and question/answer
bijections. All cardinalities derive from the canonical inventories where possible.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import re
from check_chapter_crossrefs import uncomment
from generate_chapter_navigation import argument, lesson_metadata, validate_navigation

ROOT=Path(__file__).resolve().parents[1]
BOOK=ROOT/'book'
PART_TITLES=[
    '学习是什么：从规则到参数更新','把许多数一起算','让文字进入计算',
    '让词与词交换信息','组装并训练 Transformer','从语言模型到助手',
    '架构为什么在变，往哪走','换一种数据看 Transformer：从 CNN 到 ViT','联想记忆与线性状态']
CHAPTER_COUNT=34


def read_sources():
    main=uncomment((BOOK/'main.tex').read_text())
    names=re.findall(r'\\input\{chapters/([^}]+)\}',main)
    return main,{name:uncomment((BOOK/'chapters'/f'{name}.tex').read_text()) for name in names}


def core_groups():
    main,sources=read_sources(); groups=[]; current=None
    for name in re.findall(r'\\input\{chapters/([^}]+)\}', main.split(r'\appendix',1)[0]):
        for m in re.finditer(r'\\section(\*)?\{|\\chapterchecktasks\{([^}]+)\}',sources[name]):
            if m[2]:
                if current is None:raise ValueError(f'{name}: self-check has no chapter')
                current['checks'].append(m[2])
            elif not m[1] or name=='00-guide':
                title,_=argument(sources[name],m.end()-1)
                current=dict(title=title,numbered=not bool(m[1]),checks=[])
                groups.append(current)
    return groups


def ten_step_errors(body):
    # The targets can both exist and still point to the wrong kind of lesson.
    match=re.search(r'\\item \\textbf\{选择训练或生成\}：(.*?)(?=\\end\{enumerate\})',body,re.S)
    if not match:return ['Missing training/generation fork in step 10']
    targets=re.findall(r'\\ref\*?\{([^}]+)\}',match[1])
    if targets!=['intro:22c-language-training','intro:23-llm-systems']:
        return [f'Step 10 must link TRAINING then GENERATION, found {targets}']
    return []


def notation_errors(body):
    errors=[]
    row_vector=r'\\vect(?:\{[A-Za-z]+\}|\s+[A-Za-z])(?:_\{[^{}]+\}|_[A-Za-z0-9])?\^\\top'
    if re.search(row_vector+r'\s*\\cdot\s*'+row_vector,body):
        errors.append('Use row-column dot products consistently, including the first definition')
    if re.search(r'\\\|\s*'+row_vector+r'\s*\\\|',body):
        errors.append('Use the common norm notation without a transpose on a named vector')
    if re.search(r'\\log(?![A-Za-z])',body):errors.append('Natural logarithms must use ln consistently')
    if re.search(r'W_\{\\rm vocab\}|\\(?:widehat|hat)\s*(?:\{P\}|P\b)',body):
        errors.append('Use W_out and Pi, not W_vocab/hat P')
    if re.search(r'\\(?:widehat|hat)(?![A-Za-z])\s*(?!\s*\{)',body):
        errors.append('Accents require a braced argument')
    for m in re.finditer(r'\\(?:widehat|hat)\s*\{',body):
        value,_=argument(body,m.end()-1)
        if re.search(r'=|\\(?:approx|to|in)(?![A-Za-z])',value):
            errors.append('Accent scope contains a relation instead of a symbol')
    if re.search(r'\\to L:T\\times\|',body):errors.append('Logits must be Z; L is loss')
    if re.search(r'A\^\{\(\\ell\)\}',body):errors.append('MLP activations must be F, not attention A')
    if re.search(r'(?<![A-Za-z])P\s*&:',body):errors.append('Position parameter counts must use P_pos')
    if re.search(r'Best-of-(?:\$N\$|N\b)',body):errors.append('Candidate counts must use Best-of-n')
    if re.search(r'\\(?:nolinkurl|url)\{python3\s',body):errors.append('Typeset shell commands with texttt; URL macros discard spaces')
    if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]',body):errors.append('Control character in TeX')
    return errors


def concept_anchor_errors(body, label, heading):
    """A valid label can silently inherit an item number or the wrong section."""
    marker = r'\label{' + label + '}'
    if body.count(marker) != 1:
        return [f'{label}: expected one concept anchor']
    prefix = body.split(marker, 1)[0]
    headings = list(re.finditer(r'\\subsection\{', prefix))
    if not headings:
        return [f'{label}: missing subsection owner']
    last = headings[-1]
    title, end = argument(prefix, last.end()-1)
    if title != heading:
        return [f'{label}: concept belongs to {heading}, found {title}']
    # Requiring placement immediately after its heading avoids inherited item,
    # equation and other local counters, even though the hyperlink itself works.
    between = re.sub(r'\\phantomsection|\\label\{[^}]+\}', '', prefix[end:])
    return [] if not between.strip() else [f'{label}: anchor must follow its subsection heading before any content/counter']


def fitting_color_errors(body):
    """Validate the plotted marks AND their prose key; raw colors alone miss it."""
    required = (r'\fill[noisecolor]', r'\draw[flowcolor,very thick]',
                '黑点是带测量噪声的训练样本，蓝灰线')
    return [] if all(s in body for s in required) and '橙点' not in body else [
        'Fitting illustration and caption must agree: black noise points, blue-gray curves']


def visible_exercise_errors(body, valid_ids=()):
    """A hidden compatibility label may exist while its printed ID is obsolete."""
    import re
    visible=re.sub(r'\\label\{[^}]+\}|\\hyperref\[[^]]+\]', '', body)
    errors=[]
    if re.search(r'(?<![A-Za-z0-9])C[1-4]-\d+(?!\d)',visible):
        errors.append('Visible legacy exercise ID: use the canonical C-xxx or R-xx label')
    if valid_ids:
        missing=set(re.findall(r'(?<![A-Za-z0-9])(?:C-\d{3}|R-\d{2})(?!\d)',visible))-set(valid_ids)
        if missing:errors.append(f'Unknown printed exercise IDs: {sorted(missing)}')
    return errors


def exercise_link_text_errors(body, aliases):
    errors=[]
    for match in re.finditer(r'\\hyperref\[exercise:([^]]+)\]\{',body):
        text,_=argument(body,match.end()-1)
        printed=re.findall(r'(?<![A-Za-z0-9])(?:C-\d{3}|R-\d{2})(?!\d)',text)
        if printed and (match[1] not in aliases or printed!=[aliases[match[1]]]):
            errors.append(f'Exercise link {match[1]} prints the wrong canonical ID: {printed}')
    return errors


def review_ownership_errors(data, navigation):
    reviews={r['id'] for r in data if r.get('part_review')}
    errors=[]
    if len(reviews)!=18 or any(not re.fullmatch(r'R-\d{2}',x) for x in reviews):
        errors.append('Cumulative reviews require 18 independent R IDs')
    if reviews & set(re.findall(r'R-\d{2}',navigation)):
        errors.append('Cumulative review must not also be assigned as last-chapter practice')
    return errors


def route_caption_errors(body):
    return ['Route micro-map must have an unnumbered semantic caption'] if (
        r'\captionof{figure}' in body or r'tag=Caption' not in body) else []


def part_bookend_errors(main, sources):
    """Each part opens and closes with its own key; the opener's think-first
    answer (partq:<key>) must be taught inside that same part."""
    errors=[];core=main.split(r'\appendix',1)[0]
    first=core.find(r'\part{')
    if first<0 or core.find(r'\input{chapters/00-guide}') not in range(0,first):
        errors.append('Prologue must precede Part 1')
    for seg in re.split(r'(?=\\part\{)',core[first:]):
        label=re.search(r'\\label\{part:([^}]+)\}',seg)
        if not label:continue
        key=label[1]
        entries=re.findall(r'(?m)^\\partentry([a-z]+)\s*$',seg);exits=re.findall(r'(?m)^\\partexit([a-z]+)\s*$',seg)
        if entries!=[key] or exits!=[key]:errors.append(f'part:{key}: needs one \\partentry{key} and one \\partexit{key}, found {entries}/{exits}')
        owners=[n for n in re.findall(r'\\input\{chapters/([^}]+)\}',seg) if r'\label{partq:'+key+'}' in sources.get(n,'')]
        if len(owners)!=1:errors.append(f'part:{key}: think-first answer partq:{key} must sit in exactly one chapter of this part, found {owners}')
    return errors


def ending_order_errors(body):
    errors=[]
    for chunk in re.split(r'\\section\*?\{',body):
        check=chunk.find(r'\chapterchecktasks{')
        recap=chunk.find(r'\begin{conclusion}')
        if check>=0 and 0<=recap<check:
            errors.append('Chapter ending must place self-check before recap')
    return errors


def chapter_opening_errors(destination_top, page_height, text, boilerplate_han_count=0):
    errors=[]
    # PDF coordinates grow upwards: reserve one-third of the printable body.
    if destination_top-65 < .32*(page_height-120):
        errors.append('Chapter starts in the bottom third of the printable page')
    # Count the actual body after excluding the title and any optional route box.
    # A prose opener and a route box must both leave room for substantive text.
    han_count=len(re.findall(r'[\u4e00-\u9fff]',text))
    if han_count < boilerplate_han_count+30:
        errors.append('Chapter opener strands its heading without substantive text')
    return errors


def validate_contract():
    errors=[]
    main,sources=read_sources()
    def require(condition,message):
        if not condition:errors.append(message)
    require(re.findall(r'\\part\{([^}]+)\}',main)==PART_TITLES,'Nine-part curriculum order changed')
    groups=core_groups()
    require(sum(g['numbered'] for g in groups)==CHAPTER_COUNT,f'Expected {CHAPTER_COUNT} numbered chapters')
    for g in groups:require(len(g['checks'])==1,f"{g['title']}: needs one self-check, found {g['checks']}")
    require(len(groups)==CHAPTER_COUNT+1,'One unnumbered prelude must have a self-check')
    allchecks=[slug for g in groups for slug in g['checks']]
    require(len(set(allchecks))==len(allchecks),'Repeated self-check slug')
    # Merged legacy chapter links must resolve to the same numbered chapter,
    # and each part map must contain one entry per actual chapter.
    owners,_=lesson_metadata()
    for primary,legacy in (
        ('00-functions','16-loss-gradient'),
        ('21c-naive-attention','21b-why-attention'),
        ('23c-post-training','23cc-test-time-compute'),
        ('04-key-value-outer-product','06-better-linear-memory'),
        ('09-nonlinearity-and-memory','13-capacity'),
    ):
        require(owners.get('intro:'+primary)==owners.get('intro:'+legacy)==primary,
                f'{legacy}: old chapter link is not owned by merged chapter {primary}')
    part_maps=(BOOK/'part-maps.tex').read_text()
    entries=re.findall(r'\\mapchapter\{([^}]+)\}',part_maps)
    mapped=[owners.get('intro:'+entry) for entry in entries]
    require(len(mapped)==CHAPTER_COUNT and len(set(mapped))==CHAPTER_COUNT,
            'Part maps must list each merged chapter once')
    require('阅读指南' not in main and '阅读指南' not in sources['20b-task-contract'],'Prelude must be called 序章')
    errors.extend(ten_step_errors(sources['22-transformer-architecture']))
    for filename,label,heading in (
        ('23b-deployment-and-ecosystem','concept:evaluation-contamination','训练数据工程：来源、清洗、去重与配比'),
        ('23e-tech-judgement','concept:evaluation-contamination-benchmark','为什么 Benchmark 高分仍需要复核？'),
        ('23-llm-systems','concept:autoregressive','为什么训练能一次算多个位置，自回归生成却要逐个产生？'),
    ):
        errors.extend(concept_anchor_errors(sources[filename],label,heading))
    combined={'main':main,**sources,'part-maps':(BOOK/'part-maps.tex').read_text(),
              'part-reviews':(BOOK/'part-reviews.tex').read_text()}
    for p in (BOOK/'figures').glob('*.tex'):combined['figures/'+p.name]=uncomment(p.read_text())
    for name,body in combined.items():
        errors.extend(f'{name}: {e}' for e in notation_errors(body))
        errors.extend(f'{name}: {e}' for e in ending_order_errors(body))
    for name in ('00c-symbols','11-softmax-memory','04-key-value-outer-product',
                 '05-memory-interference','06-better-linear-memory','08-stacking-key-value',
                 '09-nonlinearity-and-memory','13-capacity'):
        body=sources[name].replace(r'\mathcal{M}','')
        require(not re.search(r'(?<![A-Za-z])M(?![A-Za-z])',body),f'{name}: KV/memory counts must use T_k, not M')
    require('d_h' not in sources['22d-modern-transformers'],'Modern head widths must use d_k; d_h is the RNN state width')
    require(not re.search(r'(?<![A-Za-z])N(?![A-Za-z_])', sources['23cc-test-time-compute']),
            'Test-time candidate counts must use n')
    for name in ('04-key-value-outer-product','05-memory-interference','06-better-linear-memory',
                 '08-stacking-key-value','09-nonlinearity-and-memory','14-summary','13-capacity'):
        require(not re.search(r'(?<![A-Za-z\\])S(?![A-Za-z])', sources[name]),
                f'{name}: memory state must be mathcal M, not attention score S')
    # Explicit source graph and virtual macro labels; check both ref existence and uniqueness.
    label_list=[]
    for name,body in combined.items():
        for label in re.findall(r'\\label\{([^}]+)\}',body):
            if '#' not in label:label_list.append(label)
    label_list+=['check:'+s for s in allchecks]
    duplicates=[x for x,n in Counter(label_list).items() if n>1]
    require(not duplicates,f'Duplicate source labels: {duplicates}')
    labels=set(label_list)
    for name,body in combined.items():
        targets=re.findall(r'\\(?:page)?ref\*?\{([^}]+)\}|\\hyperref\[([^]]+)\]|\\(?:termref|conceptlink)\{([^}]+)\}',body)
        for values in targets:
            target=next(v for v in values if v)
            if '#' in target:continue
            # conceptlink uses an abbreviated concept namespace.
            if target not in labels and 'concept:'+target not in labels:
                errors.append(f'{name}: undefined semantic target {target}')
    require(r'\newcommand{\chapterinlinehint}[1]{}' in main,'Hints must not render under self-checks')
    require(r'\begin{tcolorbox}[enhanced,breakable,colback=white' in main,'Self-checks must flow across pages')
    require('bookmarksdepth=2' in main and r'\setcounter{tocdepth}{1}' in main,'Chapter TOC and subsection bookmarks required')
    require('tagging=on' in main and 'pdfstandard=ua-2' in main and 'mathml-AF' in main,'Keep tagged PDF/UA-2 with MathML AF')
    require('local-build' not in main,'Unknown SHA must not be printed')
    require(r'\sourcecheck' in main,'Source date macro missing')
    require('选读：对照原论文' in sources['22-transformer-architecture'],'Paper comparison must be elective')
    require('训练资料从哪里来' not in sources['23aa-pretraining-icl'] and
            '训练数据工程' in sources['23b-deployment-and-ecosystem'] and
            'concept:pretraining-data' not in sources['23a-from-toy-to-gpt'],'Data cleaning must be outside ICL chapter')
    require(lesson_metadata()[0].get('intro:23cc-test-time-compute')=='23c-post-training' and
            '冻结参数' in sources['23cc-test-time-compute'],
            'Training feedback and fixed-weight verification must share a chapter with an explicit boundary')
    for marker in ('concept:bos-eos','concept:prefill-decode','concept:autoregressive'):
        require(marker in sources['23-llm-systems'],f'Missing generation interface: {marker}')
    require('concept:chat-template' in sources['23c-post-training'],'Chat template explanation missing')
    require('12{,}288' in sources['22d-modern-transformers'] and '402{,}653{,}184' in sources['22d-modern-transformers'],'Real KV byte estimate missing')
    for fragment in ('P_{\\rm pos}',r'\Pi',r'W_{\rm out}',r'\mathcal{M}',r'N_{\rm layer}'):
        require(fragment in sources['00c-symbols'],f'Symbol table missing {fragment}')
    for fragment in ('T_q','T_k','Best-of-$n$',r'\beta_1,\beta_2','LayerNorm',r'\texttt{loss}',r'\texttt{logits}'):
        require(fragment in sources['00c-symbols'],f'Symbol/code table missing {fragment}')
    require(r'\ln[p(1-p)]' in sources['21a-context-gap'] and
            '固定窗口 MLP 或 RNN' in sources['21a-context-gap'],'Context motivation must connect the loss bound to missing history and explain alternatives')
    require('experiment:attention-selection' in sources['22c-language-training'] and
            'figures/learned-attention-selection' in sources['22c-language-training'],
            'Context training must show learned Q/K selection')
    require('叙述借鉴与第三方许可见版权页' not in main,'Remove cover credit pointer')
    memory_part=main.split(r'\part{联想记忆与线性状态}',1)[1].split(r'\clearpage',1)[0]
    require('Alex Wang' in memory_part and 'source:alex-wang' in memory_part,'Memory part opener must credit its teaching framework')
    # One framework acknowledgment at the part entrance; F keeps the citation.
    require(main.count('Alex Wang')==1 and
            all('Alex Wang' not in body for name,body in sources.items() if name!='26-sources'),
            'Keep the framework acknowledgment once at the part opener, with its bibliographic entry in F')
    # One canonical JSON bank; every published ID and answer uses the same value.
    from generate_exercise_bank import load_exercises,render
    data,_,_=load_exercises()
    for path,expected in render().items():require(path.read_text()==expected,f'Stale generated bank/review: {path}')
    expected_legacy = {f'C{group}-{i}' for group,n in ((1,18),(2,21),(3,12),(4,50)) for i in range(1,n+1)}
    require({r['legacy_id'] for r in data if r['legacy_id']}==expected_legacy,'All 101 original exercise IDs must survive the bank merge')
    require(len([r for r in data if r.get('part_review')])==18,'Nine parts need two cumulative exercises each')
    legacy={r['legacy_id']:r for r in data if r['legacy_id']}
    for name,body in combined.items():errors.extend(f'{name}: {e}' for e in visible_exercise_errors(body,[r['id'] for r in data]))
    aliases={}
    for row in data:
        for anchor in [row['id'],row['legacy_id'],*re.findall(r'\\label\{exercise:([^}]+)\}',row['question'])]:
            if anchor:aliases[anchor]=row['id']
    for name,body in combined.items():errors.extend(f'{name}: {e}' for e in exercise_link_text_errors(body,aliases))
    errors.extend(review_ownership_errors(data,(BOOK/'chapter-practice.tex').read_text()))
    errors.extend(route_caption_errors(combined['part-maps']))
    errors.extend(part_bookend_errors(main,sources))
    guard=re.search(r'\\newcommand\{\\chapterrule\}\{\\Needspace\{([.0-9]+)\\textheight\}',main)
    require(bool(guard) and float(guard[1])>=1/3,'Chapter opening guard must reserve at least one-third of a page')
    chart_font=re.search(r'\\renewcommand\{\\scriptsize\}\{\\fontsize\{([.0-9]+)\}',main)
    require(bool(chart_font) and float(chart_font[1])>=8.5,'Chart annotations must be at least 8.5 pt')
    require(main.index(r'\input{chapters/23f-foundation-recap}')>main.index(r"\partexitmemory"),'Closing recap must follow the final part')
    require('终章：回到那四个 Token' in sources['23f-foundation-recap'],'Missing final bookend')
    require('一句话本质' not in main,'Remove redundant chapter-compass label')
    require(r'\answerresult{1280}' in legacy['C4-41']['solution'],'C4-41 must include bytes, not 640 elements')
    for fragment in (r'W_{\rm up}=I_2','关闭两次 Norm',r'r=x+aXW_V',r'f=\relu(rW_{\rm up})'):
        require(fragment in legacy['C2-13']['question'],f'C2-13 simplified model contract missing: {fragment}')
    errors.extend(validate_navigation())
    # Self-check/answer bijection follows the actual learning goals of each chapter.
    ans=sources['28-chapter-checks']
    require(ans.count(r'\par\Needspace{8\baselineskip}')==len(allchecks),'Every answer heading must keep its first answer')
    for name,body in sources.items():
        for m in re.finditer(r'\\chapterchecktasks\{',body):
            slug,e=argument(body,m.end()-1);_,e=argument(body,e);questions,_=argument(body,e)
            count=len(re.findall(r'\\item\b',questions))
            require(count>0,f'{slug}: expected substantive self-check questions')
            require(questions.count(r'\chapterinlinehint{')==count,f'{slug}: source clues and questions must match')
            marker=r'\label{answer:'+slug+'}'
            require(marker in ans,f'{slug}: missing self-check answers')
            if marker in ans:
                section=ans.split(marker,1)[1].split(r'\item[',1)[0]
                ids=re.findall(r'\\answerpiece\{([^}]+)\}',section)
                require(ids==[str(i) for i in range(1,count+1)],f'{slug}: answer numbering differs from questions: {ids}')
    # Canonical glossary defines its own count; both generated indices must match.
    from generate_bilingual_glossary import generate,entries,EXTRA_REFERENCES
    require(sources['24e-bilingual-glossary'].strip()==uncomment(generate()).strip(),'Stale generated glossary')
    total=len(entries('24-lexicon.tex'))+len(entries('24b-modern-lexicon.tex'))
    require(f'全量中英对照：{total} 项' in sources['24e-bilingual-glossary'],'Glossary count must be generated')
    expected_links=sum(line.count(r'\hyperref[') for line in generate().splitlines() if ' & ' in line and r'\hyperref[' in line)
    def lookup_entries(name):
        """Each glossary row is one entry; the English lookup prints two
        (English, 中文, 页码) triples per source row."""
        found=[]
        for line in sources[name].splitlines():
            if ' & ' not in line or r'\hyperref[' not in line:
                continue
            cells=line.rstrip().removesuffix('\\\\').split(' & ')
            if name=='24f-english-index':
                # A group's first entry is prefixed by its printed initial.
                cells=[re.sub(r'^\{\\sffamily\\bfseries\\color\{blue\}[A-Z]\}\\enspace ','',c) for c in cells]
                found += [cells[i:i+3] for i in range(0,len(cells),3) if cells[i].strip()]
            else:
                found.append(cells)
        return found
    for name in ('24e-bilingual-glossary','24f-english-index'):
        rows=lookup_entries(name)
        require(len(rows)==total,f'{name}: glossary row count mismatch')
        require(all(r'\hyperref[' in ' & '.join(row) for row in rows),f'{name}: glossary entry without a link')
        require(sum(' & '.join(row).count(r'\hyperref[') for row in rows)==expected_links,f'{name}: glossary reference count mismatch')
        for target in ('concept:evaluation-contamination','concept:evaluation-contamination-benchmark','concept:autoregressive'):
            require(r'\hyperref['+target+']' in sources[name],f'{name}: missing lookup destination {target}')
    index_rows=[]
    for name in ('24e-bilingual-glossary','24f-english-index'):
        index_rows.append({tuple(sorted(row[:2])): tuple(re.findall(r'\\hyperref\[([^]]+)\]',' & '.join(row)))
                           for row in lookup_entries(name)})
    require(index_rows[0]==index_rows[1],'English and pinyin lookup destinations differ')
    for term in ('提示注入','困惑度','自回归','蒸馏','剪枝','评测污染','混合精度','BOS/EOS'):
        require(term in sources['24e-bilingual-glossary'],f'Missing glossary term {term}')
    # The reserved role colors cannot silently return to the diagrams that
    # previously confused roles with states, shortcuts, sample points and windows.
    for name,required in {'pre-norm-block':'residualcolor','causal-mask-heatmap':'maskedcolor',
                          'rnn-numeric-memory':'flowcolor','cnn-window':'windowcolor',
                          'generalization-three-fits':'noisecolor','three-position-probabilities':'datacolor'}.items():
        body = combined['figures/'+name+'.tex']
        require(required in body, f'{name}: semantic color {required} missing')
        require(not re.search(r'\b(?:orange|teal|blue)\b', body), f'{name}: Q/K/V role palette reused for another purpose')
    errors.extend(fitting_color_errors(combined['figures/generalization-three-fits.tex']))
    # Per-link UTC audit records. Accessibility is deliberately distinct from content verification.
    manifest={r['url']:r for r in json.loads((BOOK/'source-audit.json').read_text())}
    source=sources['26-sources']
    require('台北' not in source,'Source dates must use UTC')
    urls=re.findall(r'\\sourceurl\{([^}]+)\}',source)
    for url in urls:
        escaped=re.escape(url)
        m=re.search(r'\\sourceurl\{'+escaped+r'\}\s*\\sourcecheck\{(\d{4}-\d{2}-\d{2})\}\{([^}]+)\}',source)
        require(bool(m),f'Missing per-source UTC date: {url}')
        if m:
            date.fromisoformat(m[1]);require(url in manifest and manifest[url]['checked_utc']==m[1],f'Audit manifest/date mismatch: {url}')
    require(set(urls)==set(manifest),'Source audit manifest and printed URLs differ')
    for url,revision in [('openai-community/gpt2','607a30d'),('Qwen/Qwen2.5-0.5B','060db64')]:
        require(f'{url}/blob/{revision}/config.json' in source,f'Config must be pinned: {url}')
    # No screen-only navigation wording in the printable active edition.
    for name,body in combined.items():
        if re.search(r'点击题目标题|（返回正文）',body):errors.append(f'{name}: replace screen-only navigation with page references')
    for name in ('beginner_training_demo','claude_function_call_demo','context_contrast_demo','attention_selection_demo','mini_transformer_demo','cache_budget_demo','pretraining_data_demo','pytorch_starter','teaching_trace','chinese_tokenizer_demo','icl_policy_demo'):
        spelling=name.replace('_',r'\_')
        # The reproduction table lives in Appendix B beside the experiments it reruns.
        require(spelling in sources['24e-pytorch-lab'] or name in sources['24e-pytorch-lab'],f'Missing reproduction entry: {name}')
    require('易错／边界' not in sources['00g-reading-routes'],'Use one caution category in the legend')
    from check_section_navigation import section_targets,source_errors
    heading_targets=section_targets(combined)
    for name,body in combined.items():errors.extend(f'{name}: {e}' for e in source_errors(body,heading_targets))
    # Content-review dates and version evidence belong to the central manifest,
    # not repeated chapter stamps.
    from check_dated_claims import validate as validate_dated_claims
    errors.extend(validate_dated_claims())
    return errors


def self_test():
    from generate_exercise_bank import printed_regular
    rows=[dict(id='C-001',slug='first'),dict(id='C-002',slug='second')]
    assert [r['id'] for r in printed_regular(rows,{'first':'A','second':'B'})]==['C-001','C-002']
    try:printed_regular(rows,{'second':'B','first':'A'})
    except ValueError:pass
    else:raise AssertionError('Storage-contiguous IDs must not hide noncontiguous printed chapter order')
    good=r'\item \textbf{选择训练或生成}：训练见第~\ref*{intro:22c-language-training}~章；生成见第~\ref*{intro:23-llm-systems}~章。\end{enumerate}'
    assert not ten_step_errors(good)
    # Regression: every target exists, yet the roles are wrong (the old CI miss).
    assert ten_step_errors(good.replace('intro:22c-language-training','intro:23a-from-toy-to-gpt'))
    assert ten_step_errors(good.replace('intro:23-llm-systems','intro:22c-language-training'))
    assert not notation_errors(r'\widehat{y}_i+\Pi_{1,4}')
    for bad in (r'\vect a^\top\cdot\vect b^\top',r'\vect{q}_i^\top\cdot\vect{k}_j^\top',
                r'\|\vect a^\top\|',r'\|\vect{k}^\top\|^2'):
        assert notation_errors(bad),bad
    for good in (r'\vect a^\top\vect b',r'\|\vect{k}\|^2',r'\|\vect k_t^\top\mathcal{M}-\vect v_t^\top\|^2'):
        assert not notation_errors(good),good
    assert notation_errors(r'L=-\log p') and not notation_errors(r'L=-\ln p')
    for bad in (r'\widehat y',r'\widehat{P}',r'\widehat{y\approx0}',r'W_{\rm vocab}',r'A^{(\ell)}',r'\to L:T\times|\mathcal V|'):
        assert notation_errors(bad),bad
    assert not notation_errors('Best-of-$n$') and notation_errors('Best-of-$N$')
    assert notation_errors(r'\nolinkurl{python3 scripts/example.py}')
    assert not ending_order_errors(r'\chapterchecktasks{x}{}{}\begin{conclusion}')
    assert ending_order_errors(r'\begin{conclusion}x\end{conclusion}\chapterchecktasks{x}{}{}')
    good_anchor=r'\subsection{Definition}\phantomsection\label{concept:test}'
    assert not concept_anchor_errors(good_anchor,'concept:test','Definition')
    assert concept_anchor_errors(good_anchor.replace(r'\phantomsection',r'\begin{enumerate}\item '),'concept:test','Definition')
    assert concept_anchor_errors(good_anchor.replace('Definition','Next section'),'concept:test','Definition')
    fitting=r'\fill[noisecolor] \draw[flowcolor,very thick] 黑点是带测量噪声的训练样本，蓝灰线'
    assert not fitting_color_errors(fitting)
    assert fitting_color_errors(fitting.replace('黑点','橙点'))
    assert fitting_color_errors(fitting.replace('noisecolor','orange'))
    assert not visible_exercise_errors(r'\label{exercise:C2-21}\hyperref[exercise:C2-21]{C-045}', {'C-045'})
    for old in ('C2-21','C3-12','C1-17、C1-18','做C2-21题'):
        assert visible_exercise_errors(r'\hyperref[exercise:valid]{附录 C 的 '+old+'}')
    assert visible_exercise_errors('C-999', {'C-001'})
    assert visible_exercise_errors('做C-999题', {'C-001'})
    assert not exercise_link_text_errors(r'\hyperref[exercise:alias]{C-001}',{'alias':'C-001'})
    assert exercise_link_text_errors(r'\hyperref[exercise:alias]{C-002}',{'alias':'C-001'})
    reviews=[{'id':f'R-{i:02d}','part_review':'learning'} for i in range(1,19)]
    assert not review_ownership_errors(reviews,'C-001')
    assert review_ownership_errors(reviews,'C-001、R-01')
    assert not route_caption_errors(r'\tagstructbegin{tag=Caption}')
    assert route_caption_errors(r'\captionof{figure}{全书路线}')
    book=('\\input{chapters/00-guide}\n\\part{A}\\label{part:context}\n\\partentrycontext\n\\input{chapters/21a}\n\\partexitcontext\n'
          '\\part{B}\\label{part:transformer}\n\\partentrytransformer\n\\input{chapters/22b}\n\\partexittransformer\n')
    taught={'21a':r'\label{partq:context}','22b':r'\label{partq:transformer}'}
    assert not part_bookend_errors(book,taught)
    # The answer to Part 5's question may not be taught in Part 4.
    assert part_bookend_errors(book,{'21a':r'\label{partq:context}\label{partq:transformer}','22b':''})
    assert part_bookend_errors(book.replace('\\partexittransformer','\\partexitcontext'),taught)
    assert part_bookend_errors(book.replace('\\input{chapters/00-guide}\n','')+'\\input{chapters/00-guide}\n',taught)
    opener='参数／是否训练：'+('这是连续的正文内容'*5)
    assert not chapter_opening_errors(740,842,opener)
    assert chapter_opening_errors(180,842,opener)
    assert chapter_opening_errors(740,842,'参数／是否训练：冻结权重')
    assert chapter_opening_errors(740,842,'参数／是否训练：'+('参数说明'*10),50)
    assert not chapter_opening_errors(740,842,'正文内容'*20,10)
    assert chapter_opening_errors(740,842,'只有章标题',5)
    print('Book contract regressions passed: chapter roles, notation, figure colors, printed exercise IDs, review ownership, map captions, part bookends and chapter openings')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--self-test',action='store_true');args=p.parse_args()
    if args.self_test:self_test();return
    errors=validate_contract()
    if errors:raise SystemExit('\n'.join('CONTRACT ERROR: '+e for e in errors))
    print(f'Book source contract passed: {CHAPTER_COUNT} chapters, unique self-checks, unified bank, notation and dated sources')


if __name__=='__main__':main()
