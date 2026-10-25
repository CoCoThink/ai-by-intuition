#!/usr/bin/env python3
"""Minimal Claude Messages API client-tool round trip.

Default: exercise a synthetic response offline, without credentials or requests.
--real --model MODEL_ID: explicitly make up to two paid API requests.
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
    'description': 'Compute growth from two already verified revenues in the same unit.',
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
    if response.get('stop_reason') != 'tool_use' or len(calls) != 1:
        raise ValueError('Expected exactly one client tool call')
    # Preserve ALL assistant content blocks, not just the selected tool_use block.
    return copy.deepcopy(messages)+[
        {'role':'assistant','content':response['content']},
        {'role':'user','content':[tool_result(calls[0])]},
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
    for bad in [dict(sample['content'][-1],name='upload_file'),
                dict(sample['content'][-1],input={'previous':0,'current':132}),
                dict(sample['content'][-1],input={'previous':True,'current':132}),
                dict(sample['content'][-1],input={'previous':120,'current':float('nan')}),
                dict(sample['content'][-1],id='')]:
        try:tool_result(bad)
        except ValueError:pass
        else:raise AssertionError('Unsafe dispatch accepted')
    print('Offline Claude wire-format QA: call/result IDs, complete history, 10% calculation and host rejection cases passed; no API request')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--real',action='store_true');p.add_argument('--model');a=p.parse_args()
    run_checks()
    if a.real:
        if not a.model:p.error('--real requires an available --model ID')
        body=request_body(a.model);response=api_call(body)
        body['messages']=continue_messages(body['messages'],response)
        body['tool_choice']={'type':'none'}
        final=api_call(body)
        print(json.dumps(final,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
