#!/usr/bin/env python3
"""Generate chapter C questions and independent cumulative R questions from JSON."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
from generate_chapter_navigation import lesson_metadata
ROOT=Path(__file__).resolve().parents[1]
BOOK=ROOT/'book'
PARTS=('learning','matrices','tokens','context','transformer','assistant','architecture','vision','memory')
PART_NAMES=('学习','矩阵','文字','上下文','Transformer','助手','架构','视觉','联想记忆')

def validate_keys(data):
    """Semantic keys survive printed renumbering; retired fields must not return."""
    keys=[r.get('key','') for r in data]
    if any(not re.fullmatch(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)+',key) for key in keys):
        raise ValueError('Every exercise needs a stable semantic key')
    if len(set(keys))!=len(keys):raise ValueError('Duplicate exercise keys')
    if any({'legacy_id','legacy_answer_anchor'} & r.keys() for r in data):
        raise ValueError('Retired exercise ID fields must not return')

def validate_progression(data,chapter_slugs):
    """Readers meet a basic task before longer calculations and transfer tasks."""
    levels={'基础':0,'标准':1,'挑战':2}
    for slug in chapter_slugs:
        rows=[r for r in data if r['slug']==slug and not r.get('part_review')]
        if not any(r['difficulty']=='基础' for r in rows):
            raise ValueError(f'{slug}: chapter and optimizer practice need a basic entry exercise')
    groups={r['slug'] for r in data if not r.get('part_review')}
    for slug in groups:
        values=[levels[r['difficulty']] for r in data if r['slug']==slug]
        if values!=sorted(values):raise ValueError(f'{slug}: use 基础 → 标准 → 挑战 order')

def load_exercises():
    data=json.loads((BOOK/'exercises.json').read_text())
    validate_keys(data)
    ids=[r['id'] for r in data]
    if len(set(ids))!=len(ids):raise ValueError('Duplicate exercise IDs')
    for prefix,items,width in [('C',[r for r in data if not r.get('part_review')],3),('R',[r for r in data if r.get('part_review')],2)]:
        if [r['id'] for r in items]!=[f'{prefix}-{i:0{width}d}' for i in range(1,len(items)+1)]:
            raise ValueError(f'{prefix} exercise numbering must be contiguous and independent')
    owners,titles=lesson_metadata();primary={}
    for label,slug in owners.items():
        if label.startswith('intro:'):primary.setdefault(slug,label)
    for r in data:
        if r['slug'] in primary and r['owner']!=primary[r['slug']]:raise ValueError(f"{r['id']}: chapter metadata points to a subsection")
        expected=('review:'+r['part_review'] if r.get('part_review') and r['owner']=='part:'+r['part_review'] else
                  owners.get(r['owner'],'optimizer-details' if r['owner']=='app:optimizer-details' else None))
        if expected!=r['slug']:raise ValueError(f"{r['id']}: wrong ownership")
        if r['difficulty'] not in ('基础','标准','挑战') or not 1<=r['minutes']<=60:raise ValueError(f"{r['id']}: invalid difficulty/time")
        if any(ord(c)<32 and c!='\n' for key in ('question','solution') for c in r[key]):raise ValueError(f"{r['id']}: control character")
        if not r['question'] or r['solution'].count(r'\textbf{第一步：}')!=1:raise ValueError(f"{r['id']}: missing first step/solution")
        if not re.search(r'\\textbf\{(?:解答|解题过程)：\}',r['solution']) or re.search(r'完整解答|\\small',r['solution']):
            raise ValueError(f"{r['id']}: answer label must be 解答 or 解题过程, without legacy size/label variants")
        if re.search(r'\\\][。，]',r['solution']+r['question']):raise ValueError(f"{r['id']}: display math followed by orphan punctuation")
        if re.search(r'(?<!-)--(?=[A-Za-z])',r['solution']+r['question']):raise ValueError(f"{r['id']}: write command-line flags as -{{}}-flag to avoid the TeX en-dash ligature")
        step=re.search(r'\\textbf\{第一步：\}(.*?)\\textbf\{(?:解答|解题过程)：\}(\s*\\textbf\{[^}]*：\})?',r['solution'],re.S)
        if not step or not step[1].rstrip().endswith(r'\par\nobreak') or step[2]:
            raise ValueError(f"{r['id']}: first step must end with \\par\\nobreak before one answer label")
        if r.get('part_review') and (r['part_review'] not in PARTS or not r.get('review_prompt')):raise ValueError(f"{r['id']}: missing review prompt/part")
    validate_progression(data,(set(titles)-{'00-guide'})|{'optimizer-details'})
    by_key={r['key']:r for r in data}
    for part in PARTS:
        reviews=[r for r in data if r.get('part_review')==part]
        warmup=by_key.get(reviews[0].get('warmup_key')) if reviews else None
        if not warmup or warmup['difficulty']!='基础' or warmup.get('part_review'):
            raise ValueError(f'{part}: first cumulative review needs a basic C exercise link')
    printed_regular(data,titles)
    return data,owners,titles

def printed_regular(data,titles):
    """Validate the order readers actually see, after grouping by real chapters."""
    order={slug:i for i,slug in enumerate(titles)}
    rows=sorted([r for r in data if not r.get('part_review')],key=lambda r:(order.get(r['slug'],999),r['id']))
    if [r['id'] for r in rows]!=[f'C-{i:03d}' for i in range(1,len(rows)+1)]:
        raise ValueError('Printed chapter exercise numbers must be contiguous after chapter sorting')
    return rows


def group_heading(row, titles):
    """One entry per chapter/part: the chapter number, title and body page live here."""
    review=row.get('part_review')
    if review:
        return '累积复习 · '+PART_NAMES[PARTS.index(review)], r'本部分第~\pageref*{part:'+review+r'}~页起'
    if row['slug']=='optimizer-details':
        return '附录 A · 优化器', r'正文第~\pageref*{app:optimizer-details}~页'
    if row['slug']=='00-guide':
        return '序章', r'自测第~\pageref*{check:00-guide}~页'
    return r'第~\ref*{'+row['owner']+r'}~章 · '+titles[row['slug']], r'正文第~\pageref*{'+row['owner']+r'}~页'

def linked_solution(row):
    """The first-step label links back to its question; no per-item page line is printed."""
    marker=r'\textbf{第一步：}'
    body=row['solution'].replace(marker,r'\hyperref[exercise:'+row['key']+r']{'+marker+'}',1)
    # Short runnable programs stay together; the preceding nobreak keeps their lead-in.
    return body.replace(r'\begin{verbatim}',r'\begin{samepage}\begin{verbatim}').replace(
        r'\end{verbatim}',r'\end{verbatim}\end{samepage}')

def render():
    data,owners,titles=load_exercises();order={slug:i for i,slug in enumerate(titles)}
    regular=printed_regular(data,titles)
    cumulative=[r for r in data if r.get('part_review')]
    question=[r'% Generated by scripts/generate_exercise_bank.py; edit book/exercises.json.',
              r'\subsection{按章练习与累积复习：C、R 两种任务}',r'\label{app:exercise-bank}',
              'C 题按章排列；R 题按部分排列，连接多个章节，不计入末章题号。',
              '章内按“基础、标准、挑战”排列，同档内按知识依赖排序。初读先做基础题；标准题用于完整计算与迁移；挑战题及扩展路径按需完成。R 题保留综合任务，每部分先给出一道基础热身题入口。预计耗时是逐题估计，不是要求连续完成的学习时长。',
              r'各组标题给出章号与正文页码；每题标明解答页码、难度和预计耗时。两类题的第一步和解答均在附录 D.1，第~\pageref*{app:answers}~页起。']
    answer=[r'% Generated by scripts/generate_exercise_bank.py; edit book/exercises.json.',
            r'\subsection{按章练习与累积复习参考答案}',r'\phantomsection\label{app:answers}',
            '先遮住解题过程，只读第一步；独立完成后再核对结果、单位与形状。各组标题给出题目起始页，电子版点击“第一步”可回到原题。']
    current=None
    for row in regular+cumulative:
        review=row.get('part_review');slug=('review:'+review) if review else row['slug'];identifier=row['id']
        if current!=slug:
            if current is not None:question.append(r'\end{enumerate}');answer.append(r'\end{enumerate}')
            title,entry=group_heading(row,titles)
            first=r'\hyperref[exercise:'+identifier+r']{题目见第~\pageref*{exercise:'+identifier+r'}~页起}'
            question += [r'\Needspace{6\baselineskip}',r'\subsubsection*{'+title+r'\enspace{\mdseries\footnotesize（'+entry+r'）}}',
                         r'\begin{enumerate}[label={},leftmargin=4.8em,itemsep=4pt]']
            answer += [r'\Needspace{6\baselineskip}',r'\subsubsection*{'+title+r'\enspace{\mdseries\footnotesize（'+first+r'）}}',
                       r'\begin{enumerate}[label={},leftmargin=4.8em,itemsep=4pt]'];current=slug
        alias=r'\label{exercise:'+row['key']+'}'
        meta=r'\hyperref[solution:'+identifier+r']{解答第~\pageref*{solution:'+identifier+r'}~页}'
        # Start the item paragraph before placing anchors: a vertical-mode
        # phantomsection can stay on the previous page when the first line moves.
        question += [r'\item[\textbf{'+identifier+r'.}] \leavevmode\phantomsection\label{exercise:'+identifier+'}'+alias+r'\exercisemeta{'+row['difficulty']+'}{'+str(row['minutes'])+'}{'+meta+'}'+row['question']]
        if row.get('warmup_key'):
            warmup=next(r for r in regular if r['key']==row['warmup_key'])
            question[-1]+=r'\par 可先做\hyperref[exercise:'+warmup['key']+r']{基础热身 '+warmup['id']+r'}。'
        answer += [r'\item[\textbf{'+identifier+r'.}] \leavevmode\phantomsection\label{solution:'+identifier+r'}\label{solution:'+row['key']+'}'+linked_solution(row)]
    question.append(r'\end{enumerate}');answer.append(r'\end{enumerate}')
    reviews=[r'% Generated by scripts/generate_exercise_bank.py; edit book/exercises.json.']
    for part in PARTS:
        selected=[r for r in cumulative if r['part_review']==part]
        if len(selected)!=2:raise ValueError(f'{part}: expected two cumulative reviews')
        reviews += [r'\newcommand{\partreview'+part+r'}{\par\Needspace{3\baselineskip}\begingroup\small\linespread{1.06}\selectfont\setlength{\parskip}{1pt}',r'\noindent{\sffamily\bfseries 本部分累积复习}\par\nobreak']
        warmup=next(r for r in regular if r['key']==selected[0]['warmup_key'])
        reviews += [r'\noindent 可先做\hyperref[exercise:'+warmup['key']+r']{基础热身 '+warmup['id']+r'}，再连接本部分的多个步骤。\par']
        for row in selected:reviews += [r'\noindent\textbf{'+row['id']+r'.} '+row['review_prompt']+r' \hyperref[solution:'+row['id']+r']{（解答：第~\pageref*{solution:'+row['id']+r'}~页）}\par']
        reviews += [r'\endgroup}']
    return {BOOK/'part-reviews.tex':'\n'.join(reviews)+'\n',BOOK/'chapters/25-exercise-bank.tex':'\n'.join(question)+'\n',BOOK/'chapters/27-answer-key.tex':'\n'.join(answer)+'\n'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args()
    for path,text in render().items():
        if args.check:
            if not path.exists() or path.read_text()!=text:raise SystemExit(f'Stale exercise output: {path}')
        else:path.write_text(text)
    data,_,_=load_exercises();print(f'Exercise bank QA: {len(data)-18} chapter C questions + 18 independent R reviews; one linked first step and one answer label each')
if __name__=='__main__':main()
