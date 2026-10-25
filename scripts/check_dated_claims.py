#!/usr/bin/env python3
"""Generate the dated assertion register; reject stale MCP versions and wire data.

Content review dates are entered by a reviewer, never copied from the build clock.
--online additionally compares the official current MCP redirect with our version.
"""
from __future__ import annotations
import argparse
import copy
from datetime import date, datetime, timezone
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


def rendered(rows):
    lines=[BEGIN,r'\subsubsection*{带日期断言清单}',r'\phantomsection\label{app:dated-claims}',
        '下表记录所用版本、内容核验日期与范围；编译日期和 Git 提交只标识产物。',
        '链接可访问与内容复核分别记录，重编译不会刷新这里的日期。表中来源均列于附录 F。',
        r'\begingroup\small\setlength{\tabcolsep}{3pt}\renewcommand{\arraystretch}{1.25}',
        r'\tagpdfsetup{table/header-rows={1}}',
        r'\begin{longtable}{@{}>{\raggedright\arraybackslash}p{50mm}>{\raggedright\arraybackslash}p{28mm}>{\raggedright\arraybackslash}p{73mm}@{}}',
        r'\toprule 断言与正文位置 & 版本／核验日（UTC） & 来源与核验范围\\\midrule',
        r'\endfirsthead',
        r'\toprule 断言与正文位置 & 版本／核验日（UTC） & 来源与核验范围\\\midrule',
        r'\endhead',r'\bottomrule\endfoot']
    for row in rows:
        target=row['target']
        entry=row['claim']+r'（\hyperref['+target+r']{第~\pageref*{'+target+r'}~页}）'
        sources='、'.join(r'\href{'+s['url']+'}{'+s['name']+'}' for s in row['sources'])
        lines.append(entry+' & '+row['version']+r'\newline '+row['checked_utc']+' & '+sources+'。'+row['scope']+r'\\')
    lines += [r'\end{longtable}\endgroup',END]
    return '\n'.join(lines)


def validate():
    rows=load_claims()
    sources='\n'.join(p.read_text() for p in (BOOK/'chapters').glob('*.tex'))
    labels=set(re.findall(r'\\label\{([^}]+)\}',sources))
    audit={r['url']:r for r in json.loads((BOOK/'source-audit.json').read_text())}
    errors=manifest_errors(rows,audit,labels)
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
    print('Dated assertion regression tests passed: old version, missing metadata, wrong metadata nesting and link-only evidence rejected')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--online',action='store_true')
    args=parser.parse_args()
    if args.write:
        text=OUTPUT.read_text();table=rendered(load_claims())
        if BEGIN in text:text=re.sub(re.escape(BEGIN)+'.*?'+re.escape(END),lambda _:table,text,flags=re.S)
        else:text=text.replace(r'\subsubsection*{从可复算的例子开始}',table+'\n\n'+r'\subsubsection*{从可复算的例子开始}')
        OUTPUT.write_text(text)
    if args.self_test:self_test()
    errors=validate()
    if args.online:
        version=next(r for r in load_claims() if r['id']=='mcp')['version']
        req=Request(PREFIX.rstrip('/'),headers={'User-Agent':'ai-by-intuition-source-audit/1.0'})
        with urlopen(req,timeout=30) as response:
            errors.extend(current_version_errors(response.geturl(),version))
        print(f'Official current MCP revision compared with reviewed {version}')
    if errors:raise SystemExit('\n'.join(errors))
    print(f'Dated assertion QA passed: {len(load_claims())} content review records, matching printed table and MCP request')


if __name__=='__main__':main()
