#!/usr/bin/env python3
"""Optional extraction against local original captures; publish facts, not full pages."""
import datetime, hashlib, html, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def matrix_post_headers(source):
    records=[]
    for chunk in re.split(r'<li class="postbitlegacy',source)[1:]:
        if 'Aproveitei e passeei por hellgate' not in chunk:continue
        id=re.search(r'id="post_(\d+)"',chunk)
        date=re.search(r'<span class="date">([^<]*)<span class="time">([^<]*)</span>',chunk)
        if id is None or date is None:raise ValueError('post header unavailable')
        stamp=' '.join(html.unescape(date.group(1)+' '+date.group(2)).split())
        parsed=datetime.datetime.strptime(stamp,'%d-%m-%Y, %H:%M')
        records.append({'post_id':id.group(1),'displayed_post_timestamp':parsed.isoformat(),
                        'timezone_authenticated':False,'reports_middle_stack_look_count_six':
                        'Apesar de parecerem ser 5 caveiras' in chunk,
                        'matrix_image_link_present':'http://i63.tinypic.com/14v7969.jpg' in chunk})
    return records


def run():
    captures={r['id']:r for p in sorted(ROOT.glob('data/round26_http_*.json')) for r in json.loads(p.read_text())}
    def payload(id):
        row=captures[id];raw=(ROOT/row['body_local_ignored']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==row['sha256']
        return raw
    earliest=[]
    for id in ('wiki469_first','hellgate_first'):
        for page in json.loads(payload(id))['query']['pages']:
            for rev in page.get('revisions',[]):
                content=rev['slots']['main']['content'];assert hashlib.sha1(content.encode()).hexdigest()==rev['sha1']
                earliest.append({'page':page['title'],'revision_id':rev['revid'],'timestamp':rev['timestamp'],
                                  'sha1_verified':rev['sha1'],'mentions_matrix_or_skulls':
                                  any(w in content.lower() for w in ('matriz','caveira','skull','misterio02'))})
    intervals=[]
    for id in ('wiki469_history','hellgate_history'):
        obj=json.loads(payload(id));intervals.append({'capture_id':id,'revisions_in_requested_interval':
            sum(len(p.get('revisions',[])) for p in obj.get('query',{}).get('pages',[])),
            'continuation_present':bool(obj.get('continue'))})
    images=[r for p in json.loads(payload('matrix_image_history'))['query']['pages'] for r in p.get('imageinfo',[])]
    archive=[]
    for id in ('archive2010_page58_index','archive2010_page59_index','forum2017_image_cdx'):
        obj=json.loads(payload(id));archive.append({'capture_id':id,'returned_cdx_rows':max(0,len(obj)-1),
                                                   'scope':'exact requested URL/time interval only; not global archive absence'})
    forum=matrix_post_headers(payload('forum2016_look').decode('latin-1'))
    return {'earliest_available_wiki_records':earliest,'wiki2008_2010_intervals':intervals,'image_versions_returned':images,
            'forum_posts':forum,'forum_lineage':'Post6999460quotes post6999332; one reported observation, not two independent counts. Internal capture ID forum2016_look was a tentative label; displayed original post date is2017.',
            'archive_requests':archive,'recording_probe':'results/round26_cam_probe.json','new_authenticated_full_5x5_keys':0,
            'new_authenticated_game_transition_dates':0,'new_english_numeric_pairs':0}


if __name__=='__main__':
    out=run();(ROOT/'results/round26_sources.json').write_text(json.dumps(out,indent=2)+'\n')
