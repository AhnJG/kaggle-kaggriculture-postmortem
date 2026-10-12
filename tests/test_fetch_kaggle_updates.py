"""Network-free regression checks for public source collection failures."""
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('collector', Path(__file__).parents[1] / 'scripts/fetch_kaggle_updates.py')
collector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(collector)


class Response(SimpleNamespace):
    def to_dict(self, ignore_defaults=False):
        return vars(self)


def topic(number, votes=0):
    return Response(id=number, title=f'Topic {number}', votes=votes, author_name='Staff',
                    last_comment_post_date='2026-09-15T00:00:00Z')


def message(number, content, replies=()):
    return Response(id=number, content=content, raw_markdown=content, author_name='Reader',
                    post_date=f'2026-09-15T00:00:{number:02d}Z', is_deleted=False, votes=0, replies=list(replies))


class FakeApi:
    def __init__(self):
        self.calls = []
        self.fail_listings = False
        self.fail_messages = False
        self.fail_pull = False
        self.topics = {'top': [topic(1, 23)], 'recent': [topic(2, 0), topic(1, 23)]}
        self.kernels = [Response(ref='author/bot', title='Bot', total_votes=17, current_version_number=4)]
        self.source = 'print("source only")\n'

    def competition_list_topics(self, competition, sort_by, page):
        self.calls.append(('topics', sort_by, page))
        if self.fail_listings:
            raise RuntimeError('listing unavailable')
        return Response(topics=self.topics[sort_by], total_count=99)

    def competition_list_topic_messages(self, competition, topic_id, sort_by, page_size):
        self.calls.append(('messages', topic_id, sort_by, page_size))
        if self.fail_messages:
            raise RuntimeError('messages unavailable')
        return Response(messages=[message(1, 'ROOT', [message(2, 'CORRECTION')])])

    def kernels_list(self, competition, sort_by):
        self.calls.append(('kernels', sort_by))
        if self.fail_listings:
            raise RuntimeError('listing unavailable')
        return self.kernels

    def kernels_pull(self, ref, path, metadata):
        self.calls.append(('pull', ref, metadata))
        if self.fail_pull:
            raise RuntimeError('source unavailable')
        folder = Path(path)
        # Enumeration must not select this helper instead of code_file.
        (folder / 'helper.py').write_text('WRONG SOURCE')
        (folder / 'main.py').write_text(self.source)
        (folder / 'kernel-metadata.json').write_text(json.dumps(
            {'code_file': 'main.py', 'language': 'python', 'dataset_sources': ['author/data']}))


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.api = FakeApi()

    def run_collection(self):
        with patch('builtins.print'):
            return collector.collect(self.api, self.root)

    def metadata(self):
        return json.loads((self.root / 'docs/latest_metadata.json').read_text())

    def report(self):
        return json.loads(sorted((self.root / 'docs/collection_runs').glob('*.json'))[-1].read_text())

    def test_sdk_fields_server_sort_reply_tree_and_ref_dedup(self):
        self.assertEqual(self.run_collection(), 0)
        data = self.metadata()
        top = data['discussions']['top_voted'][0]
        recent = data['discussions']['recent'][0]
        self.assertEqual((top['id'], top['score'], recent['id'], recent['score']), (1, 23, 2, 0))
        self.assertEqual(top['author'], 'Staff')
        text = (self.root / top['path']).read_text()
        self.assertIn('CORRECTION', text)
        self.assertIn('ID: 2; API parent: 1', text)
        self.assertLess(text.index('ROOT'), text.index('CORRECTION'))
        self.assertIn(('topics', 'top', 1), self.api.calls)
        self.assertIn(('topics', 'recent', 1), self.api.calls)
        self.assertEqual(self.api.calls.count(('messages', 1, 'old', -1)), 1)
        self.assertEqual(self.api.calls.count(('pull', 'author/bot', True)), 1)
        code = data['codes']['top_voted'][0]
        self.assertEqual(code['score'], 17)
        self.assertEqual(code['listed_version'], 4)
        self.assertIsNone(code['source_version'])
        self.assertEqual((self.root / code['path']).read_text(), self.api.source)
        self.assertEqual(code['scope'], 'source_only')
        self.assertEqual(self.report()['status'], 'complete')

    def test_partial_failure_preserves_last_good_entries_and_raw_bytes(self):
        self.run_collection()
        before = self.metadata()
        old = before['discussions']['top_voted'][0]
        old_bytes = (self.root / old['path']).read_bytes()
        self.api.fail_messages = True
        self.api.source = '# changed\n'
        self.assertEqual(self.run_collection(), 1)
        self.assertEqual(self.metadata()['discussions'], before['discussions'])
        self.assertEqual((self.root / old['path']).read_bytes(), old_bytes)
        self.assertEqual(self.report()['status'], 'partial')
        self.assertTrue(self.report()['errors'][0]['preserved_previous'])
        self.assertNotEqual(self.metadata()['codes'], before['codes'])

    def test_total_listing_failure_preserves_metadata_byte_for_byte(self):
        self.run_collection()
        path = self.root / 'docs/latest_metadata.json'
        before = path.read_bytes()
        self.api.fail_listings = True
        self.assertEqual(self.run_collection(), 1)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(self.report()['status'], 'failed')
        self.assertEqual(len(self.report()['errors']), 4)

    def test_source_failure_does_not_replace_last_good_code(self):
        self.run_collection()
        before = self.metadata()['codes']
        self.api.fail_pull = True
        self.assertEqual(self.run_collection(), 1)
        self.assertEqual(self.metadata()['codes'], before)

    def test_prior_snapshots_and_provenance_survive_updated_source(self):
        self.run_collection()
        before = self.metadata()['codes']['top_voted'][0]
        self.api.source = '# version two\n'
        self.run_collection()
        after = self.metadata()['codes']['top_voted'][0]
        self.assertNotEqual(before['sha256'], after['sha256'])
        self.assertEqual((self.root / before['snapshot_path']).read_text(), 'print("source only")\n')
        inventory = json.loads((self.root / 'docs/collection_inventory.json').read_text())
        self.assertEqual(len(inventory['codes:author/bot']), 2)
        raw = json.loads((self.root / after['source_metadata']['snapshot_path']).read_text())
        self.assertEqual(raw['dataset_sources'], ['author/data'])
        self.assertIsNone(after['engine_version'])
        self.assertIsNone(after['license'])

    def test_missing_votes_are_distinct_from_real_zero(self):
        del self.api.topics['top'][0].votes
        del self.api.kernels[0].total_votes
        self.run_collection()
        self.assertIsNone(self.metadata()['discussions']['top_voted'][0]['score'])
        self.assertEqual(self.metadata()['discussions']['recent'][0]['score'], 0)
        self.assertIsNone(self.metadata()['codes']['top_voted'][0]['score'])

    def test_atomic_replace_failure_keeps_existing_bytes_and_cleans_temp(self):
        path = self.root / 'existing.json'
        path.write_bytes(b'last good')
        with patch.object(collector.os, 'replace', side_effect=OSError('interrupted')):
            with self.assertRaises(OSError):
                collector.atomic_write(path, b'replacement')
        self.assertEqual(path.read_bytes(), b'last good')
        self.assertEqual(list(self.root.iterdir()), [path])

    def test_empty_raw_markdown_preserves_content(self):
        msg = message(1, 'BODY')
        msg.raw_markdown = ''
        with patch.object(self.api, 'competition_list_topic_messages', return_value=Response(messages=[msg])):
            self.assertEqual(self.run_collection(), 0)
        entry = self.metadata()['discussions']['top_voted'][0]
        self.assertIn('BODY', (self.root / entry['path']).read_text())

    def test_manifest_write_failure_is_reported_and_nonzero(self):
        self.run_collection()
        target = self.root / 'docs/latest_metadata.json'
        before = target.read_bytes()
        original = collector.atomic_write
        def fail_metadata(path, data):
            if path == target:
                raise OSError('metadata disk failure')
            return original(path, data)
        with patch.object(collector, 'atomic_write', side_effect=fail_metadata):
            self.assertEqual(self.run_collection(), 1)
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual(self.report()['status'], 'failed')
        self.assertEqual(self.report()['errors'][-1]['stage'], 'publish_manifest')

    def test_legacy_alias_and_inventory_rollback_on_publish_failure(self):
        self.run_collection()
        target = self.root / 'docs/latest_metadata.json'
        legacy = self.metadata()
        for kind in ('codes', 'discussions'):
            for group in ('top_voted', 'recent'):
                legacy[kind][group] = [{key: value for key, value in entry.items()
                                        if key in ('id', 'ref', 'title', 'path', 'score')}
                                       for entry in legacy[kind][group]]
        target.write_text(json.dumps(legacy))
        before = target.read_bytes()
        alias = self.root / legacy['codes']['top_voted'][0]['path']
        old_source = alias.read_bytes()
        inventory = self.root / 'docs/collection_inventory.json'
        old_inventory = inventory.read_bytes()
        self.api.source = '# NEW BYTES\n'
        original = collector.atomic_write
        def fail_metadata(path, data):
            if path == target:
                raise OSError('publish failure')
            return original(path, data)
        with patch.object(collector, 'atomic_write', side_effect=fail_metadata):
            self.assertEqual(self.run_collection(), 1)
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual(alias.read_bytes(), old_source)
        self.assertEqual(inventory.read_bytes(), old_inventory)
        self.assertEqual(self.report()['status'], 'failed')

    def test_new_aliases_and_inventory_removed_on_publish_failure(self):
        target = self.root / 'docs/latest_metadata.json'
        original = collector.atomic_write
        def fail_metadata(path, data):
            if path == target:
                raise OSError('publish failure')
            return original(path, data)
        with patch.object(collector, 'atomic_write', side_effect=fail_metadata):
            self.assertEqual(self.run_collection(), 1)
        self.assertFalse(target.exists())
        self.assertFalse((self.root / 'docs/code/author_bot.py').exists())
        self.assertFalse((self.root / 'docs/discussion/1_Topic_1.md').exists())
        self.assertFalse((self.root / 'docs/collection_inventory.json').exists())
        self.assertTrue(list((self.root / 'docs/collection_snapshots').iterdir()))

    def test_rollback_failure_is_reported_and_nonzero(self):
        self.run_collection()
        target = self.root / 'docs/latest_metadata.json'
        alias = self.root / 'docs/code/author_bot.py'
        old_source = alias.read_bytes()
        self.api.source = '# new bytes\n'
        original = collector.atomic_write
        def fail_publish_and_rollback(path, data):
            if path == target or (path == alias and data == old_source):
                raise OSError('disk refuses write')
            return original(path, data)
        with patch.object(collector, 'atomic_write', side_effect=fail_publish_and_rollback):
            self.assertEqual(self.run_collection(), 1)
        self.assertEqual(self.report()['status'], 'failed')
        rollback = [error for error in self.report()['errors'] if error['stage'] == 'rollback']
        self.assertEqual([error['path'] for error in rollback], ['docs/code/author_bot.py'])

    def test_corrupt_previous_manifest_fails_without_overwrite(self):
        path = self.root / 'docs/latest_metadata.json'
        path.parent.mkdir()
        path.write_bytes(b'broken JSON')
        self.assertEqual(self.run_collection(), 1)
        self.assertEqual(path.read_bytes(), b'broken JSON')
        self.assertEqual(self.api.calls, [])
        self.assertEqual(self.report()['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
