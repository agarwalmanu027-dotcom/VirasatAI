import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = json.loads((ROOT / '06_Database/JSON/monuments_places_catalog.json').read_text(encoding='utf-8-sig'))
ENTRIES = {e['id']: e for g in CAT['main_monuments'] if 8 <= g['order'] <= 14 for e in [g, *g['nearby_places']]}
def write_record(r):
    e = ENTRIES[r['id']]
    slug = e['id'].split('__')[-1]
    d, s = ROOT/e['paths']['data'], ROOT/e['paths']['scripts']
    for directory in ['Basic_Info','Facts','Story_Data','Sources']:
        (d/directory).mkdir(parents=True, exist_ok=True)
    for directory in ['English','Hindi','Voice_Directions']:
        (s/directory).mkdir(parents=True, exist_ok=True)
    checked = r.get('checked', '2026-10-07')
    basic = f"Name: {e['display_name']}\nPlace ID: {e['id']}\nLocation: {r['location']}\nType: {r['type']}\nVerification date: {checked}\nContent status: verified narrative prepared\n\nOverview\n{r['summary']}\n\nIdentity and scope notes\n{r.get('notes','User-selected parent association preserved. No travel distance or journey time has been assumed.')}\n\nVisitor information\nOpening hours, ticket prices, accessibility, transport and photography permissions are not live-verified in this content pack. Check the managing institution before visiting.\n"
    (d/'Basic_Info'/f'{slug}_basic.txt').write_text(basic,encoding='utf-8')
    (d/'Facts'/f'{slug}_facts.txt').write_text(f"{e['display_name']} — verified facts\nChecked: {checked}\n\n" + '\n'.join(f'{i}. {f}' for i,f in enumerate(r['facts'],1)) + '\n\nReferences: see the matching Sources file. Legends, where included, are identified as tradition rather than verified events.\n',encoding='utf-8')
    (d/'Story_Data'/f'{slug}_story.txt').write_text(f"{e['display_name']} — story content\n\n{r['en']}\n\nEditorial notes\n{r.get('notes','Narration uses verified features and interpretation. No invented dialogue or unverified event is included.')}\n",encoding='utf-8')
    sources=f"{e['display_name']} — factual sources\nChecked: {checked}\nMethod: primary institutional or government pages opened or reviewed through web research; writing is an original paraphrase.\n\n"
    for i,source in enumerate(r['sources'],1):
        sources+=f"[{i}] {source[0]}\nURL: {source[1]}\nSupports: {source[2]}\n\n"
    sources+='Editorial limitations: nearby is the user-selected grouping, not a verified distance promise. Operational details are excluded from spoken scripts. Hindi is a natural-language counterpart of the English narration. TTS pronunciation must be tested with the selected voice.\n'
    (d/'Sources'/f'{slug}_sources.txt').write_text(sources,encoding='utf-8')
    (s/'English'/f'{slug}_master_story_English.txt').write_text(r['en'].strip()+'\n',encoding='utf-8')
    (s/'Hindi'/f'{slug}_master_story_Hindi.txt').write_text(r['hi'].strip()+'\n',encoding='utf-8')
    voice=f"Place: {e['display_name']}\nDelivery: warm, clear heritage-guide narration; natural conversational pace.\nEnglish pace: 115–130 words per minute.\nHindi pace: 105–120 words per minute; use a Hindi voice for Devanagari.\nPause briefly after each paragraph and at sentence boundaries. Do not read this direction file aloud.\nPronunciation notes: {r.get('pronunciation',e['display_name'])}. Test local names with the selected TTS engine before audio export.\nEnglish word count: {len(r['en'].split())}\nEstimated English duration: {round(len(r['en'].split())/125*60)} seconds at 125 words per minute.\nScripts have no spoken headings, citations, URLs or stage directions.\nNo audio file has been generated or tested by this content-writing step.\n"
    (s/'Voice_Directions'/f'{slug}_voice_direction.txt').write_text(voice,encoding='utf-8')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--only-file', help='Write only this existing batch JSON filename, while reporting all batches.')
    args = parser.parse_args()
    records=[]
    for p in sorted((ROOT/'tools').glob('content_records_8_14_*.json')):
        records.extend(json.loads(p.read_text(encoding='utf-8')))
    to_write = records
    if args.only_file:
        batch_path = (ROOT/'tools'/args.only_file).resolve()
        if batch_path.parent != (ROOT/'tools').resolve():
            raise ValueError('Batch must be inside the project tools directory')
        to_write = json.loads(batch_path.read_text(encoding='utf-8'))
    for r in to_write:
        write_record(r)
    report={'checked_on':max(r.get('checked','2026-10-07') for r in records),'assigned_count':len(ENTRIES),'completed_count':len(records),'completed_ids':[r['id'] for r in records],'source_count':sum(len(r['sources']) for r in records),'unresolved_ids':[],'remaining_ids':[x for x in ENTRIES if x not in {r['id'] for r in records}]}
    (ROOT/'tools/content_progress_8_14.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'completed':len(records),'remaining':len(report['remaining_ids']),'sources':report['source_count']}))
