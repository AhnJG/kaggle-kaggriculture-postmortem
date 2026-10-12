"""RL0929 collector (Claude, 2026-09-29). Kaggriculture discussion + code 중 강화학습(RL) 관련 글을 댓글까지 수집한다.

- 조회·소스 다운로드만 한다. 노트북 실행/fork/push/제출/투표/댓글 작성, dataset·kernel output 다운로드는 하지 않는다.
- 쓰기 위치는 이 파일이 있는 폴더(analysis/rl_community_20260929/) 아래뿐이다.
- 재실행 안전: raw 캐시(cache/)가 있으면 다시 받지 않는다. 429 등 오류 후 같은 명령으로 이어서 돌리면 된다.

Usage:
  python3 analysis/rl_community_20260929/fetch_rl_community.py discussions   # 대회 discussion 전수 → RL 필터
  python3 analysis/rl_community_20260929/fetch_rl_community.py code          # 대회 code 전수 → RL 필터 + 노트북 댓글
  python3 analysis/rl_community_20260929/fetch_rl_community.py digest        # 결과를 ALL_RL.md 한 파일로 합침
  python3 analysis/rl_community_20260929/fetch_rl_community.py all           # 위 3개 순서대로

검증한 SDK: kaggle 2.2.4 / kagglesdk 0.1.37 (competition_list_topics, competition_list_topic_messages,
kernels_list, kernels_pull, kernel_list_topics, forums_topic_show).
"""
import csv, hashlib, json, os, re, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
COMP = 'kaggriculture'
VENV = os.environ.get('KAGGLE_VENV', '~/.gemini/antigravity/brain/'
                      'a8068519-c818-408b-8856-6802e8639fe9/scratch/venv/lib/python3.13/site-packages')
SLEEP = 1.0            # 요청 간 간격(초)
MAX_TOPIC_PAGES = 60   # 20개/쪽 → 최대 1200 topic
MAX_KERNEL_PAGES = 40  # 100개/쪽 → 최대 4000 kernel
KERNEL_SEARCHES = ['reinforcement', 'RL', 'PPO', 'DQN', 'self-play', 'policy gradient', 'Q-learning',
                   'actor critic', 'AlphaZero', 'imitation', 'behavior cloning']

# ---- RL 판정 키워드 ----------------------------------------------------------------------------
# core: 이것 하나만 있어도 RL 글로 본다. adjacent: RL 인접 기법(BC·탐색·진화 등) — 따로 표시.
CORE = {
    'reinforcement learning': r'reinforcement[\s-]*learn\w*',
    'RL': r'(?<![\w/.])RL(?!\w)|\bDRL\b|\bMARL\b',  # 대소문자 구분: url·curl 오탐 방지
    'PPO': r'\bPPO\b|proximal policy',
    'DQN': r'\b(?:D{1,2}QN|DDQN|Rainbow)\b|deep q[\s-]network',
    'Q-learning': r'\bq[\s-]learning\b|\bq[\s-]?(?:table|value|function)s?\b',
    'actor-critic': r'actor[\s-]?critic|\bA2C\b|\bA3C\b|\bSAC\b|\bTD3\b|\bDDPG\b|\bIMPALA\b|\bV-trace\b',
    'policy gradient': r'policy[\s-]gradient|\bREINFORCE\b|\bTRPO\b|\bGRPO\b|\bGAE\b|advantage (?:function|estimat)',
    'value/policy net': r'(?:value|policy)[\s-](?:network|net|head)\b',
    'self-play': r'self[\s-]?play',
    'AlphaZero/MuZero': r'alpha[\s-]?zero|mu[\s-]?zero|alpha[\s-]?go',
    'TD/Bellman': r'temporal[\s-]difference|\bTD\((?:0|λ|lambda)\)|\bTD[\s-]learning|bellman',
    'RL libs': r'stable[\s_-]?baselines3?|\bsb3\b|\brllib\b|\bcleanrl\b|\btianshou\b|pettingzoo|'
               r'gymnasium|\bgym\.(?:Env|make|spaces)|torchrl',
    'RL terms': r'replay[\s-]buffer|experience[\s-]replay|epsilon[\s-]greedy|discount(?:ed)? (?:factor|return)|'
                r'reward[\s-]shaping|\bMDP\b|markov decision',
}
ADJACENT = {
    'imitation/BC': r'imitation[\s-]learn\w*|behaviou?r(?:al)?[\s-]clon\w*|\bBC\b(?= (?:agent|model|policy|at|on|from))',
    'MCTS/search': r'\bMCTS\b|monte[\s-]carlo tree',
    'bandit': r'multi[\s-]armed bandit|\bUCB1?\b|thompson sampling',
    'evolutionary': r'evolution(?:ary)? strateg\w*|\bCMA[\s-]?ES\b|genetic algorithm|neuroevolution',
    'learned agent': r'neural[\s-]net\w* agent|train(?:ed|ing) (?:an? )?(?:agent|policy)',
}
CORE_RE = {k: re.compile(v, 0 if k == 'RL' else re.I) for k, v in CORE.items()}
ADJ_RE = {k: re.compile(v, re.I) for k, v in ADJACENT.items()}


def hits(text):
    text = text or ''
    core = {k: len(r.findall(text)) for k, r in CORE_RE.items()}
    adj = {k: len(r.findall(text)) for k, r in ADJ_RE.items()}
    return {k: v for k, v in core.items() if v}, {k: v for k, v in adj.items() if v}


# ---- 공통 ---------------------------------------------------------------------------------------
def now():
    return datetime.now(timezone.utc).isoformat()


def iso(x):
    if x is None:
        return ''
    return (x.isoformat() if hasattr(x, 'isoformat') else str(x)).replace(' ', 'T')[:19]


def jdump(obj):
    def dflt(v):
        if isinstance(v, datetime):
            return v.isoformat()
        if hasattr(v, 'to_dict'):
            return v.to_dict()
        return str(v)
    return json.dumps(obj, indent=1, ensure_ascii=False, default=dflt)


def api_login():
    if os.path.isdir(VENV):
        sys.path.insert(0, VENV)
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    for name in ('competition_list_topics', 'competition_list_topic_messages', 'kernels_list', 'kernels_pull',
                 'kernel_list_topics', 'forums_topic_show'):
        if not hasattr(api, name):
            raise SystemExit(f'STOP: kaggle SDK에 {name} 없음 (kaggle>=2.2.4 필요)')
    return api


def retry(fn, *a, **k):
    for i in range(4):
        try:
            out = fn(*a, **k)
            time.sleep(SLEEP)
            return out
        except Exception as e:
            msg = str(e)
            if any(s in msg for s in ('404', 'Not Found', '403', 'Forbidden')) or i == 3:
                raise
            time.sleep(30 * (i + 1))  # 429 / 일시 오류


def log(*a):
    print(f'[{now()[:19]}]', *a, flush=True)


def write_index(path, rows, fields):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)


def fmt_hits(d):
    return '|'.join(f'{k}:{v}' for k, v in sorted(d.items(), key=lambda x: -x[1]))


# ---- discussions --------------------------------------------------------------------------------
def message_rows(messages, parent=None, depth=0):
    rows = []
    for m in messages or []:
        row = {n: getattr(m, n, None) for n in ('id', 'post_date', 'author_name', 'content', 'raw_markdown',
                                                 'is_deleted', 'votes')}
        row.update(parent_id=parent, depth=depth)
        rows.append(row)
        rows.extend(message_rows(getattr(m, 'replies', None), row['id'], depth + 1))
    return rows


def discussions():
    api = api_login()
    d = OUT / 'discussion'
    cache = d / 'cache'
    cache.mkdir(parents=True, exist_ok=True)
    topics, errors = {}, []
    # 1) 전체 topic 목록 (new 정렬 전 페이지 + top/hot 보강)
    for sort in ('new', 'top', 'hot', 'active'):
        for page in range(1, MAX_TOPIC_PAGES + 1):
            try:
                resp = retry(api.competition_list_topics, COMP, sort_by=sort, page=page)
            except Exception as e:
                errors.append(dict(stage='list', sort=sort, page=page, error=str(e)[:300]))
                break
            ts = resp.topics or []
            for t in ts:
                topics.setdefault(t.id, t)
            total = resp.total_count or 0
            if not ts or page * 20 >= total or (sort != 'new' and page >= 5):
                break
        log(f'list sort={sort}: 누적 topic {len(topics)} (total_count={total})')
    # 2) topic 별 메시지 전부 → 캐시
    rows = []
    for i, (tid, t) in enumerate(sorted(topics.items())):
        raw = cache / f'{tid}.json'
        if raw.exists():
            msgs = json.loads(raw.read_text())['messages']
        else:
            try:
                resp = retry(api.competition_list_topic_messages, COMP, tid, sort_by='old', page_size=-1)
                msgs = message_rows(resp.messages)
            except Exception as e:
                errors.append(dict(stage='messages', topic=tid, error=str(e)[:300]))
                continue
            meta = {n: getattr(t, n, None) for n in ('id', 'title', 'topic_url', 'author_name', 'comment_count',
                                                     'votes', 'post_date', 'last_comment_post_date', 'is_sticky')}
            raw.write_text(jdump(dict(fetched_at=now(), topic=meta, messages=msgs)))
        if i % 25 == 0:
            log(f'messages {i + 1}/{len(topics)}')
        body = msgs[0] if msgs else {}
        head_text = (t.title or '') + '\n' + (body.get('raw_markdown') or body.get('content') or '')
        rest_text = '\n'.join((m.get('raw_markdown') or m.get('content') or '') for m in msgs[1:])
        c_head, a_head = hits(head_text)
        c_all, a_all = hits(head_text + '\n' + rest_text)
        if not (c_all or a_all):
            continue
        tier = ('A_core_in_post' if c_head else 'B_core_in_comments' if c_all else
                'C_adjacent_only')
        url = f'https://www.kaggle.com/competitions/{COMP}/discussion/{tid}'
        lines = [f'# {t.title}', f'discussion {tid} | author {getattr(t, "author_name", None)} | votes '
                 f'{getattr(t, "votes", None)} | messages {len(msgs)} | tier {tier}', url,
                 f'RL hits: {fmt_hits(c_all)} | adjacent: {fmt_hits(a_all)}', '']
        for m in msgs:
            ind = '  ' * m['depth']
            lines += [f'### {ind}{"↳ " if m["depth"] else ""}{m["author_name"]} at {iso(m["post_date"])} '
                      f'(id {m["id"]}, parent {m["parent_id"]}, votes {m["votes"]}'
                      f'{", DELETED" if m.get("is_deleted") else ""})',
                      m.get('raw_markdown') or m.get('content') or '', '']
        (d / f'{tid}.md').write_text('\n'.join(lines), encoding='utf-8')
        rows.append(dict(kind='discussion', id=tid, title=t.title, author=getattr(t, 'author_name', None),
                         tier=tier, core_hits=fmt_hits(c_all), adjacent_hits=fmt_hits(a_all),
                         n_msgs=len(msgs), votes=getattr(t, 'votes', None), post_date=iso(getattr(t, 'post_date', None)),
                         last_activity=iso(getattr(t, 'last_comment_post_date', None)), url=url,
                         file=f'discussion/{tid}.md'))
    rows.sort(key=lambda r: (r['tier'], -(r['votes'] or 0)))
    write_index(d / 'index.csv', rows, list(rows[0]) if rows else ['id'])
    summary = dict(done=now(), topics_listed=len(topics), cached=len(list(cache.glob('*.json'))), rl_saved=len(rows),
                   by_tier={k: sum(r['tier'] == k for r in rows) for k in sorted({r['tier'] for r in rows})},
                   errors=errors)
    (d / 'summary.json').write_text(jdump(summary))
    log('DISCUSSIONS', json.dumps({k: v for k, v in summary.items() if k != 'errors'}, ensure_ascii=False),
        'errors', len(errors))
    return summary


# ---- code (kernels) -----------------------------------------------------------------------------
def nb_to_text(path):
    """노트북 → (markdown 텍스트, code 텍스트). 출력은 저장하지 않는다(소스만)."""
    if path.suffix != '.ipynb':
        src = path.read_text(errors='replace')
        return '', src
    nb = json.loads(path.read_text(errors='replace'))
    md, code = [], []
    for c in nb.get('cells', []):
        s = c.get('source', '')
        s = ''.join(s) if isinstance(s, list) else s
        (md if c.get('cell_type') == 'markdown' else code).append(s)
    return '\n\n'.join(md), '\n\n'.join(code)


def comment_rows(comments, parent=None, depth=0):
    rows = []
    for c in comments or []:
        row = {n: getattr(c, n, None) for n in ('id', 'author_name', 'post_date', 'content', 'votes')}
        row.update(parent_id=parent, depth=depth)
        rows.append(row)
        rows.extend(comment_rows(getattr(c, 'replies', None), row['id'], depth + 1))
    return rows


def kernel_comments(api, ref, errors):
    """노트북 댓글 스레드 전부: kernel_list_topics → forums_topic_show(모든 페이지)."""
    threads, token = [], None
    for _ in range(20):
        try:
            resp = retry(api.kernel_list_topics, ref, page_size=50, page_token=token)
        except Exception as e:
            errors.append(dict(stage='kernel_topics', ref=ref, error=str(e)[:300]))
            return threads
        for t in resp.topics or []:
            try:
                topic, comments, _ = retry(api.forums_topic_show, t.id)
            except Exception as e:
                errors.append(dict(stage='kernel_comments', ref=ref, topic=t.id, error=str(e)[:300]))
                continue
            threads.append(dict(topic_id=t.id, title=getattr(topic, 'title', None),
                                author_name=getattr(topic, 'author_name', None),
                                post_date=getattr(topic, 'post_date', None), votes=getattr(topic, 'votes', None),
                                content=getattr(topic, 'content', None), comments=comment_rows(comments)))
        token = resp.next_page_token
        if not token:
            break
    return threads


def code():
    api = api_login()
    d = OUT / 'code'
    cache = d / 'cache'
    cache.mkdir(parents=True, exist_ok=True)
    kernels, errors = {}, []
    # 1) 대회 노트북 전수 목록 + RL 검색어 보강
    for sort in ('dateCreated', 'voteCount'):
        for page in range(1, MAX_KERNEL_PAGES + 1):
            try:
                ks = retry(api.kernels_list, competition=COMP, page=page, page_size=100, sort_by=sort) or []
            except Exception as e:
                errors.append(dict(stage='list', sort=sort, page=page, error=str(e)[:300]))
                break
            for k in ks:
                kernels.setdefault(k.ref, k)
            if len(ks) < 100:
                break
        log(f'kernels_list sort={sort}: 누적 {len(kernels)}')
    for q in KERNEL_SEARCHES:
        try:
            for k in retry(api.kernels_list, competition=COMP, search=q, page_size=100) or []:
                kernels.setdefault(k.ref, k)
        except Exception as e:
            errors.append(dict(stage='search', q=q, error=str(e)[:300]))
    log(f'검색 보강 후 kernel {len(kernels)}')
    # 2) 소스 pull + 댓글 (캐시) → RL 판정
    rows = []
    for i, (ref, k) in enumerate(sorted(kernels.items())):
        slug = ref.replace('/', '__')
        kc = cache / slug
        src_file = next(iter(sorted(kc.glob('*.ipynb')) + sorted(kc.glob('*.py')) + sorted(kc.glob('*.r*'))), None) \
            if kc.exists() else None
        if src_file is None:
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    retry(api.kernels_pull, ref, path=tmp, metadata=True)
                    kc.mkdir(parents=True, exist_ok=True)
                    for f in Path(tmp).iterdir():
                        if f.is_file() and f.stat().st_size < 50 * 1024 ** 2:
                            (kc / f.name).write_bytes(f.read_bytes())
                src_file = next(iter(sorted(kc.glob('*.ipynb')) + sorted(kc.glob('*.py')) + sorted(kc.glob('*.r*'))), None)
            except Exception as e:
                errors.append(dict(stage='pull', ref=ref, error=str(e)[:300]))
        if i % 25 == 0:
            log(f'pull {i + 1}/{len(kernels)}')
        md, src = nb_to_text(src_file) if src_file else ('', '')
        title = getattr(k, 'title', '') or ''
        c_head, a_head = hits(title + '\n' + md)
        c_code, a_code = hits(src)
        c_all = {x: c_head.get(x, 0) + c_code.get(x, 0) for x in set(c_head) | set(c_code)}
        a_all = {x: a_head.get(x, 0) + a_code.get(x, 0) for x in set(a_head) | set(a_code)}
        # 댓글(모든 노트북; 댓글에서만 RL이 언급된 노트북도 잡기 위해)
        cfile = kc / 'comments.json'
        if cfile.exists():
            threads = json.loads(cfile.read_text())
        else:
            threads = kernel_comments(api, ref, errors)
            kc.mkdir(parents=True, exist_ok=True)
            cfile.write_text(jdump(threads))
        c_cmt, a_cmt = hits('\n'.join((t.get('content') or '') + '\n' + '\n'.join((c.get('content') or '')
                                                                             for c in t['comments']) for t in threads))
        # 코드에서만 걸린 경우는 핵심 키워드 2종 이상 또는 총 3회 이상일 때만 RL로 본다(우연한 'MDP' 등 오탐 방지).
        code_strong = len(c_code) >= 2 or sum(c_code.values()) >= 3
        if c_head:
            tier = 'A_core_in_title_or_markdown'
        elif code_strong:
            tier = 'B_core_in_code'
        elif c_cmt:
            tier = 'B_core_in_comments'
        elif a_head or c_code or a_code or a_cmt:
            tier = 'C_adjacent_or_weak'
        else:
            continue
        n_cmt = sum(len(t['comments']) for t in threads)
        url = f'https://www.kaggle.com/code/{ref}'
        lines = [f'# {title}', f'code {ref} | author {getattr(k, "author", None)} | votes {getattr(k, "total_votes", None)} '
                 f'| last run {iso(getattr(k, "last_run_time", None))} | tier {tier}', url,
                 f'RL hits (title+markdown): {fmt_hits(c_head)} | (code): {fmt_hits(c_code)} | '
                 f'adjacent: {fmt_hits(a_all)} | (comments): {fmt_hits(c_cmt)} {fmt_hits(a_cmt)}',
                 f'source: code/cache/{slug}/{src_file.name if src_file else "(pull 실패)"}', '',
                 '## Markdown cells', md or '(없음)', '', f'## Comments (threads {len(threads)}, comments {n_cmt})']
        for t in threads:
            lines += [f'### [thread {t["topic_id"]}] {t.get("title") or ""} — {t.get("author_name")} at {iso(t.get("post_date"))}'
                      f' (votes {t.get("votes")})', t.get('content') or '', '']
            for c in t['comments']:
                ind = '  ' * c['depth']
                lines += [f'#### {ind}{"↳ " if c["depth"] else ""}{c["author_name"]} at {iso(c["post_date"])} '
                          f'(id {c["id"]}, parent {c["parent_id"]}, votes {c["votes"]})', c.get('content') or '', '']
        if not threads:
            lines.append('(댓글 없음)')
        (d / f'{slug}.md').write_text('\n'.join(lines), encoding='utf-8')
        rows.append(dict(kind='code', id=ref, title=title, author=getattr(k, 'author', None), tier=tier,
                         core_hits=fmt_hits(c_all), adjacent_hits=fmt_hits(a_all), comment_hits=fmt_hits(c_cmt),
                         n_threads=len(threads), n_comments=n_cmt,
                         votes=getattr(k, 'total_votes', None), last_run=iso(getattr(k, 'last_run_time', None)),
                         url=url, file=f'code/{slug}.md',
                         source=f'code/cache/{slug}/{src_file.name}' if src_file else ''))
    rows.sort(key=lambda r: (r['tier'], -(r['votes'] or 0)))
    write_index(d / 'index.csv', rows, list(rows[0]) if rows else ['id'])
    summary = dict(done=now(), kernels_listed=len(kernels), rl_saved=len(rows),
                   by_tier={k: sum(r['tier'] == k for r in rows) for k in sorted({r['tier'] for r in rows})},
                   comments_total=sum(r['n_comments'] for r in rows), errors=errors)
    (d / 'summary.json').write_text(jdump(summary))
    log('CODE', json.dumps({k: v for k, v in summary.items() if k != 'errors'}, ensure_ascii=False),
        'errors', len(errors))
    return summary


# ---- digest -------------------------------------------------------------------------------------
def digest():
    """index.csv 두 개를 읽어 tier 순으로 ALL_RL.md 하나로 합친다(C 등급은 목록만)."""
    parts = [f'# Kaggriculture RL 관련 커뮤니티 글 모음 (생성 {now()[:19]}Z)', '',
             'tier A/B = 본문 합침, C(인접·약한 매치) = 목록만. 원문은 각 file 경로.', '']
    for kind in ('discussion', 'code'):
        idx = OUT / kind / 'index.csv'
        if not idx.exists():
            parts.append(f'## {kind}: index.csv 없음 (수집 미실행)')
            continue
        rows = list(csv.DictReader(open(idx, encoding='utf-8')))
        parts += [f'## {kind} — {len(rows)}건', '', '| tier | votes | title | hits | file |', '|---|---|---|---|---|']
        parts += [f'| {r["tier"]} | {r["votes"]} | {r["title"].replace("|", "/")} | {r["core_hits"] or r["adjacent_hits"]} '
                  f'| {r["file"]} |' for r in rows]
        parts.append('')
        for r in rows:
            if r['tier'].startswith('C'):
                continue
            parts += ['', '---', '', (OUT / r['file']).read_text(encoding='utf-8')]
    (OUT / 'ALL_RL.md').write_text('\n'.join(parts), encoding='utf-8')
    log('DIGEST', OUT / 'ALL_RL.md', f'{(OUT / "ALL_RL.md").stat().st_size:,} bytes')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if cmd == 'all':
        discussions(); code(); digest()
    else:
        {'discussions': discussions, 'code': code, 'digest': digest}[cmd]()
