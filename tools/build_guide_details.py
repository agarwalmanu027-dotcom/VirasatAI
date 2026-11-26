"""Prepare offline guide sections from the existing reviewed bilingual library.

Main-monument facts have explicit Hindi translations and section assignments.
Other entries reuse existing narration verbatim; they do not acquire new facts.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'tools/guide_main_details.json'


def paragraphs(text):
    return [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]


def detail_fields(entry, main):
    if not entry['ready']:
        return {}
    en = paragraphs(entry['storyEnglish'])
    hi = paragraphs(entry['storyHindi'])
    if entry['id'] in main:
        spec = main[entry['id']]
        translated = spec['factsHindi']
        if len(translated) != len(entry['facts']):
            raise ValueError(f"Fact translation count changed: {entry['id']}")
        result = {
            'facts': spec['quickFacts'],
            'factsHindi': spec['quickFactsHindi'],
            'factLabels': spec['factLabels'],
            'factLabelsHindi': spec['factLabelsHindi'],
        }
        if any(len(result[key]) != len(translated)
               for key in ('facts', 'factsHindi', 'factLabels', 'factLabelsHindi')):
            raise ValueError(f"Quick facts are incomplete: {entry['id']}")
        for topic in ('history', 'architecture'):
            if len(en) != len(hi):
                raise ValueError(f"Narration alignment changed: {entry['id']}")
            indices = spec[topic + 'Paragraphs']
            result[topic] = '\n\n'.join(en[i] for i in indices)
            result[topic + 'Hindi'] = '\n\n'.join(hi[i] for i in indices)
        return result
    # For associated places, Hindi details remain the approved Hindi account,
    # clearly identified as a summary rather than line-by-line translations.
    result = {'detailsSummaryHindi': entry['storyHindi']}
    if len(en) != len(hi):
        return result
    topics = {
        'history': r'\b(built|founded|established|commissioned|centur\w*|dynast\w*|reign|histor\w*|memorial|commemorat\w*)\b',
        'architecture': r'\b(architect\w*|carv\w*|dome\w*|pillar\w*|column\w*|arches|arch|sandstone|marble|layout|courtyard\w*|structure\w*|facade\w*|gateway\w*)\b',
    }
    for topic, pattern in topics.items():
        chosen = [i for i, p in enumerate(en) if re.search(pattern, p, re.I)][:2]
        result[topic] = '\n\n'.join(en[i] for i in chosen)
        result[topic + 'Hindi'] = '\n\n'.join(hi[i] for i in chosen)
    return result


def main():
    catalog = ROOT / 'frontend_recovered/assets/data/guide_catalog.json'
    data = json.loads(catalog.read_text(encoding='utf-8'))
    specs = json.loads(MAIN.read_text(encoding='utf-8'))
    details = {e['id']: detail_fields(e, specs) for e in data['entries']}
    for entry in data['entries']:
        entry.update(details[entry['id']])
    catalog.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Prepared bilingual details for {sum(e['ready'] for e in data['entries'])} ready entries")


if __name__ == '__main__':
    main()
