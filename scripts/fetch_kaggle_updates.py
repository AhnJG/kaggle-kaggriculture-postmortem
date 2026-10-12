"""Collect selected public source only; never execute notebooks or fetch outputs.

Validated SDK interface: kaggle 2.2.4 / kagglesdk 0.1.37. The API can flatten
reply ancestry, and source pull is not version-pinned: SHA is the source identity.
"""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import tempfile
from datetime import datetime, timezone


def safe_filename(name):
    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')


def json_default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value.to_dict(ignore_defaults=False)


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, default=json_default) + '\n').encode()


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            name = stream.name
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


def snapshot(root, data, suffix):
    digest = hashlib.sha256(data).hexdigest()
    path = Path('docs/collection_snapshots') / digest / ('source' + suffix)
    if (root / path).exists():
        if (root / path).read_bytes() != data:
            raise ValueError('Existing snapshot does not match content SHA')
    else:
        atomic_write(root / path, data)
    return {'sha256': digest, 'snapshot_path': str(path)}


def update_alias(root, path, data, originals):
    target = root / path
    previous = target.read_bytes() if target.exists() else None
    originals.setdefault(path, previous)
    if previous is not None:
        snapshot(root, previous, target.suffix)
    atomic_write(target, data)


def restore_files(root, originals, report):
    for path, data in originals.items():
        try:
            if data is None:
                (root / path).unlink(missing_ok=True)
            else:
                atomic_write(root / path, data)
        except OSError as error:
            report['errors'].append({'stage': 'rollback', 'path': path, 'error': str(error)})


def message_rows(messages, parent=None):
    rows = []
    for msg in messages:
        row = {name: getattr(msg, name, None) for name in
               ('id', 'post_date', 'author_name', 'content', 'raw_markdown', 'is_deleted', 'votes')}
        row['api_parent_id'] = parent
        rows.append(row)
        rows.extend(message_rows(getattr(msg, 'replies', None) or [], row['id']))
    return rows


def fetch_discussion(api, competition, topic, root, originals):
    response = api.competition_list_topic_messages(competition, topic.id, sort_by='old', page_size=-1)
    rows = message_rows(response.messages)
    if not rows:
        raise ValueError('Empty message tree; preserving previous source')
    rows.sort(key=lambda row: (str(row['post_date'] or ''), str(row['id'])))
    raw = snapshot(root, json_bytes(response), '.json')
    lines = [f'# {topic.title}', f'Author: {getattr(topic, "author_name", None) or "N/A"}',
             f'Score: {getattr(topic, "votes", None) if getattr(topic, "votes", None) is not None else "N/A"}',
             'Order: post_date ascending; unknown dates first. Parent is API ancestry, which may be flattened.', '']
    for row in rows:
        lines.extend([f'### {row["author_name"] or "N/A"} at {row["post_date"] or "N/A"}',
                      f'ID: {row["id"]}; API parent: {row["api_parent_id"]}; deleted: {row["is_deleted"]}',
                      row['raw_markdown'] or row['content'] or '', '', '---'])
    path = f'docs/discussion/{topic.id}_{safe_filename(topic.title)}.md'
    data = ('\n'.join(lines) + '\n').encode()
    identity = snapshot(root, data, '.md')
    entry = dict(id=topic.id, title=topic.title, path=path, score=getattr(topic, 'votes', None),
                author=getattr(topic, 'author_name', None),
                url=f'https://www.kaggle.com/competitions/{competition}/discussion/{topic.id}',
                source_version=None, last_comment_post_date=getattr(topic, 'last_comment_post_date', None),
                raw_response=raw, returned_messages=len(rows), expected_messages=None,
                completeness='all returned replies; server completeness unverified', **identity)
    update_alias(root, path, data, originals)
    return entry


def fetch_code(api, competition, kernel, root, originals):
    ref = kernel.ref
    author, slug = ref.split('/')
    with tempfile.TemporaryDirectory() as folder:
        api.kernels_pull(ref, path=folder, metadata=True)
        metadata_path = Path(folder) / 'kernel-metadata.json'
        source_metadata = json.loads(metadata_path.read_text())
        source = Path(folder) / source_metadata['code_file']
        if source.resolve().parent != Path(folder).resolve() or source.suffix not in ('.ipynb', '.py'):
            raise ValueError('Unsupported source path or language')
        data = source.read_bytes()
        if not data.strip():
            raise ValueError('Empty kernel source')
        if source.suffix == '.ipynb':
            notebook = json.loads(data)
            if not isinstance(notebook.get('cells'), list):
                raise ValueError('Invalid notebook cells')
        identity = snapshot(root, data, source.suffix)
        raw = snapshot(root, json_bytes(source_metadata), '.json')
        path = f'docs/code/{author}_{slug}{source.suffix}'
    entry = dict(ref=ref, title=getattr(kernel, 'title', slug), path=path,
                score=getattr(kernel, 'total_votes', None), url=f'https://www.kaggle.com/code/{ref}',
                listed_version=getattr(kernel, 'current_version_number', None), source_version=None,
                version_note='listed version is not a verified version of unpinned pulled bytes; use SHA',
                last_run_time=getattr(kernel, 'last_run_time', None), source_metadata=raw,
                outputs='not collected', dependencies='metadata inventory only; not downloaded', **identity)
    update_alias(root, path, data, originals)
    return entry


def collect(api, root=Path('.'), competition='kaggriculture'):
    root = Path(root)
    now = datetime.now(timezone.utc).isoformat()
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    report = {'run_id': run_id, 'started_at': now, 'scope': 'source_only', 'errors': [], 'fetched': [],
              'selection': {'discussions': {'top_voted': 'top', 'recent': 'recent'},
                            'codes': {'top_voted': 'voteCount', 'recent': 'dateRun'}},
              'coverage': 'up to 5 per server sort; not full corpus or watchlist',
              'sdk_versions': {}}
    for package in ('kaggle', 'kagglesdk'):
        try:
            report['sdk_versions'][package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            report['sdk_versions'][package] = None
    metadata_path = root / 'docs/latest_metadata.json'
    inventory_path = root / 'docs/collection_inventory.json'
    try:
        previous = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
        inventory = json.loads(inventory_path.read_text()) if inventory_path.exists() else {}
    except (ValueError, OSError) as error:
        report.update(status='failed', errors=[{'stage': 'read_previous', 'error': str(error)}])
        atomic_write(root / f'docs/collection_runs/{run_id}.json', json_bytes(report))
        return 1
    metadata = dict(previous)
    originals = {}
    list_success = 0
    for kind, identity_key, fetch in (('discussions', 'id', fetch_discussion), ('codes', 'ref', fetch_code)):
        old = previous.get(kind, {})
        old_entries = {entry[identity_key]: entry for group in ('top_voted', 'recent')
                       for entry in old.get(group, []) if identity_key in entry}
        selected = dict(old)
        cache = {}
        for group, sort in report['selection'][kind].items():
            try:
                if kind == 'discussions':
                    response = api.competition_list_topics(competition, sort_by=sort, page=1)
                    items = response.topics
                    if items is None or (not items and response.total_count):
                        raise ValueError('Missing topics despite nonempty listing')
                else:
                    items = api.kernels_list(competition=competition, sort_by=sort)
                    if items is None:
                        raise ValueError('Missing kernel listing')
                list_success += 1
            except Exception as error:
                report['errors'].append({'stage': 'listing', 'kind': kind, 'group': group, 'error': str(error)})
                continue
            entries = []
            for item in items[:5]:
                source_id = getattr(item, identity_key)
                if source_id not in cache:
                    try:
                        entry = fetch(api, competition, item, root, originals)
                        entry.update(fetched_at=now, run_id=run_id, scope='source_only', fetch_status='complete',
                                     engine_version=None, license=None, sdk_versions=report['sdk_versions'])
                        cache[source_id] = entry
                        report['fetched'].append({'kind': kind, identity_key: source_id, 'sha256': entry['sha256']})
                        history = inventory.setdefault(f'{kind}:{source_id}', [])
                        history.append(entry)
                    except Exception as error:
                        cache[source_id] = old_entries.get(source_id)
                        report['errors'].append({'stage': 'fetch', 'kind': kind, identity_key: source_id,
                                                 'error': str(error), 'preserved_previous': cache[source_id] is not None})
                if cache[source_id] is not None:
                    entries.append(cache[source_id])
            selected[group] = entries
        metadata[kind] = selected
    report['status'] = ('complete' if not report['errors'] else
                        'partial' if report['fetched'] else 'failed')
    try:
        if report['fetched']:
            originals['docs/collection_inventory.json'] = inventory_path.read_bytes() if inventory_path.exists() else None
            atomic_write(inventory_path, json_bytes(inventory))
        # A completely failed run must not touch the last-good metadata bytes.
        if list_success and (report['fetched'] or not report['errors']):
            metadata['collection'] = {key: report[key] for key in ('run_id', 'started_at', 'scope', 'status', 'coverage')}
            atomic_write(metadata_path, json_bytes(metadata))
    except (OSError, ValueError, TypeError) as error:
        report['status'] = 'failed'
        report['errors'].append({'stage': 'publish_manifest', 'error': str(error)})
        restore_files(root, originals, report)
    atomic_write(root / f'docs/collection_runs/{run_id}.json', json_bytes(report))
    print(f'Collection {report["status"]}: {len(report["fetched"])} sources, {len(report["errors"])} errors; run {run_id}')
    return 0 if report['status'] == 'complete' else 1


def main():
    # Keep the existing deployment path; importing this module for tests never authenticates.
    sys.path.insert(0, '~/.gemini/antigravity/brain/a8068519-c818-408b-8856-6802e8639fe9/scratch/venv/lib/python3.13/site-packages')
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
    except Exception as error:
        run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        atomic_write(Path(f'docs/collection_runs/{run_id}.json'), json_bytes(
            {'run_id': run_id, 'status': 'failed', 'scope': 'source_only',
             'errors': [{'stage': 'initialize_or_authenticate', 'error': str(error)}]}))
        return 1
    return collect(api)


if __name__ == '__main__':
    raise SystemExit(main())
