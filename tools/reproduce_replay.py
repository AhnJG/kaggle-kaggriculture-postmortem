#!/usr/bin/env python3
"""Verify both recorded action streams against original game state, never strength."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import time

ENGINE_SHA = 'bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e'
OBS_FIELDS = ('day', 'hour', 'farms', 'market', 'player', 'private', 'town')


def tape_agent(replay, seat):
    def agent(obs, config=None):
        return copy.deepcopy(replay['steps'][int(obs['step']) + 1][seat]['action'])
    return agent


def projection(state):
    # Exclude runtime/overage/info and framework's seat-0-only step bookkeeping.
    return {'observation': {k: state['observation'][k] for k in OBS_FIELDS},
            'reward': state['reward'], 'status': state['status']}


def first_difference(expected, actual, path=''):
    if isinstance(expected, dict) and isinstance(actual, dict):
        if expected.keys() != actual.keys():
            return {'path': path, 'expected_keys': sorted(expected), 'actual_keys': sorted(actual)}
        for key in expected:
            diff = first_difference(expected[key], actual[key], path + '/' + str(key))
            if diff is not None:
                return diff
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            return {'path': path, 'expected_length': len(expected), 'actual_length': len(actual)}
        for i, (left, right) in enumerate(zip(expected, actual)):
            diff = first_difference(left, right, path + '/' + str(i))
            if diff is not None:
                return diff
    elif expected != actual:
        return {'path': path, 'expected': expected, 'actual': actual}
    return None


def reproduce(replay):
    from kaggle_environments import make
    from kaggle_environments.envs.kaggriculture import kaggriculture as engine
    engine_sha = hashlib.sha256(Path(engine.__file__).read_bytes()).hexdigest()
    if engine_sha != ENGINE_SHA or replay.get('module_version') != '1.32.7':
        raise ValueError('engine lock or replay module_version mismatch')
    seed = replay.get('info', {}).get('seed')
    if seed is None:
        raise ValueError('original seed missing')
    config = copy.deepcopy(replay['configuration'])
    if config.get('seed') not in (None, seed):
        raise ValueError('conflicting seed fields')
    config['seed'] = seed
    expected_steps = config['episodeSteps']
    if len(replay['steps']) != expected_steps or replay['statuses'] != ['DONE', 'DONE']:
        raise ValueError('incomplete or unsuccessful replay')
    started = time.perf_counter()
    env = make('kaggriculture', configuration=config)
    env.run([tape_agent(replay, 0), tape_agent(replay, 1)])
    action_matches = state_matches = 0
    differences = []
    for i, (expected, actual) in enumerate(zip(replay['steps'], env.steps)):
        for seat in (0, 1):
            if i:
                diff = first_difference(expected[seat]['action'], actual[seat]['action'])
                action_matches += diff is None
                if diff is not None and len(differences) < 5:
                    differences.append({'step': i, 'seat': seat, 'kind': 'action', **diff})
            diff = first_difference(projection(expected[seat]), projection(actual[seat]))
            state_matches += diff is None
            if diff is not None and len(differences) < 5:
                differences.append({'step': i, 'seat': seat, 'kind': 'state', **diff})
    rewards = [s['reward'] for s in env.steps[-1]]
    statuses = [s['status'] for s in env.steps[-1]]
    passed = (len(env.steps) == expected_steps and action_matches == 2 * (expected_steps - 1)
              and state_matches == 2 * expected_steps and rewards == replay['rewards']
              and statuses == replay['statuses'])
    return {'verdict': 'PASS' if passed else 'FAILURE', 'episode_id': replay.get('info', {}).get('EpisodeId'),
            'seed': seed, 'engine_sha256': engine_sha, 'expected_steps': expected_steps,
            'actual_steps': len(env.steps), 'action_matches': action_matches,
            'action_total': 2 * (expected_steps - 1), 'state_matches': state_matches,
            'state_total': 2 * expected_steps, 'expected_rewards': replay['rewards'],
            'actual_rewards': rewards, 'statuses': statuses, 'first_differences': differences,
            'wall_seconds': time.perf_counter() - started,
            'projection': list(OBS_FIELDS) + ['reward', 'status'],
            'scope': 'Original two-sided transcript reproduction only; no policy generalization claim.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.replay.read_bytes()
    try:
        result = reproduce(json.loads(raw))
    except (KeyError, ValueError, IndexError) as exc:
        result = {'verdict': 'BLOCKED', 'error': str(exc)}
    result.update({'replay': str(args.replay), 'replay_sha256': hashlib.sha256(raw).hexdigest(),
                   'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
