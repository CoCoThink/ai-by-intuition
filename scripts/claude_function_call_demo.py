#!/usr/bin/env python3
"""Minimal Claude Messages API client-tool round trip.

Default: exercise a synthetic response offline, without credentials or requests.
--real --model MODEL_ID: explicitly make up to four paid API requests.
Official schema checked 2026-10-25; no vendor SDK required.
"""
from __future__ import annotations
import argparse
import copy
import json
import math
import os
from urllib.request import Request, urlopen

TOOL = {
    'name': 'quarter_growth',
    'description': 'Compute growth from verified revenues in the same unit.',
    'input_schema': {
        'type': 'object',
        'properties': {'previous': {'type': 'number'}, 'current': {'type': 'number'}},
        'required': ['previous', 'current'], 'additionalProperties': False,
    },
}
MESSAGES = [{'role': 'user', 'content':
             'Verified Q2 and Q3 revenue: 120 and 132 million CNY. Use quarter_growth.'}]


def tool_result(call):
    """Host enforcement; tool names and arguments are model output, hence untrusted."""
    if call.get('type') != 'tool_use' or call.get('name') != TOOL['name']:
        raise ValueError('Tool not allowed')
    if not isinstance(call.get('id'), str) or not call['id']:
        raise ValueError('Missing correlation ID')
    args = call.get('input')
    if not isinstance(args, dict) or set(args) != {'previous','current'}:
        raise ValueError('Wrong arguments')
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in args.values()):
        raise ValueError('Finite numeric inputs required')
    # Bind this demonstration to the two revenues supplied by the authorized task.
    if args != {'previous':120,'current':132}:
        raise ValueError('Arguments differ from the verified task inputs')
    growth = (args['current']-args['previous'])/args['previous']
    return {'type':'tool_result', 'tool_use_id':call['id'],
            'content':json.dumps({'growth':growth,'unit':'ratio'})}


def continue_messages(messages, response):
    calls = [b for b in response['content'] if b['type']=='tool_use']
    if response.get('stop_reason') != 'tool_use' or not calls:
        raise ValueError('Expected client tool calls')
    results = [tool_result(call) for call in calls]
    if len({r['tool_use_id'] for r in results}) != len(results):
        raise ValueError('Duplicate correlation IDs')
    # Preserve ALL assistant content blocks, not just the selected tool_use block.
    return copy.deepcopy(messages)+[
        {'role':'assistant','content':copy.deepcopy(response['content'])},
        {'role':'user','content':results},
    ]


def request_body(model):
    return {'model':model,'max_tokens':256,'tools':[TOOL],
            'tool_choice':{'type':'tool','name':TOOL['name']},'messages':copy.deepcopy(MESSAGES)}


def api_call(body):
    key = os.environ['ANTHROPIC_API_KEY']
    request = Request('https://api.anthropic.com/v1/messages',
        data=json.dumps(body).encode(), method='POST', headers={
            'content-type':'application/json','x-api-key':key,'anthropic-version':'2023-06-01'})
    with urlopen(request,timeout=60) as result:
        return json.load(result)


def run_client(model, max_requests=4, request=None):
    """Bounded host loop. Inject an offline transport for protocol regression tests."""
    if max_requests < 1:
        raise ValueError('A positive request budget is required')
    request = api_call if request is None else request
    body = request_body(model)
    for _ in range(max_requests):
        response = request(body)
        reason = response.get('stop_reason')
        if reason == 'end_turn':
            return response
        if reason != 'tool_use':
            raise RuntimeError(f'Response needs separate handling: {reason}')
        body['messages'] = continue_messages(body['messages'], response)
        body['tool_choice'] = {'type':'auto'}
    raise RuntimeError('Request budget exhausted before end_turn')


def run_checks():
    # Synthetic fixture in the documented wire format; NOT a live model response.
    sample={'stop_reason':'tool_use','content':[
        {'type':'text','text':'I will calculate the verified growth.'},
        {'type':'tool_use','id':'demo-call-1','name':'quarter_growth',
         'input':{'previous':120,'current':132}}]}
    follow=continue_messages(MESSAGES,sample)
    assert follow[-2]['content']==sample['content']
    assert follow[-1]['content'][0]['tool_use_id']=='demo-call-1'
    assert json.loads(follow[-1]['content'][0]['content'])['growth']==.1
    # Two calls in one response must both be returned, before another request.
    parallel=copy.deepcopy(sample)
    parallel['content'].append(dict(sample['content'][-1],id='demo-call-2'))
    assert [r['tool_use_id'] for r in continue_messages(MESSAGES,parallel)[-1]['content']]==['demo-call-1','demo-call-2']
    duplicate=copy.deepcopy(parallel);duplicate['content'][-1]['id']='demo-call-1'
    try:continue_messages(MESSAGES,duplicate)
    except ValueError:pass
    else:raise AssertionError('Duplicate call IDs accepted')
    # A second tool round must be handled, not mistaken for a final answer.
    second=copy.deepcopy(sample);second['content'][-1]['id']='demo-call-3'
    final={'stop_reason':'end_turn','content':[{'type':'text','text':'Growth is 10%.'}]}
    replies=iter((sample,second,final));requests=[]
    def offline(body):
        requests.append(copy.deepcopy(body));return next(replies)
    assert run_client('offline-fixture',request=offline)==final
    assert len(requests)==3 and len(requests[-1]['messages'])==5
    assert requests[-1]['messages'][-1]['content'][0]['tool_use_id']=='demo-call-3'
    assert requests[1]['tool_choice']=={'type':'auto'}
    for reply,budget in (({'stop_reason':'max_tokens','content':[]},4), (sample,2)):
        seen=[]
        def failure_transport(body):
            seen.append(copy.deepcopy(body));return copy.deepcopy(reply)
        try:run_client('offline-fixture',max_requests=budget,request=failure_transport)
        except RuntimeError:pass
        else:raise AssertionError('Truncation or exhausted budget treated as completion')
        assert len(seen)==(budget if reply is sample else 1)
    for bad in [dict(sample['content'][-1],name='upload_file'),
                dict(sample['content'][-1],input={'previous':0,'current':132}),
                dict(sample['content'][-1],input={'previous':True,'current':132}),
                dict(sample['content'][-1],input={'previous':120,'current':float('nan')}),
                dict(sample['content'][-1],id='')]:
        try:tool_result(bad)
        except ValueError:pass
        else:raise AssertionError('Unsafe dispatch accepted')
    from pathlib import Path
    import re
    source=(Path(__file__).resolve().parents[1]/'book/chapters/23d-agent-tools.tex').read_text()
    definitions=[json.loads(block) for block in re.findall(r'\\begin\{Verbatim\}[^\n]*\n(.*?)\\end\{Verbatim\}',source,re.S)
                 if '"input_schema"' in block]
    assert len(definitions)==1 and definitions[0]==TOOL, 'Printed tool definition differs from executable one'
    print('Offline Claude QA: description/schema, repeated and parallel tool calls, IDs, history, stop reasons, request budget and host rejection passed; no API request')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--real',action='store_true');p.add_argument('--model');a=p.parse_args()
    run_checks()
    if a.real:
        if not a.model:p.error('--real requires an available --model ID')
        final=run_client(a.model)
        print(json.dumps(final,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
