"""COMMUNITY0929 collector (Claude, 2026-09-29). Source/output download only; never executes, forks or submits.
Writes ONLY under analysis/community_20260929/. Reuses pure helpers from scripts/fetch_kaggle_updates.py.
Usage: python3 analysis/community_20260929/fetch_community.py discussions|kernels
"""
import csv, hashlib, json, re, subprocess, sys, time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
from fetch_kaggle_updates import message_rows, json_bytes  # side-effect free helpers
VENV = '~/.gemini/antigravity/brain/a8068519-c818-408b-8856-6802e8639fe9/scratch/venv/lib/python3.13/site-packages'

COMP = 'kaggriculture'
CUTOFF = '2026-09-18T00:00:00'   # last discussion collection was 2026-09-18 12:04 UTC
MAX_PAGES = 15
KERNELS = ['georgymamarin/kaggriculture-what-2600-farms-do-differently',
           'destbreso/kaggriculture-know-your-noise',
           'destbreso/everyone-is-playing-the-same-opening']
SIZE_CAP = 3 * 1024 ** 3        # 3 GB per kernel output -> kill + STOP
FLAG = re.compile(r'deadline|extend|extension|final (evaluation|submission|standing|ranking)|evaluation|bradley|'
                  r'rerun|re-run|reset|rule|disqualif|\bban|engine|version|1\.3\d|\bbug|timeout|submission limit|'
                  r'private|prize|announce|host|staff', re.I)


def iso(x):
    if x is None:
        return ''
    return (x.isoformat() if hasattr(x, 'isoformat') else str(x)).replace(' ', 'T')[:19]


def api_login():
    sys.path.insert(0, VENV)
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    return api


def retry(fn, *a, **k):
    for i in range(3):
        try:
            return fn(*a, **k)
        except Exception as e:  # 429 / transient
            if i == 2:
                raise
            time.sleep(30)


def topic_activity(t):
    for name in ('last_comment_post_date', 'post_date', 'creation_date', 'created'):
        v = iso(getattr(t, name, None))
        if v:
            return v
    return ''


def discussions():
    api = api_login()
    out = OUT / 'discussion'
    (out / 'raw').mkdir(parents=True, exist_ok=True)
    known = {p.name.split('_')[0] for p in (ROOT / 'docs/discussion').glob('*.md')}
    cands, errors = {}, []
    for page in range(1, MAX_PAGES + 1):
        resp = retry(api.competition_list_topics, COMP, sort_by='recent', page=page)
        topics = resp.topics or []
        if not topics:
            break
        for t in topics:
            cands[t.id] = t
        acts = [topic_activity(t) for t in topics]
        if acts and all(a and a < CUTOFF for a in acts):
            break
        time.sleep(1)
    resp = retry(api.competition_list_topics, COMP, sort_by='top', page=1)
    for t in resp.topics or []:
        cands.setdefault(t.id, t)
    rows = []
    for tid, t in sorted(cands.items()):
        act = topic_activity(t)
        if act and act < CUTOFF:
            continue
        try:
            msgs = message_rows(retry(api.competition_list_topic_messages, COMP, tid, sort_by='old', page_size=-1).messages)
        except Exception as e:
            errors.append({'topic': tid, 'error': str(e)})
            continue
        time.sleep(1)
        new = [m for m in msgs if iso(m['post_date']) >= CUTOFF]
        if not new:
            continue
        (out / 'raw' / f'{tid}.json').write_bytes(json_bytes(msgs))
        lines = [f'# {t.title}', f'topic {tid} | author {getattr(t, "author_name", None)} | votes {getattr(t, "votes", None)}',
                 f'https://www.kaggle.com/competitions/{COMP}/discussion/{tid}', '']
        for m in msgs:
            tag = '[NEW] ' if m in new else ''
            lines += [f'### {tag}{m["author_name"]} at {iso(m["post_date"])} (id {m["id"]}, parent {m["api_parent_id"]}, votes {m["votes"]})',
                      m['raw_markdown'] or m['content'] or '', '']
        (out / f'{tid}.md').write_text('\n'.join(lines))
        text = t.title + '\n' + '\n'.join((m['raw_markdown'] or m['content'] or '') for m in new)
        hits = sorted({h.group(0).lower() for h in FLAG.finditer(text)})
        rows.append(dict(topic_id=tid, title=t.title, author=getattr(t, 'author_name', None), last_activity=act,
                         n_msgs=len(msgs), n_new=len(new), first_new=min(iso(m['post_date']) for m in new),
                         votes=getattr(t, 'votes', None), previously_collected=str(tid) in known,
                         flags='|'.join(hits), url=f'https://www.kaggle.com/competitions/{COMP}/discussion/{tid}'))
    rows.sort(key=lambda r: r['first_new'], reverse=True)
    with open(out / 'index.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ['topic_id'])
        w.writeheader(); w.writerows(rows)
    summary = dict(done=datetime.now(timezone.utc).isoformat(), cutoff=CUTOFF, candidates=len(cands),
                   saved=len(rows), flagged=sum(bool(r['flags']) for r in rows), errors=errors)
    (out / 'summary.json').write_text(json.dumps(summary, indent=1, default=str))
    print(json.dumps(summary, default=str))


def nb_text(path):
    nb = json.loads(path.read_text())
    parts, images = [], 0
    for i, c in enumerate(nb.get('cells', [])):
        if c.get('cell_type') == 'markdown':
            parts.append(f'[MD {i}] ' + ''.join(c.get('source', '')))
            continue
        for o in c.get('outputs', []):
            d = o.get('data', {})
            images += sum(k.startswith('image/') for k in d)
            t = o.get('text') or d.get('text/plain')
            if t:
                parts.append(f'[OUT {i}] ' + ''.join(t))
    return '\n'.join(parts), images


def kernels():
    manifest = []
    for ref in KERNELS:
        slug = ref.split('/')[1]
        d = OUT / 'kernels' / slug
        (d / 'source').mkdir(parents=True, exist_ok=True)
        (d / 'output').mkdir(parents=True, exist_ok=True)
        rec = dict(ref=ref)
        code = (f"import sys; sys.path.insert(0, {VENV!r});"
                "from kaggle.api.kaggle_api_extended import KaggleApi as A; a=A(); a.authenticate();"
                f"a.kernels_pull({ref!r}, path={str(d / 'source')!r}, metadata=True);"
                f"a.kernels_output({ref!r}, path={str(d / 'output')!r})")
        p = subprocess.Popen([sys.executable, '-c', code], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        t0, status = time.time(), 'ok'
        while p.poll() is None:
            time.sleep(15)
            size = sum(f.stat().st_size for f in d.rglob('*') if f.is_file())
            if size > SIZE_CAP:
                p.kill(); status = 'STOP_size_cap'; break
            if time.time() - t0 > 1800:
                p.kill(); status = 'STOP_timeout'; break
        log = (p.stdout.read() or b'').decode(errors='replace')[-2000:]
        if status == 'ok' and p.returncode != 0:
            status = f'error_rc{p.returncode}'
        rec.update(status=status, log_tail=log)
        texts, images = [], 0
        for f in sorted(d.rglob('*')):
            if f.suffix == '.ipynb':
                t, n = nb_text(f); texts.append(f'===== {f.relative_to(d)}\n{t}'); images += n
            elif f.suffix == '.log':
                try:
                    texts.append(f'===== {f.relative_to(d)}\n' + ''.join(e.get('data', '') for e in json.loads(f.read_text())))
                except Exception:
                    texts.append(f'===== {f.relative_to(d)} (raw)\n' + f.read_text(errors='replace')[:200000])
        (d / 'outputs_text.txt').write_text('\n'.join(texts))
        rec['files'] = [dict(path=str(f.relative_to(OUT)), bytes=f.stat().st_size,
                             sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(d.rglob('*'))
                        if f.is_file() and f.name != 'outputs_text.txt']
        rec['out_lines'] = sum(1 for l in '\n'.join(texts).splitlines() if l.startswith('[OUT'))
        rec['images'] = images
        manifest.append(rec)
        print(ref, status, 'files', len(rec['files']), 'out_lines', rec['out_lines'], 'images', images)
        if status.startswith('STOP'):
            break
    (OUT / 'kernels' / 'manifest.json').write_text(json.dumps(manifest, indent=1))


if __name__ == '__main__':
    {'discussions': discussions, 'kernels': kernels}[sys.argv[1]]()
