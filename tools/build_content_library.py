"""Build a local, read-only content browser and audit the saved place library."""
from pathlib import Path
from datetime import date
import hashlib, html, json, re
from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT = Path(r'C:\Desktop\VirasatAI')
DB = ROOT / '06_Database' / 'JSON'
TODAY = date.today().isoformat()
HOLD = {
    'amer_fort__hathni_kund': 'Exact Jaipur site identity needs further reliable-source verification.',
    'badami_cave_temples__galaganatha_temples': 'Identity pending by user instruction: Aihole group or Pattadakal temple.'
}

def relative(path):
    return path.relative_to(ROOT).as_posix() if path else None

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def first(folder, pattern='*.txt'):
    return next(iter(sorted(folder.glob(pattern))), None)

def words(text):
    return len(text.split())

def main():
    catalog = load(DB/'monuments_places_catalog.json')
    protection = load(DB/'folder_preparation_report.json')
    protected_errors = []
    for item in protection['protected_assets']:
        path = Path(item['path'])
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest().lower() != item['sha256'].lower():
            protected_errors.append(item['path'])
    if protected_errors:
        raise ValueError('Protected original files changed: '+repr(protected_errors))

    entries, errors, warnings, groups = [], [], [], []
    for main_place in catalog['main_monuments']:
        group = {'order':main_place['order'], 'name':main_place['display_name'], 'place_count':11, 'content_ready':0, 'image_count':0, 'places_with_images':0}
        for place in [main_place, *main_place['nearby_places']]:
            data = ROOT/place['paths']['data']; scripts = ROOT/place['paths']['scripts']; images_dir = ROOT/place['paths']['images']
            files = {k:first(data/f) for k,f in [('basic','Basic_Info'),('facts','Facts'),('story_data','Story_Data'),('sources','Sources')]}
            files.update(english=first(scripts/'English','*master_story*'), hindi=first(scripts/'Hindi','*master_story*'), voice_directions=first(scripts/'Voice_Directions'))
            if place['id']=='taj_mahal':
                for language in ['english','hindi']:
                    original = files[language]
                    body = re.sub(r'^#\s+[^\n]*\n\s*', '', original.read_text(encoding='utf-8-sig'), count=1).strip()+'\n'
                    clean = original.with_name('taj_mahal_tts_body_'+language+'.txt')
                    clean.write_text(body, encoding='utf-8')
                    files[language+'_original'] = original
                    files[language] = clean
            hold = HOLD.get(place['id'])
            ready = all(files[k] for k in ['basic','facts','story_data','sources','english','hindi','voice_directions']) and not hold
            if not ready and not hold: errors.append({'place_id':place['id'],'missing_files':[k for k,v in files.items() if not v]})
            texts = {k:p.read_text(encoding='utf-8-sig').strip() for k,p in files.items() if p}
            if ready:
                for language in ['english','hindi']:
                    body = texts[language]
                    if re.search(r'https?://|^#|\[\d+\]|^VIRASATAI|^English:|^Hindi:',body,re.M):
                        errors.append({'place_id':place['id'],'tts_format_problem':language})
                if not re.search(r'[\u0900-\u097f]', texts['hindi']): errors.append({'place_id':place['id'],'hindi_not_devanagari':True})
                if 'http' not in texts['sources']: errors.append({'place_id':place['id'],'source_urls_missing':True})
                count = words(texts['english'])
                target = (180,240) if place is main_place else (120,180)
                if place['id']!='taj_mahal' and not target[0]<=count<=target[1]: warnings.append({'place_id':place['id'],'english_words':count,'target':target})
            image_files = []; manifest_path = images_dir/'Image_Sources'/'image_manifest.json'
            manifest = load(manifest_path) if manifest_path.exists() else {}
            if place['id']=='taj_mahal':
                for p in sorted(images_dir.rglob('*')):
                    if p.suffix.lower() in ['.jpg','.jpeg','.png','.webp'] and 'Nearby_Heritage' not in p.relative_to(images_dir).parts:
                        with Image.open(p) as im: dimensions = im.size; im.verify()
                        image_files.append({'local_path':relative(p),'downloaded_width':dimensions[0],'downloaded_height':dimensions[1],'source_record':'02_Images/Taj_Mahal/Image_Sources/taj_mahal_source_record.txt','review_note':'Existing user-approved pilot photograph preserved. Legacy record has some author/license fields marked VERIFY; retain this publication check.'})
            else:
                for item in manifest.get('images',[]):
                    p = ROOT/item['local_path']
                    if not p.exists(): errors.append({'place_id':place['id'],'missing_image':item['local_path']}); continue
                    if hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']: errors.append({'place_id':place['id'],'image_hash_changed':item['local_path']})
                    with Image.open(p) as im: dimensions=im.size; im.verify()
                    if dimensions!=(item['downloaded_width'],item['downloaded_height']): errors.append({'place_id':place['id'],'image_dimensions_changed':item['local_path']})
                    if not item.get('license') or not item.get('author') or not item.get('source_page'): errors.append({'place_id':place['id'],'image_attribution_missing':item['local_path']})
                    image_files.append(item)
            status = 'identity_pending' if hold else ('content_ready' if ready else 'content_incomplete')
            image_status = 'identity_pending' if hold else ('reviewed_images_saved' if image_files else 'suitable_images_pending')
            place['content_status']=status
            place['image_status']=image_status
            place['audio_status']='not_generated'
            place['display_image_count']=len(image_files)
            record={'id':place['id'],'name':place['display_name'],'group_order':main_place['order'],'group_name':main_place['display_name'],'is_main':place is main_place,'content_status':status,'pending_reason':hold,'paths':place['paths'],'files':{k:relative(p) for k,p in files.items()},'english_words':words(texts.get('english','')),'estimated_english_seconds_at_130_wpm':round(words(texts.get('english',''))*60/130),'narration':{k:texts.get(k,'') for k in ['english','hindi']},'source_urls':list(dict.fromkeys(re.findall(r'https?://[^\s]+',texts.get('sources','')))),'image_status':image_status,'image_count':len(image_files),'image_manifest':relative(manifest_path) if manifest_path.exists() else None,'images':image_files,'coverage_note':manifest.get('coverage_note','Preserved original Taj Mahal pilot gallery.' if place['id']=='taj_mahal' else 'No reviewed high-quality, correct-site image saved yet.'),'download_errors':manifest.get('download_errors',[]),'audio_status':'not_generated'}
            entries.append(record)
            group['content_ready']+=int(ready); group['image_count']+=len(image_files); group['places_with_images']+=int(bool(image_files))
            if place['id']!='taj_mahal':
                for root_key in ['data','images','scripts','audio']:
                    readme=ROOT/place['paths'][root_key]/'README.txt'
                    readme.write_text(f'VIRASATAI — {place["display_name"]}\nUpdated: {TODAY}\nContent: {status}\nPhotos saved: {len(image_files)}\nAudio: not generated.\n'+(f'Pending: {hold}\n' if hold else '')+'See VirasatAI_Content_Library_Guide.md and the JSON library index for current files and source details.\n',encoding='utf-8')
        groups.append(group)
    totals={'place_entries':len(entries),'main_groups':20,'nearby_entries':200,'content_ready':sum(e['content_status']=='content_ready' for e in entries),'identity_pending':sum(e['content_status']=='identity_pending' for e in entries),'english_scripts':sum(bool(e['narration']['english']) for e in entries),'hindi_scripts':sum(bool(e['narration']['hindi']) for e in entries),'display_images':sum(e['image_count'] for e in entries),'places_with_images':sum(bool(e['image_count']) for e in entries),'places_without_images':sum(not e['image_count'] for e in entries),'protected_original_files_unchanged':len(protection['protected_assets']),'new_content_text_files':sum(sum(bool(e['files'].get(k)) for k in ['basic','facts','story_data','sources','english','hindi','voice_directions']) for e in entries if not e['is_main'] or e['id']!='taj_mahal')}
    library={'schema_version':1,'updated_on':TODAY,'scope':'Display content and narration scripts; recognition model and audio not implemented by this collection work.','totals':totals,'groups':groups,'entries':entries}
    audit={'checked_on':TODAY,'totals':totals,'errors':errors,'warnings':warnings,'image_gaps':[{'id':e['id'],'name':e['name'],'group':e['group_name'],'reason':e['pending_reason'] or e['coverage_note'],'download_errors':e['download_errors']} for e in entries if not e['image_count']],'sparse_galleries':[{'id':e['id'],'name':e['name'],'image_count':e['image_count'],'coverage_note':e['coverage_note']} for e in entries if 0<e['image_count']<3],'download_failures':[{'id':e['id'],'errors':e['download_errors']} for e in entries if e['download_errors']],'preserved_originals':{'checked':len(protection['protected_assets']),'changed':protected_errors},'limitations':['Image review is a visual check, not perfect identity or quality certification.','Some niche sites have no suitable image yet; missing galleries remain empty.','Legacy Taj source record contains VERIFY fields; original user files were preserved.','TTS scripts are prepared but audio voices and pronunciations have not been auditioned.','Distances and travel times remain unverified.','This content collection is separate from the AI training dataset.']}
    save(DB/'content_library_index.json', library); save(DB/'content_library_audit.json',audit);save(DB/'monuments_places_catalog.json',catalog)
    save(DB/'new_display_images_summary.json',[{'place_id':e['id'],'image_count':e['image_count'],'manifest':e['image_manifest']} for e in entries if e['id']!='taj_mahal'])
    build_guide(library,audit)
    build_browser(library)
    build_overview(library)
    record_context(library)
    print(json.dumps({'totals':totals,'errors':errors,'warnings':warnings},ensure_ascii=False))

def build_guide(library,audit):
    t=library['totals']
    lines=['# VirasatAI Content Library', '',f'Updated: {TODAY}', '',f'The selected list contains 20 main monument groups and 200 nearby entries. {t["content_ready"]} entries have information and English/Hindi narration scripts. {t["display_images"]} display photographs are saved across {t["places_with_images"]} entries, including the original 40 Taj Mahal photographs.', '', '## Open and use the files', '', '- Open **VirasatAI_Content_Library.html** to search places, view saved photographs, read the narration and open source links.', '- **01_Data** contains Basic_Info, Facts, Story_Data and Sources for each place.', '- **02_Images** contains photographs grouped by view. Image_Sources contains each new gallery’s source record and image_manifest.json.', '- **03_Scripts** contains English and Hindi master stories. Voice_Directions is guidance for generating audio; it must not be spoken.', '- **04_Audio** has prepared folders. Audio files have not been generated or listened to yet.', '- **06_Database/JSON/content_library_index.json** connects each place with its files, narration, photographs and status.', '- **06_Database/JSON/content_library_audit.json** records checks, sparse galleries and remaining gaps.', '', '## Text-to-speech', '', 'For new places, pass only the English or Hindi master-story text to the text-to-speech service. Hindi text uses Devanagari. Sources, filenames and voice directions are separate from the spoken body. Listen to each generated recording and check place-name pronunciation before using it in the app.', '', 'For Taj Mahal, use taj_mahal_tts_body_english.txt and taj_mahal_tts_body_hindi.txt. These copies remove only the original heading. The original master stories are unchanged. The pilot story is longer than most new stories; the duration in the index is an estimate.', '', '## Image quality and source credits', '', 'New photographs were screened for resolution and colour, then visually reviewed for the correct place, clarity and composition. Wrong-city photographs, low-resolution images, visible watermarks, black-and-white photographs and poor images were rejected. There is no fixed photo quota: a sparse gallery is safer than adding unsuitable photographs.', '', 'Wikimedia restricted original-file downloads during collection. Existing saved originals remain unchanged. New downloads use Wikimedia’s supported high-resolution sizes, commonly 1920 or 3840 pixels wide. No photograph was enlarged. The manifest records both original dimensions and actual saved dimensions.', '', 'Use the photographer name, license and source-page link in the image manifest when showing a photograph in the application. Some preserved Taj Mahal source-record fields still say VERIFY; check these legacy fields before publication. Photo licenses are separate from factual source references.', '', '## Entries that need identity clarification', '']
    for e in library['entries']:
        if e['pending_reason']:lines.append(f'- **{e["name"]}**: {e["pending_reason"]}')
    lines+=['', 'Sri Thiruvidandhai and Nithyakalyana Perumal Temple refer to the same temple/locality. Both user-selected labels are retained. Nearby associations follow the supplied list and do not prove distance or travel time.', '', '## Coverage by group', '', '| Group | Content ready / 11 | Saved photographs | Places with photographs / 11 |', '| --- | ---: | ---: | ---: |']
    for g in library['groups']:lines.append(f'| {g["name"]} | {g["content_ready"]} | {g["image_count"]} | {g["places_with_images"]} |')
    lines+=['', '## Places without suitable saved photographs', '', 'These entries remain visible as pending in the library. They are not filled with photographs of other places.', '']
    for e in audit['image_gaps']:lines.append(f'- **{e["name"]}** ({e["group"]}): {e["reason"]}')
    lines+=['', '## Project boundary', '', 'This is the display-content library. It does not mean that the AI model recognises all listed places. The training dataset was not changed. App features, model training, authority integration and report submission still need their own implementation and testing.', '',f'All {library["totals"]["protected_original_files_unchanged"]} protected original pilot files passed the saved SHA-256 comparison.', '']
    (ROOT/'VirasatAI_Content_Library_Guide.md').write_text('\n'.join(lines),encoding='utf-8')

def build_browser(library):
    small={'totals':library['totals'],'entries':[{k:v for k,v in e.items() if k not in ['download_errors','source_urls']}|{'source_urls':e['source_urls']} for e in library['entries']]}
    template=r'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>VirasatAI · Content Library</title>
<style>:root{color-scheme:light;--ink:#20352f;--green:#245b49;--muted:#66766e;--paper:#f6f3eb}*{box-sizing:border-box}body{margin:0;font:16px/1.6 system-ui,sans-serif;background:var(--paper);color:var(--ink)}header{background:var(--green);color:white;padding:32px max(5vw,20px)}header h1{font:38px Georgia,serif;margin:0}header p{margin:4px 0;opacity:.9}.stats{display:flex;gap:28px;flex-wrap:wrap;margin-top:24px}.stats b{display:block;font-size:26px}.controls{position:sticky;top:0;background:#f6f3ebee;backdrop-filter:blur(8px);padding:20px 5vw;display:flex;gap:12px;z-index:2;border-bottom:1px solid #dadfd7}input,select,button{font:inherit;padding:10px 14px;border:1px solid #bac9be;border-radius:8px;background:white;color:var(--ink)}input{flex:1;min-width:140px}main{padding:24px 5vw}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:20px}.card{background:white;border:1px solid #e0e3d8;border-radius:12px;overflow:hidden;cursor:pointer;text-align:left;padding:0;box-shadow:0 3px 14px #20352f08}.card:hover{border-color:var(--green)}.card img,.placeholder{width:100%;height:180px;object-fit:cover;background:#e3e8df}.placeholder{display:grid;place-items:center;color:var(--muted)}.card .text{padding:16px}.card h2{font:22px/1.2 Georgia,serif;margin:5px 0 12px}.group{color:var(--muted);font-size:12px}.badge{font-size:12px;padding:3px 9px;background:#eef3e8;border-radius:20px;display:inline-block}.pending{background:#fff1d7}dialog{width:min(1100px,94vw);max-height:92vh;padding:0;border:0;border-radius:14px;color:var(--ink);background:var(--paper)}dialog::backdrop{background:#122b23aa}.detail{padding:26px}.close{float:right;position:sticky;top:12px}.detail h2{font:30px Georgia,serif;margin:0}.photos{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}.photos img{width:100%;height:190px;object-fit:contain;background:#e4e8dd;border-radius:8px}.photos figure{margin:0;background:white;padding:10px;border-radius:10px}.photos figcaption{font-size:11px;line-height:1.4;margin-top:8px;overflow-wrap:anywhere}a{color:#215b47}.script{white-space:pre-wrap;background:white;padding:22px;border-radius:10px;margin-top:12px;max-width:800px}.tabs{display:flex;gap:10px;margin-top:24px}.active{background:var(--green);color:white}.notice{padding:14px 18px;background:#fff1d7;border-radius:8px}.footer{color:var(--muted);font-size:13px;margin:30px 0}.filelinks{display:flex;gap:14px;flex-wrap:wrap}h3{font:23px Georgia,serif;margin-top:28px}@media(max-width:650px){.controls{flex-wrap:wrap;padding:12px}.controls select{max-width:45%}.stats{gap:18px}.detail{padding:18px}}</style>
<header><h1>VirasatAI</h1><p>Heritage photographs & stories · Saved content library</p><div class="stats" id="stats"></div></header><div class="controls"><input id="search" type="search" placeholder="Search a monument or nearby place" aria-label="Search places"><select id="group" aria-label="Monument group"><option value="">All monument groups</option></select><select id="status" aria-label="Photo availability"><option value="">All places</option><option value="photos">With photos</option><option value="pending">Photos pending</option><option value="main">Main monuments</option></select></div><main><p id="count"></p><div class="grid" id="cards"></div><p class="footer">Display photographs and prepared narration scripts. Audio is not generated. Model recognition is a separate project step. <a href="VirasatAI_Content_Library_Guide.md">Read the library guide</a>.</p></main><dialog id="dialog"><div class="detail"><button class="close" id="close">Close ×</button><div id="detail"></div></div></dialog>
<script>const library=__DATA__;const $=s=>document.querySelector(s),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),link=(p,label)=>p?`<a href="${encodeURI(p)}" target="_blank" rel="noopener">${esc(label)}</a>`:'';
const t=library.totals;$('#stats').innerHTML=[[t.main_groups,'main groups'],[t.content_ready,'places with stories'],[t.display_images,'saved photographs'],[t.places_without_images,'photo galleries pending']].map(([v,n])=>`<div><b>${v}</b>${n}</div>`).join('');
const groups=[...new Set(library.entries.map(e=>e.group_name))];groups.forEach(g=>$('#group').add(new Option(g,g)));
function render(){const q=$('#search').value.toLowerCase(),g=$('#group').value,s=$('#status').value;const entries=library.entries.filter(e=>(!q||(e.name+' '+e.group_name).toLowerCase().includes(q))&&(!g||e.group_name===g)&&(!s||s==='photos'&&e.image_count||s==='pending'&&!e.image_count||s==='main'&&e.is_main));$('#count').textContent=entries.length+' places shown';$('#cards').innerHTML=entries.map(e=>`<button class="card" data-id="${e.id}">${e.images[0]?`<img src="${encodeURI(e.images[0].local_path)}" alt="${esc(e.name)}" loading="lazy">`:'<div class="placeholder">Suitable photograph pending</div>'}<div class="text"><span class="group">${esc(e.group_name)} ${e.is_main?'· Main monument':''}</span><h2>${esc(e.name)}</h2><span class="badge ${e.image_count?'':'pending'}">${e.image_count?e.image_count+' photos':'Photos pending'}</span> <span class="badge ${e.pending_reason?'pending':''}">${e.pending_reason?'Identity pending':'English + Hindi stories'}</span></div></button>`).join('');document.querySelectorAll('.card').forEach(c=>c.onclick=()=>show(c.dataset.id))}
function show(id){const e=library.entries.find(x=>x.id===id);$('#detail').innerHTML=`<p class="group">${esc(e.group_name)}</p><h2>${esc(e.name)}</h2><p>${e.image_count} photographs · ${e.pending_reason?'Identity pending':e.english_words+' English words · approx. '+e.estimated_english_seconds_at_130_wpm+' seconds'}</p>${e.pending_reason?`<p class="notice">${esc(e.pending_reason)}</p>`:''}${e.coverage_note?`<p class="notice">${esc(e.coverage_note)}</p>`:''}<div class="filelinks">${link(e.files.basic,'Basic information')}${link(e.files.facts,'Facts')}${link(e.files.sources,'Research sources')}${link(e.files.voice_directions,'Voice directions')}</div><h3>Photographs</h3><div class="photos">${e.images.map(im=>`<figure>${link(im.local_path, '').replace('></a>',`><img src="${encodeURI(im.local_path)}" alt="${esc(e.name)}" loading="lazy"></a>`)}<figcaption>${im.author?esc(im.author)+' · '+esc(im.license)+'<br>'+link(im.source_page,'Wikimedia source')+' · '+link(im.license_url,'License'):link(im.source_record,'Original source record · verify legacy credits')}<br>${im.downloaded_width} × ${im.downloaded_height}</figcaption></figure>`).join('')||'<p>Suitable photographs have not been saved for this place.</p>'}</div>${e.narration.english?'<h3>Narration</h3><div class="tabs"><button id="english" class="active">English</button><button id="hindi">हिन्दी</button></div><p id="scriptfile"></p><div id="script" class="script"></div>':''}<h3>Factual references</h3>${e.source_urls.map(u=>`<p>${link(u,u)}</p>`).join('')}`;if(e.narration.english){const language=l=>{$('#script').textContent=e.narration[l];$('#scriptfile').innerHTML=link(e.files[l],'Open plain narration text');$('#english').classList.toggle('active',l==='english');$('#hindi').classList.toggle('active',l==='hindi')};$('#english').onclick=()=>language('english');$('#hindi').onclick=()=>language('hindi');language('english')}$('#dialog').showModal();$('#dialog').scrollTop=0}
$('#close').onclick=()=>$('#dialog').close();$('#dialog').onclick=e=>{if(e.target===$('#dialog'))$('#dialog').close()};['search','group','status'].forEach(id=>$('#'+id).addEventListener(id==='search'?'input':'change',render));render();</script></html>'''
    (ROOT/'VirasatAI_Content_Library.html').write_text(template.replace('__DATA__',json.dumps(small,ensure_ascii=False).replace('</',r'<\/')),encoding='utf-8')

def build_overview(library):
    canvas=Image.new('RGB',(1600,1200),'#f6f3eb'); draw=ImageDraw.Draw(canvas)
    title=ImageFont.truetype(r'C:\Windows\Fonts\georgia.ttf',36); label=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',17)
    draw.text((30,16),'VirasatAI · Saved monument photographs',font=title,fill='#20352f')
    draw.text((30,62),'20 selected main groups · Nearby galleries are available in the content library',font=label,fill='#66766e')
    for i,e in enumerate(x for x in library['entries'] if x['is_main']):
        x=(i%5)*320+10;y=(i//5)*275+108
        if e['images']:
            with Image.open(ROOT/e['images'][0]['local_path']) as im:
                thumb=ImageOps.contain(ImageOps.exif_transpose(im).convert('RGB'),(300,215))
                canvas.paste(thumb,(x+(300-thumb.width)//2,y+(215-thumb.height)//2))
        else: draw.text((x+15,y+75),'Photos pending',font=label,fill='#66766e')
        name=e['name'].split(',')[0]
        draw.text((x+8,y+224),name if len(name)<30 else name[:28]+'…',font=label,fill='#20352f')
    canvas.save(ROOT/'VirasatAI_Monuments_Preview.jpg',quality=93)

def record_context(library):
    path=ROOT/'VirasatAI_Project_Context.txt'
    original=path.read_bytes()
    marker=b'\n==================================================\n66. CONTENT LIBRARY STATUS - 8 OCTOBER 2026\n'
    parts=original.split(marker,1)
    before=parts[0].rstrip(b'\r\n')
    later=b''
    if len(parts)==2:
        following=re.search(rb'\r?\n={10,}\r?\n(?:6[7-9]|[7-9][0-9]|[0-9]{3,})\. ',parts[1])
        if following: later=parts[1][following.start():]
    t=library['totals']
    body=f'''\n==================================================
66. CONTENT LIBRARY STATUS - 8 OCTOBER 2026
==================================================

Current workspace: C:\\Desktop\\VirasatAI. Older project paths above are historical.

The latest collection scope is the exact approved 20 main groups and 200 nearby entries. The selected names, order and parent associations remain unchanged.

Written content:
- {t['content_ready']} of 220 entries have Basic_Info, Facts, Story_Data, Sources, English and Hindi narration, and Voice_Directions.
- {t['english_scripts']} English and {t['hindi_scripts']} Hindi spoken bodies are available. Hindi uses Devanagari. The original Taj stories are preserved; heading-free TTS copies are added separately.
- Hathni Kund needs exact Jaipur site verification before a factual story or gallery is prepared.
- Galaganatha Temples remains identity pending by the user's explicit answer. Do not silently choose Aihole or Pattadakal.
- Sources are separate from spoken text. Dates, access, prices and distances must not be invented.

Display photographs recorded in the current library:
- {t['display_images']} saved images across {t['places_with_images']} entries, including the original 40 Taj photographs.
- {t['places_without_images']} entries currently have no suitable saved photograph. Read content_library_audit.json and the library guide for the actual gaps; do not treat rejected or unreviewed cached candidates as application assets.
- New photos are visually reviewed for correct-site identity and clarity. Original and downloaded dimensions, source page, photographer, license and hash are recorded.
- Wikimedia limited original-file downloads. Supported high-resolution image sizes are used without enlarging images. Existing downloaded originals remain preserved.
- All {t['protected_original_files_unchanged']} originally protected pilot files pass their saved SHA-256 checks. Legacy Taj source-record VERIFY fields remain a publication check.

Useful outputs:
VirasatAI_Content_Library.html — local searchable photo/story browser.
VirasatAI_Content_Library_Guide.md — simple English usage and gap guide.
06_Database/JSON/content_library_index.json — actual content paths, narration, image metadata and status.
06_Database/JSON/content_library_audit.json — integrity checks, gaps and sparse-gallery notes.
tools/image_review/narration_completeness_qa.json — narration completeness and formatting checks.

Important identities:
- Bateshwar is the Agra/Yamuna Uttar Pradesh site, not Morena Madhya Pradesh.
- Sagar Lake is the reservoir behind Amer, not Man Sagar/Jal Mahal.
- Sunehri Masjid is the 1751 Qudsia Begum mosque near Red Fort, not the other Delhi mosques with similar names.
- Hayat Bakshi Mosque means Hayathnagar, not the funerary mosque at Qutb Shahi Tombs.
- Neelkantheshwar is Udayesvara/Nilkanthesvara at Udaipur village, Vidisha, Madhya Pradesh.
- Karni Mata Temple and Vintage Car Museum in this list mean Udaipur, Rajasthan.
- Nithyakalyana Perumal Temple and Sri Thiruvidandhai refer to the same temple/locality. Both supplied labels are retained; this is not an extra distinct model class.
- Chausathi Yogini means Hirapur, Odisha. Ajanta and Ellora retain one approved main-group label.

Project implementation boundary:
This work prepares application display content. It does not establish trained-model support for 20 groups or 200 nearby entries. 05_AI_Dataset is separate and was not changed. Audio has not been generated or auditioned. The Flutter app, CNN training, cleanliness detection, authority integration and problem-report workflow still require their own implementation and testing. Continue those steps only under the user's subsequent instructions.
'''
    path.write_bytes(before+body.encode('utf-8')+later)

if __name__=='__main__': main()
