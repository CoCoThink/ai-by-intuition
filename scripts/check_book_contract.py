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
    '让词与词交换信息','组装并训练 Transformer','换一种数据看 Transformer：从 CNN 到 ViT',
    '从语言模型到助手','架构为什么在变，往哪走','联想记忆与线性状态']
CHAPTER_COUNT=41


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
    if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]',body):errors.append('Control character in TeX')
    return errors


def validate_contract():
    errors=[]
    main,sources=read_sources()
    def require(condition,message):
        if not condition:errors.append(message)
    require(re.findall(r'\\part\{([^}]+)\}',main)==PART_TITLES,'Nine-part curriculum order changed')
    groups=core_groups()
    require(sum(g['numbered'] for g in groups)==CHAPTER_COUNT,'Expected 41 numbered chapters')
    for g in groups:require(len(g['checks'])==1,f"{g['title']}: needs one self-check, found {g['checks']}")
    require(len(groups)==CHAPTER_COUNT+1,'One unnumbered prelude must have a self-check')
    allchecks=[slug for g in groups for slug in g['checks']]
    require(len(set(allchecks))==len(allchecks),'Repeated self-check slug')
    require('阅读指南' not in main and '阅读指南' not in sources['20b-task-contract'],'Prelude must be called 序章')
    errors.extend(ten_step_errors(sources['22-transformer-architecture']))
    combined={'main':main,**sources,'part-maps':(BOOK/'part-maps.tex').read_text(),
              'part-reviews':(BOOK/'part-reviews.tex').read_text()}
    for p in (BOOK/'figures').glob('*.tex'):combined['figures/'+p.name]=uncomment(p.read_text())
    for name,body in combined.items():errors.extend(f'{name}: {e}' for e in notation_errors(body))
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
            '训练资料从哪里来' in sources['23a-from-toy-to-gpt'],'Data cleaning must be outside ICL chapter')
    require('推理模型与测试时计算' not in sources['23c-post-training'] and
            'intro:23cc-test-time-compute' in sources['23cc-test-time-compute'],'Test-time compute needs an independent chapter')
    for marker in ('concept:bos-eos','concept:prefill-decode','concept:autoregressive'):
        require(marker in sources['23-llm-systems'],f'Missing generation interface: {marker}')
    require('concept:chat-template' in sources['23c-post-training'],'Chat template explanation missing')
    require('12{,}288' in sources['22d-modern-transformers'] and '402{,}653{,}184' in sources['22d-modern-transformers'],'Real KV byte estimate missing')
    for fragment in ('P_{\\rm pos}',r'\Pi',r'W_{\rm out}',r'\mathcal{M}',r'N_{\rm layer}'):
        require(fragment in sources['00c-symbols'],f'Symbol table missing {fragment}')
    # One canonical JSON bank; every published ID and answer uses the same value.
    from generate_exercise_bank import load_exercises,render
    data,_,_=load_exercises()
    for path,expected in render().items():require(path.read_text()==expected,f'Stale generated bank/review: {path}')
    expected_legacy = {f'C{group}-{i}' for group,n in ((1,18),(2,21),(3,12),(4,50)) for i in range(1,n+1)}
    require({r['legacy_id'] for r in data if r['legacy_id']}==expected_legacy,'All 101 original exercise IDs must survive the bank merge')
    require(len([r for r in data if r.get('part_review')])==18,'Nine parts need two cumulative exercises each')
    legacy={r['legacy_id']:r for r in data if r['legacy_id']}
    require(r'\answerresult{1280}' in legacy['C4-41']['solution'],'C4-41 must include bytes, not 640 elements')
    for fragment in (r'W_{\rm up}=I_2','关闭两次 Norm',r'r=x+aXW_V',r'f=\relu(rW_{\rm up})'):
        require(fragment in legacy['C2-13']['question'],f'C2-13 simplified model contract missing: {fragment}')
    errors.extend(validate_navigation())
    # Self-check/answer bijection including the four merged six-question groups.
    ans=sources['28-chapter-checks']
    require(ans.count(r'\par\Needspace{8\baselineskip}')==len(allchecks),'Every answer heading must keep its first answer')
    for name,body in sources.items():
        for m in re.finditer(r'\\chapterchecktasks\{',body):
            slug,e=argument(body,m.end()-1);_,e=argument(body,e);questions,_=argument(body,e)
            count=len(re.findall(r'\\item\b',questions))
            require(count in (3,6),f'{slug}: expected 3 or 6 substantive self-checks')
            require(questions.count(r'\chapterinlinehint{')==count,f'{slug}: source clues and questions must match')
            marker=r'\label{answer:'+slug+'}'
            require(marker in ans,f'{slug}: missing self-check answers')
            if marker in ans:
                section=ans.split(marker,1)[1].split(r'\item[',1)[0]
                ids=re.findall(r'\\answerpiece\{([^}]+)\}',section)
                require(ids==[str(i) for i in range(1,count+1)],f'{slug}: answer numbering differs from questions: {ids}')
    # Canonical glossary defines its own count; both generated indices must match.
    from generate_bilingual_glossary import generate,entries
    require(sources['24e-bilingual-glossary'].strip()==uncomment(generate()).strip(),'Stale generated glossary')
    total=len(entries('24-lexicon.tex'))+len(entries('24b-modern-lexicon.tex'))
    require(f'全量中英对照：{total} 项' in sources['24e-bilingual-glossary'],'Glossary count must be generated')
    require(sources['24e-bilingual-glossary'].count(r'\hyperref[')==total,'Glossary row count mismatch')
    require(sources['24f-chinese-index'].count(r'\hyperref[')==total,'Pinyin row count mismatch')
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
    for name in ('context_contrast_demo','mini_transformer_demo','cache_budget_demo','pretraining_data_demo','pytorch_starter','teaching_trace'):
        spelling=name.replace('_',r'\_')
        require(spelling in sources['29-revision-notes'] or name in sources['29-revision-notes'],f'Missing reproduction entry: {name}')
    return errors


def self_test():
    good=r'\item \textbf{选择训练或生成}：训练见第~\ref*{intro:22c-language-training}~章；生成见第~\ref*{intro:23-llm-systems}~章。\end{enumerate}'
    assert not ten_step_errors(good)
    # Regression: every target exists, yet the roles are wrong (the old CI miss).
    assert ten_step_errors(good.replace('intro:22c-language-training','intro:23a-from-toy-to-gpt'))
    assert ten_step_errors(good.replace('intro:23-llm-systems','intro:22c-language-training'))
    assert not notation_errors(r'\widehat{y}_i+\Pi_{1,4}')
    for bad in (r'\widehat y',r'\widehat{P}',r'\widehat{y\approx0}',r'W_{\rm vocab}',r'A^{(\ell)}',r'\to L:T\times|\mathcal V|'):
        assert notation_errors(bad),bad
    print('Book contract regression tests: valid-but-wrong chapter roles, accent scope, notation conflicts rejected')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--self-test',action='store_true');args=p.parse_args()
    if args.self_test:self_test();return
    errors=validate_contract()
    if errors:raise SystemExit('\n'.join('CONTRACT ERROR: '+e for e in errors))
    print('Book source contract passed: 41 chapters, unique self-checks, unified bank, notation and dated sources')


if __name__=='__main__':main()
