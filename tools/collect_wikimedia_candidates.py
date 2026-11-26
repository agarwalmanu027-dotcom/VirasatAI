"""Collect public Commons candidates and commit only explicitly reviewed selections."""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, html, io, json, re, threading, time, urllib.parse, urllib.request
from datetime import date
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(r'C:\Desktop\VirasatAI').resolve()
REVIEW = ROOT / 'tools' / 'image_review'
CATALOG = ROOT / '06_Database' / 'JSON' / 'monuments_places_catalog.json'
API = 'https://commons.wikimedia.org/w/api.php'
UA = 'VirasatAIStudentHeritage/1.0 (public Wikimedia Commons gallery research)'
LOCK = threading.Lock()
LAST_REQUEST = 0.0
CITY = {
 'taj_mahal':'Agra','qutub_minar':'Delhi','amer_fort':'Jaipur','red_fort':'Delhi',
 'gateway_of_india':'Mumbai','charminar':'Hyderabad','victoria_memorial':'Kolkata',
 'mysore_palace':'Mysore','hampi_monuments':'Hampi','meenakshi_temple':'Madurai',
 'golden_temple':'Amritsar','khajuraho_monuments':'Khajuraho','ajanta_ellora_caves':'Aurangabad',
 'konark_sun_temple':'Odisha','sanchi_stupa':'Vidisha','city_palace_udaipur':'Udaipur',
 'mahabalipuram':'Tamil Nadu','jaisalmer_fort':'Jaisalmer','mehrangarh_fort':'Jodhpur','badami_cave_temples':'Badami'}
ALIASES = {
 'Qutub Minar, Delhi':['Qutb Minar','Qutub Minar'],
 'Amer Fort, Jaipur':['Amber Fort','Amer Fort'],
 'Red Fort, Delhi':['Red Fort Delhi','Lal Qila Delhi'],
 'Gateway of India, Mumbai':['Gateway of India'],
 'Charminar, Hyderabad':['Charminar'],
 'Victoria Memorial, Kolkata':['Victoria Memorial Kolkata','Victoria Memorial Calcutta'],
 'Mysore Palace, Mysuru':['Mysore Palace','Amba Vilas Palace'],
 'Hampi Monuments, Karnataka':['Hampi monuments','Hampi temples','Vittala Temple Hampi'],
 'Meenakshi Temple, Madurai':['Meenakshi Temple','Meenakshi Amman Temple'],
 'Golden Temple, Amritsar':['Golden Temple Amritsar','Harmandir Sahib'],
 'Khajuraho Monuments, Madhya Pradesh':['Khajuraho temples','Khajuraho monuments'],
 'Ajanta & Ellora Caves, Maharashtra':['Ajanta Caves','Ellora Caves'],
 'Konark Sun Temple, Odisha':['Konark Sun Temple','Konark temple'],
 'Sanchi Stupa, Madhya Pradesh':['Sanchi Stupa','Sanchi monuments'],
 'City Palace, Udaipur':['City Palace Udaipur'],
 'Mahabalipuram, Tamil Nadu':['Mahabalipuram monuments','Shore Temple','Pancha Rathas'],
 'Jaisalmer Fort, Rajasthan':['Jaisalmer Fort'],
 'Mehrangarh Fort, Jodhpur':['Mehrangarh Fort','Mehrangarh'],
 'Badami Cave Temples, Karnataka':['Badami cave temples','Badami caves'],
 'The Red Taj (Hessing\'s Tomb)':['Hessing Tomb','Hessing\'s Tomb','Red Taj'],
 'Mariam-uz-Zamani Tomb':['Mariam Tomb Agra','Mariam-uz-Zamani Tomb'],
 'Jaswant Singh Ki Chhatri':['Jaswant Singh-ki-Chattri','Jaswant ki Chhatri Agra'],
 'Gurudwara Guru Ka Taal':['Guru ka Taal','Guru ka Tal'],
 'Bateshwar Temples':['Bateshwar Agra','Bateshwar Yamuna','Bateshwar Uttar Pradesh'],
 'Sunehri Masjid':['Sunehri Masjid Qudsia','Sunehri Masjid 1751','Sunehri Masjid Red Fort'],
 'St. James\' Church':['St James Church Delhi','St James Church Kashmere Gate','Skinner Church Delhi'],
 'Chunnamal Haveli':['Chunnamal Haveli','Chunna Mal Haveli'],
 'Naughara (Kinari Bazaar)':['Naughara','Nau Ghar Delhi','Naughara Delhi'],
 'Rajon Ki Baoli':['Rajon ki Baoli','Rajon ki Bain'],
 'Hijron Ka Khanqah':['Hijron ka Khanqah'],
 'Gaitore Ki Chhatriyan':['Gaitore','Gaitor cenotaphs'],
 'Sagar Lake':['Sagar Lake Amer','Amer Sagar','Sagar reservoir Amber'],
 'Vidyadhar Garden':['Vidyadhar Garden','Vidhyadhar Garden','Vidyadhar Bagh'],
 'Anokhi Museum':['Anokhi Museum'],
 'Hathni Kund':['Hathni Kund Jaipur'],
 'Keneseth Eliyahoo Synagogue':['Keneseth Eliyahoo Synagogue','Knesset Eliyahoo Synagogue'],
 'Ballard Bunder Gatehouse':['Ballard Bunder Gatehouse','Ballard Bunder'],
 'RBI Monetary Museum':['RBI Monetary Museum','Reserve Bank Monetary Museum'],
 'Bhau Daji Lad Museum':['Bhau Daji Lad Museum','Dr. Bhau Daji Lad Museum'],
 'Khursheed Jah Devdi':['Khursheed Jah Devdi','Khurshid Jah Devdi'],
 'Nipponzan Myohoji Temple':['Nipponzan Myohoji Kolkata'],
 'Jorasanko Thakur Bari':['Jorasanko Thakur Bari','Jorasanko Thakurbari'],
 'Railway Museum Mysore':['Railway Museum Mysore','Mysore Railway Museum'],
 'Melody World Wax Museum':['Melody World Wax Museum','Mysore Wax Museum'],
 'Kishkindha Moolika Bonsai Garden':['Kishkindha Moolika','Mysore Bonsai Garden'],
 'St. Philomena\'s Church Crypt':['St Philomena crypt','St Philomena catacomb'],
 'Karanji Lake Aviary':['Karanji Lake aviary','Karanji aviary'],
 'Badavilinga Temple':['Badavilinga','Badavi Linga'],
 'Sasivekalu Ganesha':['Sasivekalu Ganesha','Sasivekalu Ganesh'],
 'Palamuthirsolai Murugan Temple':['Pazhamudircholai','Pazhamudhirsolai'],
 'Yanaimalai':['Yanaimalai','Yanamalai'],
 'Gurdwara Mata Kaulan':['Gurdwara Mata Kaulan','Kaulsar'],
 'Saragarhi Memorial':['Saragarhi Memorial Amritsar','Saragarhi Gurudwara Amritsar'],
 'Ken Gharial Sanctuary':['Ken Gharial Sanctuary'],
 'Beni Sagar Dam':['Beni Sagar Dam','Benisagar'],
 'Grishneshwar Jyotirlinga':['Grishneshwar Temple','Ghrishneshwar'],
 'Bhadra Maruti Temple':['Bhadra Maruti Temple','Bhadra Maruti'],
 'Kuruma Buddhist Site':['Kuruma Odisha','Kuruma Buddhist'],
 'Barahi Temple (Chaurasi)':['Varahi Temple Chaurasi','Barahi Temple Chaurasi'],
 'Chausathi Yogini Temple':['Chausathi Yogini Hirapur','Chausath Yogini Hirapur'],
 'Mangalajodi (Chilika)':['Mangalajodi'],
 'Neelkantheshwar Temple':['Udayeshwara Temple','Udayesvara Temple Vidisha','Neelkantheshwar Vidisha'],
 'Sajjangarh (Monsoon Palace)':['Sajjangarh','Monsoon Palace Udaipur'],
 'Badi Lake':['Badi Lake','Badi Talab'],
 'Nithyakalyana Perumal Temple':['Nithya Kalyana Perumal Temple','Thiruvidanthai temple'],
 'Sri Thiruvidandhai':['Thiruvidanthai','Thiruvidandhai'],
 'Bhutanatha Group of Temples':['Bhutanatha Badami','Bhutanatha temples'],
 'Aihole (Durga Temple)':['Durga temple Aihole'],
 'Ravan Phadi Cave':['Ravana Phadi','Ravanaphadi'],
 'Banashankari Amma Temple':['Banashankari temple Badami'],
}
AMBIGUOUS_GEO = {
 'Ram Bagh':['agra','aram bagh'], 'Ram Bagh Palace':['amritsar','ranjit singh'],
 'Bateshwar Temples':['agra','yamuna','uttar pradesh'],
 'Sagar Lake':['amer','amber'],
 'Sunehri Masjid':['qudsia','1751','red fort','delhi gate'], 'Armenian Church':['kolkata','calcutta'],
 'St. James\' Church':['delhi','kashmere','skinner'],
 'Jain Museum':['khajuraho'], 'Gun House':['mysore','mysuru'],
 'Hathni Kund':['jaipur'], 'Neelkantheshwar Temple':['vidisha','udayesh','udayes','udaipur madhya'],
 'St. Philomena\'s Church Crypt':['crypt','catacomb'], 'Karanji Lake Aviary':['aviary'],
}
IDENTITY_HOLD = {'Galaganatha Temples','Hathni Kund'}
EXACT_FILES = {
 'Jaswant Singh Ki Chhatri':['File:Jaswant Singh-ki-Chattri.jpg'],
 'Bateshwar Temples':['File:BATESHWAR NATH JI.jpg','File:GOURI SHANKAR TEMPLE BATESHWAR.jpg'],
 'Garh Ganesh Temple':['File:Jaipur 03-2016 38 Garh Ganesh Temple.jpg','File:Staircase leading to Garh Ganesh Temple, Jaipur.jpg','File:Staircase to Garh Ganesh Temple.jpg'],
 'Sunehri Masjid':['File:Sunahri Masjid 02.jpg','File:Sunahri Masjid 04.jpg','File:Sunahri Masjid 05.jpg','File:Sunahri Masjid 10.jpg','File:Sunahri Masjid 11.jpg'],
 'St. James\' Church':["File:St. James' Church, Delhi, India.jpg","File:St James' Church, Kashmiri Gate, Delhi, India.jpg","File:Skinner's Church 1.jpg","File:Skinner's Church 2.jpg","File:Delhi, Saint James Church.JPG","File:James Skinner tomb (St James, Delhi).JPG"],
}
EXACT_CATEGORIES = {}
EXTRA_SEARCH = {
 'red_fort':['Lahori Gate Delhi','Diwan-i-Am Red Fort Delhi','Diwan-i-Khas Red Fort Delhi','Moti Masjid Red Fort Delhi'],
 'amer_fort':['Sheesh Mahal Amer','Ganesh Pol Amber','Diwan-e-Aam Amber'],
}
UNSUITABLE = re.compile(r'\b(map|plan|drawing|engraving|lithograph|postcard|stamp|coin|painting|watercolour|watercolor|sketch|logo|flag|diagram|black.and.white|sepia|selfie|portrait)\b', re.I)
FONT = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 20)
SMALL = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 16)

def safe(path: Path) -> Path:
    path = path.resolve()
    if ROOT != path and ROOT not in path.parents: raise ValueError('Path outside project')
    return path

def dump(path: Path, value):
    safe(path).parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(path)

def clean(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', value or ''))).strip()

def norm(value):
    return re.sub(r'[^a-z0-9]+', ' ', clean(value).lower()).strip()

def fetch(url, timeout=40):
    global LAST_REQUEST
    for attempt in range(4):
        with LOCK:
            delay = (2.5 if url.startswith(API) else .6) - (time.monotonic() - LAST_REQUEST)
            if delay > 0: time.sleep(delay)
            LAST_REQUEST = time.monotonic()
        try:
            req = urllib.request.Request(url, headers={'User-Agent':UA})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read()
        except Exception as error:
            code = getattr(error, 'code', None)
            if code == 404: raise
            if code == 429:
                if not url.startswith(API) or attempt==3: raise
                retry=int(getattr(error,'headers',{}).get('Retry-After','30'))
                if retry>60: raise
                time.sleep(max(30,retry));continue
            if attempt == 3: raise
            time.sleep(min(12, 2 ** (attempt + 1)))

def query(search):
    params = {'action':'query','format':'json','generator':'search','gsrnamespace':6,
              'gsrsearch':search,'gsrlimit':45,'prop':'imageinfo',
              'iiprop':'url|size|mime|extmetadata|sha1','iiurlwidth':1280}
    data = json.loads(fetch(API + '?' + urllib.parse.urlencode(params)))
    return sorted(data.get('query',{}).get('pages',{}).values(), key=lambda p:p.get('index',9999))

def relevance(place, metadata, aliases):
    name = place['display_name']
    text = norm(metadata['title'] + ' ' + metadata['description'])
    if UNSUITABLE.search(metadata['title']): return False
    meaningful = {'temple','temples','tomb','mosque','church','fort','lake','garden','gardens','palace','museum','village','group','of','the','india','monuments','caves','cave','memorial','ki','ka','and','sri','st'}
    matches = False
    for alias in aliases:
        phrase = norm(alias)
        tokens = [t for t in phrase.split() if t not in meaningful]
        if phrase and phrase in text: matches = True; break
        if len(tokens) >= 2 and sum(t in text.split() for t in tokens) >= min(2,len(tokens)):
            matches = True; break
        if len(tokens) == 1 and len(tokens[0]) >= 6 and tokens[0] in text.split():
            matches = True; break
    if not matches: return False
    required = AMBIGUOUS_GEO.get(name)
    if required and not any(norm(x) in text for x in required): return False
    return True

def metadata(page):
    info = page.get('imageinfo',[{}])[0]
    ext = info.get('extmetadata',{})
    val = lambda key: clean(ext.get(key,{}).get('value',''))
    license_name, artist = val('LicenseShortName'), val('Artist')
    return {'title':page.get('title',''),'source_page':info.get('descriptionurl',''),
       'original_url':info.get('url',''),'preview_url':info.get('thumburl',info.get('url','')),
       'original_width':info.get('width',0),'original_height':info.get('height',0),
       'mime':info.get('mime',''),'license':license_name,'license_url':val('LicenseUrl'),
       'author':artist,'credit':val('Credit'),'attribution':val('Attribution'),
       'description':val('ImageDescription'),'date_time_original':val('DateTimeOriginal'),
       'sha1':info.get('sha1',''),'commons_assessment':val('Assessments'),
       'copyrighted':val('Copyrighted'),'usage_terms':val('UsageTerms')}

def quality(raw):
    with Image.open(io.BytesIO(raw)) as source:
        image = ImageOps.exif_transpose(source).convert('RGB')
        image.thumbnail((512,512),Image.Resampling.LANCZOS)
        arr = np.asarray(image, dtype=np.float32)
        color = float((abs(arr[:,:,0]-arr[:,:,1])+abs(arr[:,:,1]-arr[:,:,2])+abs(arr[:,:,0]-arr[:,:,2])).mean()/3)
        grey = arr.mean(axis=2)
        lap = -4*grey[1:-1,1:-1]+grey[2:,1:-1]+grey[:-2,1:-1]+grey[1:-1,2:]+grey[1:-1,:-2]
        sharp = float(lap.var())
        small = np.asarray(image.convert('L').resize((9,8)), dtype=np.int16)
        dhash = 0
        for bit in (small[:,1:] > small[:,:-1]).flatten(): dhash = (dhash<<1)|int(bit)
        return {'color_score':round(color,2),'sharpness_score':round(sharp,2),'dhash':format(dhash,'016x')}

def collect(place, main, force=False, supplement=False):
    out = REVIEW/'candidates'/place['id']
    meta_path = out/'candidates.json'
    if meta_path.exists() and not force and not supplement: return json.loads(meta_path.read_text(encoding='utf-8'))
    name = place['display_name']
    result = {'place_id':place['id'],'display_name':name,'parent_id':main['id'],'main_order':main['order'],
              'is_main':place['id']==main['id'],'candidates':[],'errors':[],'visual_review_status':'pending'}
    if supplement and meta_path.exists(): result=json.loads(meta_path.read_text(encoding='utf-8'))
    existing_titles={c['title'] for c in result['candidates']}
    if name in IDENTITY_HOLD:
        result['status']='identity_confirmation_required'; dump(meta_path,result); return result
    aliases = ALIASES.get(name,[name.split(',')[0], re.sub(r'\([^)]*\)','',name).strip()])
    aliases = list(dict.fromkeys(aliases))
    searches = aliases[:3]
    if name not in ALIASES: searches = [f'"{aliases[0]}"',f'{aliases[-1]} {CITY[main["id"]]}']
    else: searches = [f'"{x}"' if len(x.split())>1 else x for x in searches]
    if supplement: searches=EXTRA_SEARCH.get(place['id'],searches)
    pages, seen = [], {c['title'] for c in result['candidates']}
    if name in EXACT_FILES:
        params={'action':'query','format':'json','titles':'|'.join(EXACT_FILES[name]),'prop':'imageinfo','iiprop':'url|size|mime|extmetadata|sha1','iiurlwidth':1280}
        data=json.loads(fetch(API+'?'+urllib.parse.urlencode(params)))
        pages=list(data.get('query',{}).get('pages',{}).values())
        searches=[]
    elif name in EXACT_CATEGORIES:
        for category in EXACT_CATEGORIES[name]:
            params={'action':'query','format':'json','generator':'categorymembers','gcmtitle':category,'gcmnamespace':6,'gcmlimit':50,'prop':'imageinfo','iiprop':'url|size|mime|extmetadata|sha1','iiurlwidth':1280}
            data=json.loads(fetch(API+'?'+urllib.parse.urlencode(params)))
            pages.extend(data.get('query',{}).get('pages',{}).values())
        searches=[]
    for search in searches:
        try:
            for page in query(search):
                if page['title'] not in seen: pages.append(page); seen.add(page['title'])
        except Exception as error: result['errors'].append(str(error))
    screened=[]
    for page in pages:
        m=metadata(page)
        if m['title'] in existing_titles: continue
        w,h=m['original_width'],m['original_height']
        if m['mime'] not in ('image/jpeg','image/png','image/webp'): continue
        if max(w,h)<1600 or min(w,h)<800 or not (.38 <= w/h <= 2.8): continue
        if not m['source_page'] or not m['original_url'] or not m['license'] or not m['author']: continue
        if not any(x in m['license'].lower() for x in ('cc','public domain','pd','free art','fal','attribution')): continue
        if name not in EXACT_FILES and name not in EXACT_CATEGORIES and not relevance(place,m,aliases): continue
        screened.append(m)
    limit = (len(result['candidates'])+24) if supplement else (32 if result['is_main'] else 10)
    fingerprints=[int(c['dhash'],16) for c in result['candidates']]
    for m in screened:
        if len(result['candidates'])>=limit: break
        try:
            raw=fetch(m['preview_url'])
            q=quality(raw)
            if q['color_score']<3.5 or q['sharpness_score']<18: continue
            signature=int(q['dhash'],16)
            if any((signature^other).bit_count()<=5 for other in fingerprints): continue
            fingerprints.append(signature)
            rank=len(result['candidates'])+1
            file=out/f'candidate_{rank:02d}.jpg'
            file.parent.mkdir(parents=True,exist_ok=True)
            # Preserve the downloaded preview bytes; extension follows decoded format below.
            with Image.open(io.BytesIO(raw)) as im:
                if im.format=='PNG': file=file.with_suffix('.png')
                elif im.format=='WEBP': file=file.with_suffix('.webp')
            file.write_bytes(raw)
            m.update(q);m['candidate_id']=rank;m['preview_path']=str(file.relative_to(ROOT)).replace('\\','/')
            result['candidates'].append(m)
        except Exception as error: result['errors'].append(f'{m["title"]}: {error}')
    result['status']='candidates_collected' if result['candidates'] else 'no_qualifying_candidates'
    dump(meta_path,result)
    return result

def wrapped(text,width=34):
    words=text.split(); lines=[]; line=''
    for word in words:
        if len(line)+len(word)+1>width: lines.append(line);line=word
        else: line=(line+' '+word).strip()
    if line: lines.append(line)
    return lines

def sheets(records):
    target=REVIEW/'contact_sheets';target.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for order in range(1,21):
        group=[r for r in records if r['main_order']==order]
        for kind in ('main','nearby'):
            subset=[r for r in group if r['is_main']==(kind=='main')]
            tiles=[(r,c) for r in subset for c in r['candidates']]
            for start in range(0,len(tiles),24):
                batch=tiles[start:start+24];cols=4;rows=(len(batch)+cols-1)//cols
                canvas=Image.new('RGB',(1600,70+rows*330),(245,245,245));draw=ImageDraw.Draw(canvas)
                draw.text((15,15),f'Group {order:02d} - {kind} - page {start//24+1} | Candidate numbers; original resolution in label',font=FONT,fill='black')
                for k,(r,c) in enumerate(batch):
                    x=(k%cols)*400;y=70+(k//cols)*330
                    with Image.open(ROOT/c['preview_path']) as im:
                        thumb=ImageOps.contain(ImageOps.exif_transpose(im).convert('RGB'),(390,230))
                        canvas.paste(thumb,(x+(400-thumb.width)//2,y))
                    label=f'{r["display_name"]} | #{c["candidate_id"]} | {c["original_width"]}x{c["original_height"]}'
                    for j,line in enumerate(wrapped(label,45)[:3]): draw.text((x+7,y+234+j*20),line,font=SMALL,fill='black')
                    draw.text((x+7,y+299),f'Sharp {c["sharpness_score"]:.0f} / color {c["color_score"]:.1f}',font=SMALL,fill='black')
                file=target/f'group_{order:02d}_{kind}_{start//24+1:02d}.jpg';canvas.save(file,quality=93)
                manifest.append({'path':str(file.relative_to(ROOT)).replace('\\','/'),'order':order,'kind':kind,'items':[{'id':r['place_id'],'candidate':c['candidate_id']} for r,c in batch]})
    dump(REVIEW/'contact_sheets_manifest.json',manifest)
    return manifest

def commit(records,selection,workers=4,progress_name='download_progress.json'):
    catalog=json.loads(CATALOG.read_text(encoding='utf-8-sig'))
    places={p['id']:p for m in catalog['main_monuments'] for p in [m,*m['nearby_places']]}
    by_id={r['place_id']:r for r in records};outputs=[]
    def download_one(place, c, choice, number):
        if choice.get('reviewed_source_title') and choice['reviewed_source_title']!=c['title']:
            raise ValueError('Reviewed source title no longer matches candidate; fresh visual review required')
        if choice.get('reviewed_source_sha1') and choice['reviewed_source_sha1']!=c['sha1']:
            raise ValueError('Reviewed source content changed; fresh visual review required')
        category=choice.get('category','Overview')
        if category not in {'Front','Back','East','West','North','South','Aerial','Details','Surroundings','Overview','Different_Views'}: raise ValueError('Invalid category')
        out=safe(ROOT/place['paths']['images']/category);out.mkdir(parents=True,exist_ok=True)
        ext={'image/jpeg':'.jpg','image/png':'.png','image/webp':'.webp'}[c['mime']]
        file=out/f'{place["folder_name"].lower()}_{category.lower()}_{number:02d}{ext}'
        downloaded_url=c['original_url'];download_kind='original'
        if file.exists():
            prior=None
            previous_path=ROOT/place['paths']['images']/'Image_Sources'/'image_manifest.json'
            if previous_path.exists():
                previous=json.loads(previous_path.read_text(encoding='utf-8'))
                prior=next((x for x in previous.get('images',[]) if (ROOT/x['local_path']).resolve()==file.resolve()),None)
                if prior and (prior['title']!=c['title'] or prior.get('sha1')!=c['sha1']):
                    raise ValueError('Existing file belongs to another source; refusing to relabel it')
            raw=file.read_bytes();download_kind='existing_verified_file'
            if prior:
                downloaded_url=prior.get('downloaded_url',downloaded_url)
                download_kind=prior.get('download_kind',download_kind)
        else:
            # Use Commons' documented common thumbnail steps; original downloads
            # were explicitly limited by Wikimedia. Do not upscale a photograph.
            step=next(s for s in (3840,1920,1280,960,500) if s<=c['original_width'])
            downloaded_url=re.sub(r'/\d+px-',f'/{step}px-',c['preview_url'])
            if '/thumb/' not in downloaded_url:
                original=urllib.parse.urlsplit(c['original_url']);name=original.path.rsplit('/',1)[-1]
                path=original.path.replace('/commons/','/commons/thumb/')+f'/{step}px-'+name
                if c['mime']=='image/webp': path+='.jpg'
                downloaded_url=urllib.parse.urlunsplit(('https','thumb.wikimedia.org',path,'',''))
            raw=fetch(downloaded_url,timeout=90);download_kind='commons_standard_high_resolution'
        with Image.open(io.BytesIO(raw)) as im:
            w,h=im.size
            if im.format not in {'JPEG','PNG','WEBP'} or w>c['original_width'] or h>c['original_height'] or min(w,h)<700 or max(w,h)<1200: raise ValueError('Downloaded image resolution/format fails quality requirements')
            ext={'JPEG':'.jpg','PNG':'.png','WEBP':'.webp'}[im.format]
            file=file.with_suffix(ext)
            im.verify()
        if downloaded_url==c['original_url'] and (w,h)!=(c['original_width'],c['original_height']):
            original=urllib.parse.urlsplit(c['original_url']);name=original.path.rsplit('/',1)[-1]
            path=original.path.replace('/commons/','/commons/thumb/')+f'/{w}px-'+name
            if c['mime']=='image/webp': path+='.jpg'
            downloaded_url=urllib.parse.urlunsplit(('https','thumb.wikimedia.org',path,'',''))
            download_kind='commons_standard_high_resolution'
        if file.exists():
            if hashlib.sha256(file.read_bytes()).digest()!=hashlib.sha256(raw).digest(): raise ValueError('Refusing to replace a different image')
        else: file.write_bytes(raw)
        m=dict(c);m.pop('preview_url',None);m.pop('preview_path',None);m['local_path']=str(file.relative_to(ROOT)).replace('\\','/')
        m['sha256']=hashlib.sha256(raw).hexdigest();m['visual_review_status']='visually_reviewed'
        m['downloaded_width']=w;m['downloaded_height']=h;m['downloaded_url']=downloaded_url;m['download_kind']=download_kind
        m['review_note']=choice.get('review_note','Relevant subject and acceptable clarity checked in contact sheet; original resolution verified.')
        return m
    for entry in selection:
        id=entry['place_id'];record=by_id[id];place=places[id]
        if entry.get('review_status')!='visually_reviewed': raise ValueError('Selection lacks visual review: '+id)
        selected=[]
        download_errors=[]
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            pending=[pool.submit(download_one,place,next(x for x in record['candidates'] if x['candidate_id']==choice['candidate_id']),choice,number) for number,choice in enumerate(entry.get('selected',[]),1)]
            for number,future in enumerate(pending,1):
                try: selected.append(future.result())
                except Exception as error:
                    download_errors.append({'selection_number':number,'error':str(error)})
                    print(json.dumps({'download_failed_place':id,'selection_number':number,'error':str(error)}),flush=True)
        manifest={'place_id':id,'display_name':place['display_name'],'checked_on':date.today().isoformat(),
                  'source':'Wikimedia Commons','images':selected,'download_errors':download_errors,'coverage_note':entry.get('coverage_note','')}
        metadata_dir=safe(ROOT/place['paths']['images']/'Image_Sources');metadata_dir.mkdir(parents=True,exist_ok=True)
        dump(metadata_dir/'image_manifest.json',manifest)
        lines=['VIRASATAI - WIKIMEDIA IMAGE SOURCE RECORD',place['display_name'],'',
               'High-resolution color photographs. Downloaded and original dimensions recorded separately. Photographer and license copied from Commons metadata.',
               'Check each linked file page for complete license conditions before reuse.','']
        for n,m in enumerate(selected,1):
            lines.extend([f'{n:02d}. {m["title"]}',f'Local file: {m["local_path"]}',f'Downloaded size: {m["downloaded_width"]} x {m["downloaded_height"]}',f'Original size: {m["original_width"]} x {m["original_height"]}',
              f'Photographer/artist: {m["author"]}',f'License: {m["license"]}',f'License link: {m["license_url"]}',
              f'Commons file page: {m["source_page"]}',f'Downloaded image: {m["downloaded_url"]}',f'Original image: {m["original_url"]}',f'Credit: {m["credit"]}',f'Attribution: {m["attribution"]}',''])
        (metadata_dir/(place['folder_name'].lower()+'_source_record.txt')).write_text('\n'.join(lines),encoding='utf-8')
        outputs.append({'place_id':id,'image_count':len(selected),'manifest':str((metadata_dir/'image_manifest.json').relative_to(ROOT))})
        dump(REVIEW/progress_name,outputs)
        print(json.dumps({'downloaded_place':id,'images':len(selected)}),flush=True)
    dump(ROOT/'06_Database'/'JSON'/'new_display_images_summary.json',outputs)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['collect','sheets','commit'],default='collect')
    parser.add_argument('--start',type=int,default=1);parser.add_argument('--end',type=int,default=20);parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--selection',default=str(REVIEW/'reviewed_selections.json'))
    parser.add_argument('--only',nargs='*',default=[])
    parser.add_argument('--force',action='store_true')
    parser.add_argument('--supplement',action='store_true')
    parser.add_argument('--source-plan',help='Verified Commons exact file/category plan JSON')
    args=parser.parse_args();catalog=json.loads(CATALOG.read_text(encoding='utf-8-sig'))
    if args.source_plan:
        plan=json.loads(Path(args.source_plan).read_text(encoding='utf-8-sig'))
        canonical_names={p['id']:p['display_name'] for m in catalog['main_monuments'] for p in [m,*m['nearby_places']]}
        for entry in plan:
            name=canonical_names[entry['place_id']]
            if entry.get('exact_files'): EXACT_FILES[name]=entry['exact_files']
            if entry.get('exact_categories'): EXACT_CATEGORIES[name]=entry['exact_categories']
    REVIEW.mkdir(parents=True,exist_ok=True)
    if args.mode=='commit':
        records=[json.loads(p.read_text(encoding='utf-8')) for p in (REVIEW/'candidates').glob('*/candidates.json')]
        selection=json.loads(Path(args.selection).read_text(encoding='utf-8'));commit(records,selection,args.workers,Path(args.selection).stem+'_download_progress.json');return
    records=[]
    if args.mode=='collect':
        jobs=[(p,m) for m in catalog['main_monuments'] if args.start<=m['order']<=args.end for p in [m,*m['nearby_places']] if p['id']!='taj_mahal' and (not args.only or p['id'] in args.only)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures={pool.submit(collect,p,m,args.force,args.supplement):p['id'] for p,m in jobs}
            for future in concurrent.futures.as_completed(futures):
                id=futures[future]
                try:
                    record=future.result();records.append(record)
                    print(json.dumps({'collected':id,'candidates':len(record['candidates']),'status':record['status']}),flush=True)
                except Exception as error: print(json.dumps({'error':id,'message':str(error)}),flush=True)
                dump(REVIEW/'collection_progress.json',{'places_processed':len(records),'candidate_count':sum(len(r['candidates']) for r in records),'records':[{'id':r['place_id'],'candidates':len(r['candidates']),'status':r['status']} for r in records]})
    records=[json.loads(p.read_text(encoding='utf-8')) for p in (REVIEW/'candidates').glob('*/candidates.json')]
    records.sort(key=lambda x:(x['main_order'],not x['is_main'],x['place_id']))
    dump(REVIEW/'all_candidates.json',records)
    manifest=sheets(records)
    print(json.dumps({'places':len(records),'candidates':sum(len(r['candidates']) for r in records),'sheets':len(manifest)}),flush=True)

if __name__=='__main__': main()
