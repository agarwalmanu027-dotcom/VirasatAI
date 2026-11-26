import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / '06_Database/JSON/monuments_places_catalog.json').read_text(encoding='utf-8-sig'))
ENTRIES = {}
for main in CATALOG['main_monuments']:
    if main['order'] >= 15:
        ENTRIES[main['id']] = main
        ENTRIES.update({e['id']: e for e in main['nearby_places']})

def save(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.strip() + '\n', encoding='utf-8')

def run():
    complete, unresolved, sources, qa = [], [], {}, []
    for batch in sorted((ROOT / 'tools').glob('content_batch_1[5-9].json')) + sorted((ROOT / 'tools').glob('content_batch_20.json')):
        for record in json.loads(batch.read_text(encoding='utf-8-sig')):
            entry = ENTRIES[record['id']]
            slug = entry['folder_name'].lower()
            data = ROOT / entry['paths']['data']
            script = ROOT / entry['paths']['scripts']
            bibliography = '\n\n'.join(f"[{i}] {source[0]}\nURL: {source[1]}\nSupports: {source[2]}\nChecked: 2026-10-07" for i, source in enumerate(record['sources'], 1))
            save(data / 'Sources' / f'{slug}_sources.txt', f"VIRASATAI — VERIFIED SOURCE RECORD\nEntry ID: {entry['id']}\nUser label: {entry['display_name']}\n\n{bibliography}\n\nMethod: Original paraphrased narrative based on listed primary sources. Observational prompts and respectful visitor advice are editorial. No prices, opening hours, guaranteed activities, exact distance or journey time are asserted. Recheck access and site rules before visiting.")
            if record.get('blocked'):
                unresolved.append(entry['id'])
                save(data / 'Sources' / f'{slug}_research_note.txt', f"RESEARCH STATUS: IDENTITY OR HERITAGE EVIDENCE UNRESOLVED\nEntry: {entry['display_name']}\n\n{record['blocked']}\n\nNo completed spoken script is supplied, to avoid inventing or silently substituting a site.")
                continue
            facts = '\n'.join(f"{i}. {fact}" for i, fact in enumerate(record['facts'], 1))
            save(data / 'Basic_Info' / f'{slug}_basic.txt', f"VIRASATAI — BASIC INFORMATION\nName: {entry['display_name']}\nEntry ID: {entry['id']}\nLocation: {record['location']}\nType: {record['type']}\nIdentity note: {record.get('identity', 'User-selected site identity verified against the sources below.')}\nContent status: Source-checked narrative prepared on 2026-10-07; audio has not been generated or auditioned.\n\n{facts}\n\nSources: See {slug}_sources.txt. The parent association is the user's selection, not a verified proximity claim.")
            save(data / 'Facts' / f'{slug}_facts.txt', f"VIRASATAI — IMPORTANT FACTS\n{entry['display_name']}\n\n{facts}\n\nSource key and verification date: {slug}_sources.txt.")
            save(data / 'Story_Data' / f'{slug}_story.txt', f"VIRASATAI — STORY DATA\nEntry ID: {entry['id']}\nName: {entry['display_name']}\nNarrative focus: {record['focus']}\nLanguage files: Separate English and Devanagari Hindi master scripts in 03_Scripts.\nStatus: Written narration ready for TTS input; pronunciation and generated audio still need listening QA.\n\n{record['en']}")
            save(script / 'English' / f'{slug}_master_story_English.txt', record['en'])
            save(script / 'Hindi' / f'{slug}_master_story_Hindi.txt', record['hi'])
            count = len(re.findall(r"\b[\w]+(?:['’-][\w]+)*\b", record['en']))
            save(script / 'Voice_Directions' / f'{slug}_voice_direction.txt', f"VIRASATAI — VOICE DIRECTIONS\nPlace: {entry['display_name']}\nRead only the selected master-story body. Do not read filenames, this file, source citations or metadata.\nEnglish: Warm, clear, curious museum-guide voice, approximately 125–140 words per minute.\nHindi: Natural Indian Hindi voice, calm conversational delivery. Input is Devanagari, not Roman transliteration.\nPause briefly at full stops and slightly longer between paragraphs. Avoid theatrical suspense or invented ambient effects.\nEnglish word count: {count}. Duration is an estimate until audio is rendered.\nPronunciation practice: {record.get('pronunciation', entry['display_name'])}.\nDo not read English spelling hints aloud. Listen to both generated versions and verify place names before app publication.\nNarration and gallery are separate; no image-timing synchronization is required.")
            complete.append(entry['id'])
            sources[entry['id']] = len(record['sources'])
            low, high = (180, 240) if '__' not in entry['id'] else (120, 180)
            qa.append({'id': entry['id'], 'english_words': count, 'length_in_target': low <= count <= high, 'hindi_present': bool(re.search('[\u0900-\u097f]', record['hi']))})
    save(ROOT / 'tools/content_progress_15_20.json', json.dumps({'checked_date':'2026-10-07', 'completed_count':len(complete), 'completed_ids':complete, 'source_counts':sources, 'unresolved_ids':unresolved, 'qa':qa}, ensure_ascii=False, indent=2))
    print(json.dumps({'completed':len(complete),'unresolved':unresolved,'length_issues':[q for q in qa if not q['length_in_target']]}, ensure_ascii=False))

if __name__ == '__main__':
    run()
