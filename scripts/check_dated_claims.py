#!/usr/bin/env python3
"""Generate the dated assertion register; reject stale MCP versions and wire data.

Content review dates are entered by a reviewer, never copied from the build clock.
--online additionally compares the official current MCP redirect with our version.
--check-due rejects overdue reviews without preventing offline historical builds.
"""
from __future__ import annotations
import argparse
import copy
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
BOOK=ROOT/'book'
BEGIN='% BEGIN GENERATED DATED CLAIMS'
END='% END GENERATED DATED CLAIMS'
OUTPUT=BOOK/'chapters/29-revision-notes.tex'
PREFIX='https://modelcontextprotocol.io/specification/'


def load_claims():
    return json.loads((BOOK/'dated-claims.json').read_text())


def request_errors(request, version):
    errors=[]
    if request.get('jsonrpc')!='2.0' or request.get('method')!='tools/call':
        errors.append('MCP example must be a tools/call JSON-RPC request')
    if type(request.get('id')) not in (str,int):
        errors.append('MCP request ID must be a string or integer')
    params=request.get('params',{})
    meta=params.get('_meta',{})
    if meta.get('io.modelcontextprotocol/protocolVersion')!=version:
        errors.append('MCP version belongs in params._meta and must match the reviewed revision')
    if not isinstance(meta.get('io.modelcontextprotocol/clientCapabilities'),dict):
        errors.append('MCP request must declare clientCapabilities, even when empty')
    if not isinstance(params.get('arguments'),dict) or not isinstance(params.get('name'),str) or not params['name']:
        errors.append('MCP tool name and arguments required')
    if 'io.modelcontextprotocol/clientInfo' in meta:
        info=meta['io.modelcontextprotocol/clientInfo']
        if not isinstance(info,dict) or not all(isinstance(info.get(k),str) for k in ('name','version')):
            errors.append('MCP clientInfo needs a name and version')
    return errors


def manifest_errors(rows, audit, labels):
    errors=[];seen=set()
    for row in rows:
        ident=row['id']
        if ident in seen:errors.append(f'Duplicate dated assertion: {ident}')
        seen.add(ident)
        try: reviewed=date.fromisoformat(row['checked_utc'])
        except ValueError:
            errors.append(f'Invalid UTC date: {ident}');continue
        if reviewed>datetime.now(timezone.utc).date():errors.append(f'Future content review date: {ident}')
        interval=row.get('review_interval_days')
        if type(interval) is not int or not 1<=interval<=90:
            errors.append(f'Review interval must be an integer from 1 to 90 days: {ident}')
        if row.get('review_on_new_revision') is not True:
            errors.append(f'New revisions must trigger a review: {ident}')
        if row['target'] not in labels:errors.append(f'Unknown assertion destination: {ident}')
        if not row['claim'] or not row['scope'] or not row['sources']:
            errors.append(f'Assertion needs a claim, review scope and primary sources: {ident}')
        for source in row['sources']:
            record=audit.get(source['url'])
            if not record or record['checked_utc']<row['checked_utc']:
                errors.append(f'Missing or older source record for {ident}: {source["url"]}')
            elif 'accessibility only' in record['method']:
                errors.append(f'Link accessibility is not content verification: {ident}')
    mcp=next((r for r in rows if r['id']=='mcp'),None)
    if mcp is None:errors.append('Missing MCP assertion')
    else:
        for source in mcp['sources']:
            if not source['url'].startswith(PREFIX+mcp['version']+'/'):
                errors.append('MCP sources must pin the reviewed protocol version')
    return errors


def target_region(sources, label):
    """Source text owned by a label: up to the next chapter heading for chapter
    targets (intro:...), otherwise up to the next section or subsection."""
    for text in sources.values():
        start=text.find(r'\label{'+label+'}')
        if start<0:continue
        stop=re.compile(r'\\section\*?\{' if label.startswith('intro:') else r'\\(?:sub)?section\*?\{')
        end=stop.search(text,start+1)
        return re.sub(r'\s+',' ',text[start:end.start() if end else len(text)])
    return None


def evidence_errors(rows, sources):
    """A valid label is not enough: the claimed facts must be printed where the
    table points. This caught a claim about DeepSeek CED and Qwen3 whose target
    was a chapter that mentioned neither."""
    errors=[]
    for row in rows:
        evidence=row.get('evidence')
        if not evidence or not all(isinstance(e,str) and e.strip() for e in evidence):
            errors.append(f"Assertion needs literal evidence strings: {row['id']}");continue
        region=target_region(sources,row['target'])
        if region is None:continue  # unknown targets are reported by manifest_errors
        for item in evidence:
            if re.sub(r'\s+',' ',item) not in region:
                errors.append(f"Evidence {item!r} for {row['id']} is not printed at {row['target']}")
    return errors


def review_due_errors(rows, today=None):
    today=datetime.now(timezone.utc).date() if today is None else today
    errors=[]
    for row in rows:
        due=date.fromisoformat(row['checked_utc'])+timedelta(days=row['review_interval_days'])
        if today>=due:
            errors.append(f'Content review due for {row["id"]}: last reviewed {row["checked_utc"]}, '
                          f'due {due.isoformat()} (UTC); review the sources and claim before updating the date')
    return errors


def mcp_page_errors(pages):
    """The lead-in belongs to the same unbreakable box as its complete request."""
    compact=[re.sub(r'\s+','',p) for p in pages]
    intro=[i+1 for i,p in enumerate(compact) if '下面假定已发现获授权的报表工具：' in p]
    markers=('"jsonrpc":"2.0"', '"io.modelcontextprotocol/protocolVersion"',
             '"io.modelcontextprotocol/clientCapabilities":{}}}}')
    request=[[i+1 for i,p in enumerate(compact) if marker in p] for marker in markers]
    if len(intro)!=1 or any(found!=intro for found in request):
        return [f'MCP lead-in and complete JSON request must share one page: intro={intro}, request={request}']
    return []


def rendered(rows):
    """Reader table; a shared review cycle is stated once instead of on every row."""
    cycles={(r['review_interval_days'],r['review_on_new_revision']) for r in rows}
    shared=len(cycles)==1
    if shared:
        days=next(iter(cycles))[0]
        cycle=f'每条断言均在 {days} 天内或新修订发布时复查，以先到者为准；重新编译不会刷新核验日期。'
        columns=r'@{}>{\raggedright\arraybackslash}p{50mm}>{\raggedright\arraybackslash}p{26mm}>{\raggedright\arraybackslash}p{80mm}@{}'
        header=r'\toprule 断言与正文位置 & 版本／核验日（UTC） & 来源与核验范围\\\midrule'
    else:
        cycle='每行注明复查周期，以周期与新修订发布先到者为准；重新编译不会刷新核验日期。'
        columns=r'@{}>{\raggedright\arraybackslash}p{43mm}>{\raggedright\arraybackslash}p{26mm}>{\raggedright\arraybackslash}p{62mm}>{\raggedright\arraybackslash}p{25mm}@{}'
        header=r'\toprule 断言与正文位置 & 版本／核验日（UTC） & 来源与核验范围 & 建议复查周期\\\midrule'
    lines=[BEGIN,r'\subsubsection*{带日期断言清单}',r'\phantomsection\label{app:dated-claims}',
        '下表列出带日期的断言：所用版本、内容核验日（UTC）与核验范围；来源均列于附录 F。',
        cycle,
        r'\begingroup\small\setlength{\tabcolsep}{3pt}\renewcommand{\arraystretch}{1.25}',
        r'\tagpdfsetup{table/header-rows={1}}',
        r'\begin{longtable}{'+columns+'}',
        header,r'\endfirsthead',header,
        r'\endhead',r'\bottomrule\endfoot']
    for row in rows:
        target=row['target']
        entry=row['claim']+r'（\hyperref['+target+r']{第~\pageref*{'+target+r'}~页}）'
        sources='、'.join(r'\href{'+s['url']+'}{'+s['name']+'}' for s in row['sources'])
        line=entry+' & '+row['version']+r'\newline '+row['checked_utc']+' & '+sources+'。'+row['scope']
        lines.append(line+(r'\\' if shared else ' & '+str(row['review_interval_days'])+r' 天／新修订\\'))
    lines += [r'\end{longtable}\endgroup',END]
    return '\n'.join(lines)


def validate():
    rows=load_claims()
    sources='\n'.join(p.read_text() for p in (BOOK/'chapters').glob('*.tex'))
    labels=set(re.findall(r'\\label\{([^}]+)\}',sources))
    audit={r['url']:r for r in json.loads((BOOK/'source-audit.json').read_text())}
    errors=manifest_errors(rows,audit,labels)
    errors.extend(evidence_errors(rows,{p.name:p.read_text() for p in (BOOK/'chapters').glob('*.tex')}))
    expected=rendered(rows)
    if expected not in OUTPUT.read_text():errors.append('Dated assertion table is stale; run check_dated_claims.py --write')
    mcp=next(r for r in rows if r['id']=='mcp')
    chapter=(BOOK/'chapters/23d-agent-protocols.tex').read_text()
    declaration=re.search(r'以下按 MCP (\d{4}-\d{2}-\d{2}) 版',chapter)
    if not declaration or declaration[1]!=mcp['version']:
        errors.append('The prose MCP version differs from the reviewed request/source version')
    blocks=re.findall(r'\\begin\{Verbatim\}[^\n]*\n(.*?)\\end\{Verbatim\}',chapter,re.S)
    requests=[json.loads(block) for block in blocks if '"jsonrpc"' in block]
    if len(requests)!=1:errors.append('Expected one complete modern MCP request')
    for request in requests:errors.extend(request_errors(request,mcp['version']))
    if '省略了初始化' in chapter:errors.append('Modern MCP has no initialization to omit')
    main=(BOOK/'main.tex').read_text()
    if '接口、配置与实现记录按本日期核验' in main:
        errors.append('A build-wide date cannot stand in for individual content reviews')
    return errors


def current_version_errors(url, version):
    match=re.fullmatch(re.escape(PREFIX)+r'(\d{4}-\d{2}-\d{2})/?',url)
    if not match:return [f'Official current MCP entry no longer resolves to a dated revision: {url}']
    if match[1]!=version:
        return [f'MCP official current version is {match[1]}, reviewed book version is {version}; review the new specification and update the dated register']
    return []


def self_test():
    rows=load_claims();version=next(r for r in rows if r['id']=='mcp')['version']
    request={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'read_reports','arguments':{},'_meta':{
        'io.modelcontextprotocol/protocolVersion':version,'io.modelcontextprotocol/clientCapabilities':{}}}}
    assert not request_errors(request,version)
    for key in ('io.modelcontextprotocol/protocolVersion','io.modelcontextprotocol/clientCapabilities'):
        broken=copy.deepcopy(request);broken['params']['_meta'].pop(key)
        assert request_errors(broken,version)
    broken=copy.deepcopy(request);broken['_meta']=broken['params'].pop('_meta')
    assert request_errors(broken,version)
    assert request_errors(request,'2025-06-18')
    assert not current_version_errors(PREFIX+version,version)
    assert current_version_errors(PREFIX+'2025-11-25',version)
    assert current_version_errors('https://example.com/',version)
    audit={s['url']:{'checked_utc':r['checked_utc'],'method':'Content review'} for r in rows for s in r['sources']}
    labels={r['target'] for r in rows}
    assert not manifest_errors(rows,audit,labels)
    broken=copy.deepcopy(audit);broken[rows[0]['sources'][0]['url']]['method']='HTTP GET; link accessibility only'
    assert manifest_errors(rows,broken,labels)
    assert manifest_errors(rows,{},labels)
    broken=copy.deepcopy(rows);broken[0]['version']='2025-06-18'
    assert manifest_errors(broken,audit,labels)
    for key,value in (('review_interval_days',0),('review_interval_days',91),
                      ('review_interval_days',True),('review_on_new_revision',False)):
        broken=copy.deepcopy(rows);broken[0][key]=value
        assert manifest_errors(broken,audit,labels)
    sources={'a.tex':'\\section{A}\\label{intro:a}正文 768。\\subsection{X}\\label{concept:x}有 $20$ 层。\\subsection{Y}另有 Qwen3。\\section{B}\\label{intro:b}无关。'}
    claim=lambda target,evidence:[{'id':'e','target':target,'evidence':evidence}]
    assert not evidence_errors(claim('concept:x',['$20$ 层']),sources)
    assert not evidence_errors(claim('intro:a',['768','Qwen3']),sources)
    assert evidence_errors(claim('concept:x',['Qwen3']),sources)   # later subsection
    assert evidence_errors(claim('intro:b',['768']),sources)       # wrong chapter
    assert evidence_errors(claim('intro:a',[]),sources)
    fixture=[{'id':'dated-fixture','checked_utc':'2026-10-25','review_interval_days':90}]
    assert not review_due_errors(fixture,date(2027,1,22))
    assert review_due_errors(fixture,date(2027,1,23))
    assert review_due_errors(fixture,date(2027,2,1))
    intro='下面假定已发现获授权的报表工具：'
    request='"jsonrpc":"2.0", "io.modelcontextprotocol/protocolVersion": "'+version+'", "io.modelcontextprotocol/clientCapabilities":{}}}}'
    assert not mcp_page_errors([intro+'\n'+request])
    assert mcp_page_errors([intro,request])
    assert mcp_page_errors([request])
    assert mcp_page_errors([intro+'\n'+request.split('clientCapabilities')[0], 'clientCapabilities'+request.split('clientCapabilities')[1]])
    print('Dated assertion regression tests passed: version/metadata, link-only evidence, claims missing at their target, invalid or overdue reviews and split MCP lead-in rejected')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--online',action='store_true')
    parser.add_argument('--check-due',action='store_true')
    args=parser.parse_args()
    if args.write:
        text=OUTPUT.read_text();table=rendered(load_claims())
        if BEGIN in text:text=re.sub(re.escape(BEGIN)+'.*?'+re.escape(END),lambda _:table,text,flags=re.S)
        else:text=text.replace(r'\subsubsection*{从可复算的例子开始}',table+'\n\n'+r'\subsubsection*{从可复算的例子开始}')
        OUTPUT.write_text(text)
    if args.self_test:self_test()
    errors=validate()
    if args.check_due and not errors:
        errors.extend(review_due_errors(load_claims()))
    if args.online:
        version=next(r for r in load_claims() if r['id']=='mcp')['version']
        req=Request(PREFIX.rstrip('/'),headers={'User-Agent':'ai-by-intuition-source-audit/1.0'})
        with urlopen(req,timeout=30) as response:
            errors.extend(current_version_errors(response.geturl(),version))
        print(f'Official current MCP revision compared with reviewed {version}')
    if errors:raise SystemExit('\n'.join(errors))
    print(f'Dated assertion QA passed: {len(load_claims())} content review records, matching printed table and MCP request')


if __name__=='__main__':main()
