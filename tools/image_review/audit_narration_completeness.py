import json,re
from pathlib import Path
ROOT=Path(r'C:\Desktop\VirasatAI')
catalog=json.loads((ROOT/'06_Database/JSON/monuments_places_catalog.json').read_text(encoding='utf-8-sig'))
pending_ids={'amer_fort__hathni_kund','badami_cave_temples__galaganatha_temples'}
rows=[]
for main in catalog['main_monuments']:
    for place in [main]+main['nearby_places']:
        scripts=ROOT/place['paths']['scripts']; data=ROOT/place['paths']['data']
        row={'place_id':place['id'],'is_main':place is main,'languages':{},'issues':[]}
        for lang in ['English','Hindi']:
            candidates=[p for p in (scripts/lang).glob('*.txt') if 'master_story' in p.name.lower()]
            clean_pilot=[p for p in (scripts/lang).glob('*.txt') if ('tts' in p.name.lower() or 'spoken' in p.name.lower()) and 'master_story' not in p.name.lower()]
            chosen=clean_pilot[0] if place['id']=='taj_mahal' and clean_pilot else (candidates[0] if candidates else None)
            if not chosen:
                row['issues'].append('missing_'+lang+'_script'); continue
            body=chosen.read_text(encoding='utf-8-sig').strip()
            fmt=[]
            if re.search(r'https?://',body): fmt.append('url')
            if re.search(r'^\s*#|^\s*[-*]\s|^\s*(?:VIRASATAI|References|Sources|Editorial notes|Voice directions)',body,re.M|re.I): fmt.append('heading_or_metadata')
            if re.search(r'\[\d+\]|\[(?:pause|music|voice)[^\]]*\]',body,re.I): fmt.append('citation_or_stage_direction')
            if re.search(r'catalog|field report|count this label|invented foundation|project documents do not confirm|past inventory is not a promise|not a claim of an ancient|without inventing the biography|unverified legend|कैटलॉग|मनगढ़ंत स्थापना|दूसरा असंबंधित स्मारक|पुराने परियोजना दस्तावेज|पुरानी सूची आज के दर्शन',body,re.I): fmt.append('research_or_catalog_process')
            if '\ufffd' in body: fmt.append('unicode_replacement')
            if lang=='Hindi' and not re.search(r'[\u0900-\u097f]',body): fmt.append('missing_Devanagari')
            words=len(body.split())
            row['languages'][lang]={'path':chosen.relative_to(ROOT).as_posix(),'word_count':words,'body_format_issues':fmt,'uses_clean_pilot_copy':chosen in clean_pilot}
            if not body: row['issues'].append('empty_'+lang+'_body')
            if fmt:
                if place['id']=='taj_mahal' and not clean_pilot: row.setdefault('preserved_original_format_notes',[]).extend(lang+': '+x for x in fmt)
                else: row['issues'].append(lang+'_body_format')
            if lang=='English' and place['id']!='taj_mahal' and not (180<=words<=240 if place is main else 120<=words<=180): row['issues'].append('English_word_count_outside_target')
        voices=list((scripts/'Voice_Directions').glob('*.txt'))
        row['voice_direction_file_count']=len(voices)
        if not voices and place['id'] not in pending_ids: row['issues'].append('missing_voice_directions')
        if voices and place['id']!='taj_mahal' and 'English' in row['languages']:
            v='\n'.join(p.read_text(encoding='utf-8-sig') for p in voices)
            declared=re.search(r'English word count:\s*(\d+)',v) or re.search(r'English master contains\s*(\d+)\s+words',v)
            row['voice_word_count_matches']=bool(declared and int(declared.group(1))==row['languages']['English']['word_count'])
            if not row['voice_word_count_matches']: row['issues'].append('voice_word_count_mismatch')
        stories=list((data/'Story_Data').glob('*.txt'))
        if place['id']!='taj_mahal' and 'English' in row['languages']:
            en=(ROOT/row['languages']['English']['path']).read_text(encoding='utf-8-sig').strip()
            row['story_data_synced']=any(en in p.read_text(encoding='utf-8-sig') for p in stories)
            if not row['story_data_synced']: row['issues'].append('story_data_not_synced')
        row['status']='documented_pending' if place['id'] in pending_ids else ('needs_attention' if row['issues'] else 'complete_written_pack')
        rows.append(row)
report={'checked_date':'2026-10-08','scope':'All 220 catalog entries checked for written narration availability, spoken-body formatting, target English lengths, Hindi encoding, Story_Data synchronisation and voice word counts. Existing Taj master files are preserved; clean Taj copies are preferred when available. This does not claim audio generation, audition or a fresh fact verification of every source.','catalog_entries':len(rows),'complete_written_packs':sum(r['status']=='complete_written_pack' for r in rows),'documented_pending_packs':sum(r['status']=='documented_pending' for r in rows),'packs_needing_attention':sum(r['status']=='needs_attention' for r in rows),'available_language_scripts':sum(len(r['languages']) for r in rows),'selected_spoken_bodies_without_format_issues':sum(not lang['body_format_issues'] for r in rows for lang in r['languages'].values()),'preserved_original_pilot_bodies_with_format_notes':sum(len(r.get('preserved_original_format_notes',[])) for r in rows),'pending_ids':sorted(pending_ids),'rows':rows}
(ROOT/'tools/image_review/narration_completeness_qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False))
for row in rows:
    if row['issues'] and row['status']!='documented_pending': print(row['place_id'],row['issues'])
