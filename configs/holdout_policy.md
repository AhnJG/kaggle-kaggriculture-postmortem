# holdout 정책

## 용어
- **holdout** — 모든 에이전트가 읽을 수 있는 폴더의 seed. **이건 blind가 아니다.** 재사용 가능하지만 과적합된다.
- **blind** — 코드와 config를 먼저 동결한 뒤 **사람이 새로 생성**한 seed. 집계가 끝나면 **재사용하지 않는다.**

## 규칙
1. 일상 A/B는 `configs/paired_seeds.yaml`(holdout)로 한다.
2. 승격 판정 직전에만 blind set을 쓴다. 사람이 생성하고, 쓴 seed는 폐기 목록에 기록한다.
3. **결과를 보고 seed를 추가하지 않는다.** 표본 수는 pilot으로 정하고 사전 선언한다.
4. 모든 비교는 **같은 seed, 양 좌석 교대** 페어드다.
