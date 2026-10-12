# ENGINE_LOCK — 고정된 게임 엔진

고정일 2026-09-06 · 고정 주체 cowork(claude-opus-5) · 상태 **ACTIVE**

## 왜 고정하는가
이 게임의 진짜 규칙은 Kaggle 웹페이지가 아니라 `kaggle-environments` 패키지 소스다.
그리고 이 패키지는 **실제로 업데이트된다** — 2026-08-15에 밸런스 패치(당근·토마토·달걀 가격 곡선)가
배포되었고 사다리도 같은 날 전환됐다. 버전을 박아두지 않으면 "A가 B보다 낫다"는 측정이
어느 게임에 대한 얘기였는지 알 수 없게 되고, 실험 기록 전체가 무효가 된다.

## 고정 대상

| 항목 | 값 |
|---|---|
| 패키지 | `kaggle-environments` |
| **버전** | **1.32.7** (2026-09-06 기준 PyPI 최신) |
| requires_python | **>= 3.11** ← 로컬 파이썬이 3.11 미만이면 설치 자체가 안 된다 |
| wheel sha256 | `2a1bb862ad2d6463080f80f6a766f46d94b53fd57168cfeddb9857fc3dbc4c8f` |
| sdist sha256 | `4679d757e3677ada652d239679767c678a317c3fabdc58a332a3b6c9566ce1c0` |
| PyPI 업로드 | 2026-08-15T01:35:47Z |

## 환경 파일 SHA-256 (`kaggle_environments/envs/kaggriculture/`)

| 파일 | 크기 | sha256 |
|---|---:|---|
| `kaggriculture.py` | 40,356 B | `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e` |
| `kaggriculture.json` | 6,002 B | `a82c89c1a2315b93f39775d8e025471a01b738647c9772658368ee6b1b6f4867` |
| `README.md` | 26,824 B | `3081e52baf8eb2da5d861acc63a3636ce29425f6bdb79a67036ba234ac4ade00` |
| `AGENTS.md` | 13,708 B | `e1a80501a7b02a212eaac9370ada4129a64e0ee6cb3cbc790f3d77d22863fe22` |

## 로컬 설치 검증 (각 머신에서 1회)

```bash
python3 --version                      # 3.11 이상이어야 함
pip install -U 'kaggle-environments==1.32.7'
python3 - <<'PY'
import hashlib, os, kaggle_environments as k
d = os.path.join(os.path.dirname(k.__file__), "envs", "kaggriculture")
for f in ("kaggriculture.py", "kaggriculture.json"):
    p = os.path.join(d, f)
    print(f, hashlib.sha256(open(p,'rb').read()).hexdigest())
PY
```
위 두 해시가 표와 다르면 **실험을 시작하지 말고 BOARD.md에 BLOCK을 올린다.**

## 패치 감시 (Gemini, 매일)
- PyPI `kaggle-environments` 최신 버전
- competition discussion의 balance change 공지
- 리플레이 JSON의 `module_version` 필드
새 버전이 나오면 **자동 업그레이드 금지.** 별도 migration 실험으로 승격 판정을 거친다.

## 이력
| 날짜 | 버전 | 사유 |
|---|---|---|
| 2026-09-06 | 1.32.7 | 최초 고정 |
