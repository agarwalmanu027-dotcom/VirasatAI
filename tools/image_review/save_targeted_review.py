"""Save explicit visual-review decisions with source-title and SHA1 binding."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "tools" / "image_review"
DECISIONS = {
"meenakshi_temple__gandhi_memorial_museum": {
"coverage_note": "Two clear photographs genuinely depict the Madurai museum: a broad facade/courtyard view and a differently dated facade appearance. Both are front views; side/interior coverage is still missing. Reject #12 as a weaker repeated facade with a central light pole, and #14 as a heavily saturated, foliage-obstructed wire portrait/garden scene rather than strong museum coverage. All old Delhi Gandhi Smriti sources stay rejected.",
"choices": [
[13,"Overview","Sharp wide view of the Madurai museum facade, wings, dome and courtyard, with the building unobstructed."],
[11,"Different_Views","Correct Madurai museum front with visible facade details and its differently dated paint appearance; visitors remain secondary."]
]},
"meenakshi_temple__palamuthirsolai_murugan_temple": {
"coverage_note": "Three correct Pazhamudircholai views show a clear colorful tower, the temple entrance and the wooded hill approach. Reject new #3 for washed-out haze and weak detail. Prior Kallazhagar/Bengaluru candidates remain rejected.",
"choices": [
[6,"Overview","Clear colorful Pazhamudircholai gopuram and part of the adjacent facade against the wooded hill."],
[4,"Different_Views","Sharper front entrance tower with painted sculptures and the correct Murugan sign; ordinary stalls provide context."],
[5,"Surroundings","Wider temple entrance and forested hill setting, showing the approach rather than duplicating the close tower view."]
]},
"victoria_memorial__marble_palace": {
"coverage_note": "Three correct Kolkata palace views show the garden-facing colonnaded front, rear facade and street-side gate. All are clear natural-color photographs. The gate photo includes normal street traffic while retaining useful architecture context; prior wrong/weak originals are not reintroduced.",
"choices": [
[13,"Overview","Clear colonnaded palace front with garden and fountain; exact Kolkata address and palace identity verified."],
[11,"Different_Views","Clear rear facade and garden, providing a genuinely different side of Marble Palace."],
[12,"Surroundings","Street-side palace entrance and gate with the colonnaded building beyond; traffic is contextual, not a generic portrait."]
]},
"charminar__hayat_bakshi_mosque": {
"coverage_note": "Four correct Hayathnagar photographs cover the unobstructed front, minaret carving, side architecture and garden approach. Natural overcast lighting is subdued but details are visible. Reject rear street/painted-boundary view #13, hazy overexposed ceiling #15 and administrative board #17 as weak gallery coverage. All original wrong Qutb Shahi Tombs mosque candidates remain rejected.",
"choices": [
[11,"Overview","Correct Hayathnagar mosque full front with both minarets and arches visible; clear architecture under natural overcast light."],
[16,"Different_Views","Distinct close side-angle view of the Hayathnagar minaret and facade; visible stonework and architectural depth."],
[12,"Details","Sharp minaret crown and ornament carvings at the correct Hayathnagar mosque."],
[14,"Surroundings","Longer view along the garden and stone approach to the correct mosque; adds setting beyond the unobstructed front."]
]},
"konark_sun_temple__chausathi_yogini_temple": {
"coverage_note": "Four correct Hirapur photos: clear circular exterior, focused sculptural circuit, one single sculpture and a wider curved niche row. Intentional depth of field in #1 leaves its central sculpture sharply focused; no generic temple substitutions.",
"choices": [
[2,"Overview","Clear color view of the circular, open-air Hirapur temple and entrance in its landscaped setting."],
[1,"Details","Sharp central yogini sculpture and carved niche row; foreground/background softness is intentional depth of field."],
[3,"Details","Correct Hirapur stone sculpture in its niche, visible detail and color, without a prominent watermark."],
[4,"Different_Views","Wider curved interior circuit with yogini niches and red ritual cloth; complements the exterior and focused detail."]
]},
"konark_sun_temple__raghurajpur_artist_village": {
"coverage_note": "Five clear village-specific views cover the named entrance, painted house, art display, artisan at work and a wider row of studios. Reject #5 because the seated-person portrait dominates and adds little to the stronger process view.",
"choices": [
[1,"Overview","Village entrance with a legible Raghurajpur sign and clear surrounding buildings."],
[6,"Different_Views","Clear wide row of painted houses and studio displays, showing the village streetscape."],
[2,"Details","Decorated village-house wall with sharply visible painted motifs and a studio doorway."],
[4,"Details","Relevant artisan-process image with handwork and painted crafts visible; this is site-specific craft documentation."],
[3,"Different_Views","Village artisan displays artwork at a painted doorway, with the decorated house and art visible."]
]}
}
out_path = REVIEW / "reviewed_targeted_rescue.json"
existing = json.loads(out_path.read_text(encoding="utf-8-sig")) if out_path.exists() else []
entries={p["place_id"]:p for p in existing}
for pid,decision in DECISIONS.items():
    meta=json.loads((REVIEW/"candidates"/pid/"candidates.json").read_text(encoding="utf-8-sig"))
    by_id={c["candidate_id"]:c for c in meta["candidates"]}
    selected=[]
    for cid,category,note in decision["choices"]:
        c=by_id[cid]
        assert (ROOT/c["preview_path"]).exists()
        selected.append({"candidate_id":cid,"category":category,"review_note":note,"reviewed_source_title":c["title"],"reviewed_source_sha1":c["sha1"]})
    entries[pid]={"place_id":pid,"review_status":"visually_reviewed","selected":selected,"coverage_note":decision["coverage_note"]}
if "ajanta_ellora_caves" not in entries:
    prior=json.loads((REVIEW/"reviewed_groups_08_14.json").read_text(encoding="utf-8-sig"))
    base=next(p for p in prior if p["place_id"]=="ajanta_ellora_caves")
    meta=json.loads((REVIEW/"candidates"/"ajanta_ellora_caves"/"candidates.json").read_text(encoding="utf-8-sig"))
    by_id={c["candidate_id"]:c for c in meta["candidates"]}
    preserved=[]
    for choice in base["selected"]:
        c=by_id[choice["candidate_id"]]
        preserved.append({**choice,"reviewed_source_title":c["title"],"reviewed_source_sha1":c["sha1"]})
    entries[base["place_id"]]={"place_id":base["place_id"],"review_status":"visually_reviewed","selected":preserved,"coverage_note":"Preserves all 16 Ajanta selections previously visually reviewed in groups 08–14. Supplemental Ellora candidates are still pending collection and review."}
out_path.write_text(json.dumps(list(entries.values()),indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(f"Saved {len(entries)} places / {sum(len(p['selected']) for p in entries.values())} selections")

