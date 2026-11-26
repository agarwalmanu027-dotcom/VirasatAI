import json,re
from pathlib import Path
ROOT=Path(r'C:\Desktop\VirasatAI')
catalog=json.loads((ROOT/'06_Database/JSON/monuments_places_catalog.json').read_text(encoding='utf-8-sig'))
records=[]
for main in catalog['main_monuments']:
    if main['order']>7: continue
    for place in [main]+main['nearby_places']:
        is_main=place is main
        if place['id']=='taj_mahal':
            records.append({'place_id':place['id'],'status':'existing_pilot_preserved','note':'Existing Taj Mahal main text/scripts deliberately excluded from new-content length checks.'})
            continue
        scripts=ROOT/place['paths']['scripts']; data=ROOT/place['paths']['data']
        row={'place_id':place['id'],'is_main':is_main,'issues':[],'script_paths':{}}
        for lang in ['English','Hindi']:
            paths=list((scripts/lang).glob('*_master_story_'+lang+'.txt'))
            if not paths:
                row['issues'].append('missing_'+lang+'_script'); continue
            if len(paths)!=1: row['issues'].append('multiple_'+lang+'_scripts')
            path=paths[0]; body=path.read_text(encoding='utf-8-sig').strip()
            row['script_paths'][lang]=path.relative_to(ROOT).as_posix()
            row[lang+'_word_count']=len(body.split())
            if not body: row['issues'].append('empty_'+lang+'_script')
            if re.search(r'https?://|^\s*#|^\s*[-*]\s|\[\d+\]|\[(?:pause|music|voice)',body,re.M|re.I): row['issues'].append('nonspoken_format_'+lang)
            if '\ufffd' in body: row['issues'].append('replacement_character_'+lang)
            if lang=='English' and (len(body.split())<(180 if is_main else 120) or len(body.split())>(240 if is_main else 180)):
                row['issues'].append('English_length_outside_target')
            if lang=='Hindi' and not re.search(r'[\u0900-\u097f]',body): row['issues'].append('missing_Devanagari_Hindi')
        for section in ['Basic_Info','Facts','Story_Data','Sources']:
            files=list((data/section).glob('*.txt'))
            if not files: row['issues'].append('missing_'+section)
            if section=='Sources' and files:
                source='\n'.join(p.read_text(encoding='utf-8-sig') for p in files)
                urls=re.findall(r'https?://\S+',source)
                row['source_urls']=urls
                if not urls: row['issues'].append('sources_without_urls')
                if 'Checked online:' not in source: row['issues'].append('sources_missing_check_date')
                if 'Used for:' not in source: row['issues'].append('sources_missing_claim_scope')
        if not list((scripts/'Voice_Directions').glob('*_voice_direction.txt')): row['issues'].append('missing_voice_directions')
        note_files=list(data.glob('*pending*'))+list(data.glob('*research*'))+list((data/'Sources').glob('*pending*'))
        if 'hathni_kund' in place['id']:
            row['status']='documented_research_pending'
            row['note']='Hathni Kund remains explicitly unresolved; missing narration is expected and must not be called complete.'
        else: row['status']='checked' if not row['issues'] else 'needs_attention'
        records.append(row)
selected=[]
for group in [5,6,7]:
    reviews=json.loads((ROOT/f'tools/image_review/reviewed_group_{group:02}.json').read_text(encoding='utf-8-sig'))
    selected.append({'group':group,'places':len(reviews),'selected_images':sum(len(r['selected']) for r in reviews)})
report={'scope':'Local structural and spoken-body audit, groups 1–7; sampled identity/source check recorded separately. This does not claim all citations independently rechecked online.','entries':len(records),'ready_new_content':sum(r['status']=='checked' for r in records),'pending':sum(r['status']=='documented_research_pending' for r in records),'needs_attention':sum(r['status']=='needs_attention' for r in records),'image_review_counts':selected,'records':records}
(ROOT/'tools/image_review/content_audit_groups_01_07.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='records'},ensure_ascii=False))
for row in records:
    if row.get('issues'): print(row['place_id'],row['status'],row['issues'])
