"""Read-only OOXML object audit. Findings require visual/manifest review."""
import argparse
import json
import re
from zipfile import ZipFile
from pathlib import PurePosixPath
import posixpath
import xml.etree.ElementTree as E

NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}


def rect(obj):
    x = obj.find('p:spPr/a:xfrm', NS)
    if x is None:
        return None
    off, ext = x.find('a:off', NS), x.find('a:ext', NS)
    if off is None or ext is None:
        return None
    return tuple(int(v) for v in (off.get('x'), off.get('y'), ext.get('cx'), ext.get('cy')))


def audit(path):
    with ZipFile(path) as z:
        names = set(z.namelist())
        pres = E.fromstring(z.read('ppt/presentation.xml'))
        size = pres.find('p:sldSz', NS)
        area = int(size.get('cx')) * int(size.get('cy'))
        slide_parts = sorted((n for n in names if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)),
                             key=lambda n: int(re.search(r'(\d+)\.xml', n)[1]))
        rows = []
        for part in slide_parts:
            root = E.fromstring(z.read(part))
            tree = root.find('p:cSld/p:spTree', NS)
            objects = list(tree) if tree is not None else []
            shapes = root.findall('.//p:sp', NS)
            text = [s for s in shapes if any((t.text or '').strip() for t in s.findall('.//a:t', NS))]
            filled = [s for s in text if s.find('p:spPr/a:solidFill', NS) is not None]
            pics = root.findall('.//p:pic', NS)
            risks = []
            for pic in pics:
                box = rect(pic)
                if box and box[2] * box[3] >= area * .9:
                    risks.append('near_full_slide_image: check for flattened page or legitimate pure background')
            for idx, obj in enumerate(objects):
                if obj.tag != '{' + NS['p'] + '}sp' or obj not in text:
                    continue
                box = rect(obj)
                if not box or obj.find('p:spPr/a:solidFill', NS) is not None:
                    continue
                for lower in objects[:idx]:
                    lb = rect(lower)
                    if (lower.tag == obj.tag and lb == box and
                        lower.find('p:spPr/a:solidFill', NS) is not None and
                        not any((t.text or '').strip() for t in lower.findall('.//a:t', NS))):
                        risks.append('possible_separate_text_background: inspect stacking and intended roles')
            rows.append({'part': part, 'text_objects': len(text), 'self_filled_text_objects': len(filled),
                         'connectors': len(root.findall('.//p:cxnSp', NS)),
                         'tables': len(root.findall('.//a:tbl', NS)),
                         'chart_references': len(root.findall('.//c:chart', NS)),
                         'pictures': len(pics), 'review_flags': risks})
        charts = []
        for part in sorted(n for n in names if re.fullmatch(r'ppt/charts/chart\d+\.xml', n)):
            root = E.fromstring(z.read(part))
            rid = root.find('c:externalData', NS)
            target = None
            rp = str(PurePosixPath(part).parent / '_rels' / (PurePosixPath(part).name + '.rels'))
            if rid is not None and rp in names:
                rels = E.fromstring(z.read(rp))
                for rel in rels:
                    if rel.get('Id') == rid.get('{' + NS['r'] + '}id') and rel.get('TargetMode') != 'External':
                        target = posixpath.normpath(posixpath.join(posixpath.dirname(part), rel.get('Target', '')))
            charts.append({'part': part, 'embedded_data': target if target in names else None})
        return {'slide_count': len(rows), 'slides': rows, 'charts': charts,
                'limitations': 'Part order is not presentation order. Groups, inherited fills, text fit, pixels, data truth and full editability require separate inspection.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('pptx')
    args = p.parse_args()
    print(json.dumps(audit(args.pptx), ensure_ascii=False, indent=2))
