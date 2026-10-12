# P1c Collection Plan & Provenance (정정됨)

## 1. 수집 계획 (사전 고정)
- **조회 시작 시각 (T)**: `2026-09-17T16:46:04Z` (UTC)
- **수집 대상 Window**: `2026-09-16T16:46:04Z` ~ `2026-09-17T16:46:04Z` (T 기준 직전 24시간)
- **상태 조건**: `COMPLETE` 경기
- **대상 Submission**: 
  - `56165718` (EXP-006)
  - `56175620` (EXP-007)

## 2. 수집 원자료 정정 (Provenance)
- **원본 API Response 보존 실패**: 수집 당시에 다운로드했던 `episodes_56165718.json`, `episodes_56175620.json` (각각 submission별 완료 UTC와 episode ID가 매핑된 Kaggle API 응답 원본) 파일들을 스크래치 파일 정리 과정에서 삭제했습니다.
- **영향**: 원본 API 응답 메타데이터가 유실되었으므로, 확보된 77개 replay 파일이 **정확히 직전 24시간 window에 속하는지**, 그리고 **어느 submission에 46개/31개가 나뉘는지** 교차 검증할 수 없습니다. 따라서 해당 구분은 **N/A**로 정정합니다.
- 새로 API를 조회하여 과거 수집 시점의 snapshot인 것처럼 복구(위조)하지 않았습니다. 
- 보존된 원자료: `evidence/raw/p1c_replays/*.json` (총 77개).
