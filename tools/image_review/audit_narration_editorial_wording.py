import json,re
from pathlib import Path
ROOT=Path(r'C:\Desktop\VirasatAI')
catalog=json.loads((ROOT/'06_Database/JSON/monuments_places_catalog.json').read_text(encoding='utf-8-sig'))
by_script={}
for main in catalog['main_monuments']:
    for place in [main]+main['nearby_places']:
        by_script[place['paths']['scripts']]=place['id']
packs=[]
for path in sorted((ROOT/'03_Scripts').rglob('*_master_story_*.txt')):
    text=path.read_text(encoding='utf-8-sig').strip()
    relative=path.relative_to(ROOT).as_posix()
    directory=path.parent.parent.relative_to(ROOT).as_posix()
    packs.append({'path':relative,'place_id':by_script.get(directory,directory),'language':path.parent.name,'text':text})
specific={
    'mahabalipuram__poonjeri_village':('research_process','The historical project documents do not confirm','पुराने परियोजना दस्तावेज'),
    'mehrangarh_fort__machia_biological_park':('research_process','a past inventory is not a promise','पुरानी सूची आज के दर्शन का वादा'),
    'hampi_monuments__sanapur_lake':('editorial_claim_disclaimer','not a claim of an ancient temple','प्राचीन मंदिर'),
    'hampi_monuments__achyutaraya_temple':('editorial_invention_disclaimer','without inventing details','मनगढ़ंत'),
    'mahabalipuram__sadras_dutch_fort':('editorial_invention_disclaimer','without pretending that every empty space','मनगढ़ंत'),
    'jaisalmer_fort__kuldhara_village':('editorial_invention_disclaimer','without inventing the biography','मनगढ़ंत'),
    'meenakshi_temple__goripalayam_dargah':('editorial_verification_disclaimer','unverified legend','अप्रमाणित')
}
priority=[]
for pack in packs:
    spec=specific.get(pack['place_id'])
    if not spec: continue
    needle=spec[1] if pack['language']=='English' else spec[2]
    hits=[line.strip() for line in pack['text'].splitlines() if needle.lower() in line.lower()]
    if hits: priority.append({'place_id':pack['place_id'],'language':pack['language'],'path':pack['path'],'issue':spec[0],'excerpt':hits[0],'recommendation':'Retain the verified place facts and visitor guidance, but rewrite the research/editorial caveat as natural spoken narration. Keep source limitations in Basic_Info or Sources.','modified':False})
attribution_patterns=[r'official tourism',r'official descriptions',r'official Rajasthan',r'tourism account',r'tourism literature',r'Government planning records',r'University records describe',r'government heritage register',r'identity is recorded',r'Central Zoo Authority records',r'Central Zoo Authority documents',r'Museum Trust identifies',r'trust records',r'Identified on the government',r'Government conservation evaluations',r'connection with sculpture is recorded']
opportunities=[]
for pack in packs:
    if pack['language']!='English': continue
    hits=[line.strip() for line in pack['text'].splitlines() if any(re.search(p,line,re.I) for p in attribution_patterns)]
    if hits: opportunities.append({'place_id':pack['place_id'],'path':pack['path'],'excerpt':hits[0],'note':'Light spoken attribution to a modern source or registry; optional style polish, not a factual error. Check the matching Hindi body too before editing.','modified':False})
changed_ids=['mehrangarh_fort__singhasni_village','mahabalipuram__sri_thiruvidandhai']+list(specific)
changed=[]
for pack in packs:
    if pack['place_id'] not in changed_ids: continue
    changed.append({'place_id':pack['place_id'],'language':pack['language'],'path':pack['path'],'word_count':len(pack['text'].split()),'clean_body':not bool(re.search(r'https?://|^\s*#|\[\d+\]',pack['text'],re.M)),'contains_research_or_catalog_process':bool(re.search(r'field report|invented foundation|count this label|catalog|दो.*कैटलॉग|मनगढ़ंत स्थापना|दूसरा असंबंधित',pack['text'],re.I))})
report={'checked_date':'2026-10-08','scope':'Global keyword scan of existing English and Hindi master-story files followed by manual triage of matched passages. This is an editorial narration audit, not a new factual-source verification or an audio audition.','scanned_script_files':len(packs),'polished_entries':changed,'remaining_priority_place_count':len(set(r['place_id'] for r in priority)),'remaining_priority_language_files':len(priority),'remaining_priority_passages':priority,'lighter_source_attribution_opportunities':opportunities,'preservation':'Nine authorized narration packs were polished: Singhasni Village, Sri Thiruvidandhai, Poonjeri Village, Machia Biological Park, Sanapur Lake, Achyutaraya Temple, Sadras Dutch Fort, Kuldhara Village and Goripalayam Dargah. Corresponding Story_Data and voice directions were synced. Existing sources, facts, basic info, images, catalog and Taj Mahal originals were not edited.'}
(ROOT/'tools/image_review/narration_editorial_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['remaining_priority_passages','lighter_source_attribution_opportunities']},ensure_ascii=False))
print('Lighter attribution opportunities:',len(opportunities))
