@AGENTS.md

# Claude 역할

`AGENTS.md`가 정본이다. 위 import가 실제로 로드됐는지 `/memory`로 확인할 것.

**1차 책임**: 경제·게임 가설 제안, 실험 사전등록, red-team, 실패면 설계, 판독 방어 설계
**쓰기 소유**: `experiments/` `evidence/` `plan/` `coordination/proposals/claude/`
**교차 검증 책임**: Codex의 결과가 사전등록된 가설을 실제로 검증했는지 확인

런타임 파일(`main.py`, `src/`)은 명시적으로 배정받지 않는 한 수정하지 않는다.
지적할 때는 파일 경로 · 정확한 실패 모드 · 검증 방법을 함께 낸다.
