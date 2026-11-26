from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT/'06_Database/JSON/monuments_places_catalog.json').read_text(encoding='utf-8-sig'))
PROGRESS = ROOT/'tools/content_progress_1_7.json'

def write_batch(batch_path):
    batch = json.loads(Path(batch_path).read_text(encoding='utf-8-sig'))
    progress = json.loads(PROGRESS.read_text(encoding='utf-8')) if PROGRESS.exists() else {'assigned_groups': list(range(1,8)), 'completed_main_ids':[], 'completed_nearby_ids':[], 'unresolved_ids':[], 'source_counts':{}, 'existing_preserved':['taj_mahal'], 'checked_on':'2026-10-07'}
    for item in batch:
        main = CATALOG['main_monuments'][item['group']-1]
        entry = main if item['place']==0 else main['nearby_places'][item['place']-1]
        assert main['order']<=7 and entry['id']!='taj_mahal'
        slug = entry['id'].split('__')[-1]
        data, scripts = ROOT/entry['paths']['data'], ROOT/entry['paths']['scripts']
        if item.get('blocked'):
            note = f"RESEARCH NOTE — {entry['display_name']}\nChecked: 2026-10-07\nStatus: Research blocked; not ready for narration.\n\n{item['blocked']}\n"
            (data/'Sources'/f'{slug}_research_note.txt').write_text(note,encoding='utf-8')
            if entry['id'] not in progress['unresolved_ids']: progress['unresolved_ids'].append(entry['id'])
            PROGRESS.write_text(json.dumps(progress,ensure_ascii=False,indent=2),encoding='utf-8')
            continue
        assert len(item['sources'])>=1 and len(item['en'].split())>=100 and re.search('[\u0900-\u097f]',item['hi'])
        basic = f"{entry['display_name']}\n\nPlace ID: {entry['id']}\nLocation: {item['location']}\nType: {item['type']}\nUser-selected parent group: {main['display_name']}\nContent checked on: 2026-10-07\n\nOverview\n{item['facts'][0]}\n\nIdentity and scope\n{item.get('note','The selected place identity is supported by the sources below. Nearby is a project association; distance and travel time have not been calculated.')}\n\nVisitor information\nLive opening hours, fees, photography rules and access arrangements are deliberately excluded. Confirm these directly with the site before visiting.\n"
        (data/'Basic_Info'/f'{slug}_basic.txt').write_text(basic,encoding='utf-8')
        facts = f"VERIFIED FACTS — {entry['display_name']}\nChecked: 2026-10-07\n\n"+'\n'.join(f'{i}. {f}' for i,f in enumerate(item['facts'],1))+'\n\n'+item.get('note','')+'\n'
        (data/'Facts'/f'{slug}_facts.txt').write_text(facts,encoding='utf-8')
        story = f"STORY DATA — {entry['display_name']}\nChecked: 2026-10-07\n\nNarration purpose: Introduce this specific place through verified history, visible features and a respectful heritage perspective.\n\nEnglish master narrative\n{item['en']}\n\nHindi master narrative\n{item['hi']}\n\nProduction note: The narration includes original descriptive interpretation. It does not claim that those observations are historical quotations. Names and chronology follow the source record.\n"
        (data/'Story_Data'/f'{slug}_story.txt').write_text(story,encoding='utf-8')
        sources = f"CONTENT SOURCES — {entry['display_name']}\nChecked online: 2026-10-07\nPurpose: Factual research for application text and narration. Image licensing is recorded separately.\n\n"
        for i,s in enumerate(item['sources'],1):
            sources+=f"[{i}] {s['title']}\nURL: {s['url']}\nUsed for: {s['claims']}\n\n"
        sources+=f"Editorial checks\n{item.get('note','Unsupported legends, superlatives, visitor prices and opening hours are omitted.')}\nThe audio scripts are original paraphrases, with sources kept outside the spoken text.\nNo distance or travel time is inferred from the parent association.\n"
        (data/'Sources'/f'{slug}_sources.txt').write_text(sources,encoding='utf-8')
        (scripts/'English'/f'{slug}_master_story_English.txt').write_text(item['en'].strip()+'\n',encoding='utf-8')
        (scripts/'Hindi'/f'{slug}_master_story_Hindi.txt').write_text(item['hi'].strip()+'\n',encoding='utf-8')
        voice=f"VOICE DIRECTIONS — {entry['display_name']}\n\nRole: Warm, clear heritage guide speaking to one visitor.\nTone: Curious, respectful and calm. Avoid exaggerated drama or advertising delivery.\nPace: English approximately 125–145 words per minute; Hindi at a natural equivalent pace.\nPauses: Brief sentence pauses and a slightly longer pause between paragraphs.\nEmphasis: Gently emphasize {entry['display_name']} and the names in the story.\nPronunciation: Review Indian place names and architectural terms before synthesis. Hindi is written in Devanagari for Hindi TTS. Do not use English phonetics for the Hindi voice.\nText-to-speech input: Use only the matching master-story file. Do not read this direction file, source URLs, headings or metadata aloud.\nConsistency: English and Hindi should convey the same facts, with natural language-specific phrasing.\nDuration: English master contains {len(item['en'].split())} words. Duration depends on the chosen voice; listen to the rendered audio before accepting it.\nQA: Check names, dates, pauses and clipping by listening to the complete generated audio. No audio file has been synthesized in this content-preparation stage.\n"
        (scripts/'Voice_Directions'/f'{slug}_voice_direction.txt').write_text(voice,encoding='utf-8')
        key='completed_main_ids' if item['place']==0 else 'completed_nearby_ids'
        if entry['id'] not in progress[key]:progress[key].append(entry['id'])
        if entry['id'] in progress['unresolved_ids']:progress['unresolved_ids'].remove(entry['id'])
        progress['source_counts'][entry['id']]=len(item['sources'])
        PROGRESS.write_text(json.dumps(progress,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'main':len(progress['completed_main_ids']),'nearby':len(progress['completed_nearby_ids']),'unresolved':progress['unresolved_ids']}))

if __name__=='__main__':
    import sys
    write_batch(sys.argv[1])
