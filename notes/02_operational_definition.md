# Notes — Operational Definition (Section 4)

**분량:** Option 선택 + 영어 3~5 문장 정당화
**위치:** `paper.md` Section 4의 `[Author note]` 박스
**중요도:** 매우 높음. 이 선택이 §5의 데이터 소스와 회귀 모형 전체를 결정.

---

## 왜 본인이 결정해야 하는가

세 옵션은 각각 다른 이론적 commitment를 함축합니다.
- Option A를 고르면 → MEPP/dissipative-adaptation 문헌과 직접 대화
- Option B를 고르면 → 정보이론 + Landauer 한계까지 논의 확장 가능
- Option C를 고르면 → 경제학자(Acemoglu 류)에게 가장 친숙

본인이 어느 학술 커뮤니티와 대화하고 싶은지에 따라 선택이 달라집니다.

---

## Option A — Metabolic Baseline (가장 안전, 권장)

**측정**:
$$\text{EPA}_i^A = E_i^{AI} - E_i^{human}$$

- $E_i^{human}$ = 직업 $i$ 인간 작업자의 시간당 metabolic expenditure
  (kcal/h × 4184 J/kcal = J/h)
- $E_i^{AI}$ = 동등 작업량 처리 시 AI 시스템의 시간당 에너지 소비 (Wh × 3600
  = J/h)

**데이터**:
- O*NET 28.0 element "4.A.3.b.1 Performing General Physical Activities"
  (1~5 척도) → Ainsworth Compendium MET 값으로 변환
- AI inference 비용: @devries2023growing (2.9 Wh per query),
  @patterson2021carbon (training amortisation)

**장점**:
- MEPP/Schrödinger/Prigogine/England 라인과 직접 align
- 단위(J/h)가 명확하고 비교 가능
- 첫 논문에 가장 안전 — 학술적 정통성

**단점**:
- 인지 노동의 metabolic cost는 거의 일정 (뇌 ≈ 20W) — 변별력 약함
- 신체 노동 직업이 metabolic 측면에서 항상 "비싸"보임

**언제 적합한가**: 약한 형태 + PhilSci-Archive 제출 + 첫 논문이라면 이게 정답.

---

## Option B — Information-Throughput Baseline

**측정**:
$$\text{EPA}_i^B = \frac{E_i^{AI}}{\Theta_i^{AI}} - \frac{E_i^{human}}{\Theta_i^{human}}$$

- $\Theta_i$ = 직업 $i$의 정보 처리율 (bits/s)
- 분자 / 분모 = 단위 정보당 에너지 (J/bit)

**데이터**:
- 인간 throughput: 직업별 행동 분석 (typing rate, decision rate, motor
  output rate) — 데이터가 sparse
- AI throughput: 모델별 token rate (예: GPT-4 ~30 tok/s)

**장점**:
- 인지/신체 노동 동일 척도
- Landauer 한계 ($k_BT\ln 2 \approx 3 \times 10^{-21}$ J/bit at 300K)와 연결
  가능 → 이론적 깊이

**단점**:
- 측정 어려움. 직업 800개에 대한 throughput을 추정해야 함
- bits/s가 무엇을 의미하는지 직업마다 다름

**언제 적합한가**: 정보이론 reviewer가 있는 저널 (Entropy MDPI 같은) 후속
논문에서.

---

## Option C — Cost-of-Substitution Baseline

**측정**:
$$\text{EPA}_i^C = \frac{w_i^{human}}{c_e \cdot E_i^{human}} - \frac{w_i^{AI}}{c_e \cdot E_i^{AI}}$$

- $w_i$ = 시간당 비용 (USD/h)
- $c_e$ = 에너지 단가 (USD/J)

**데이터**:
- BLS OEWS wage data
- AI service pricing (예: GPT-4 API $0.03/1K tokens)
- 전기 요금 (~$0.10/kWh in US)

**장점**:
- 데이터가 가장 풍부
- 실제 substitution을 직접 측정

**단점**:
- 경제 변수 / 열역학 변수 혼동
- 가격이 에너지를 추적한다는 가정([@garrett2014long])이 본문에 들어가야 함
- Reviewer가 "이건 경제학이지 물리학이 아니다"고 말할 위험

**언제 적합한가**: Futures 또는 경제학 저널 후속 논문에서.

---

## 권장 (첫 논문 + PhilSci-Archive 기준)

**Primary: Option A** (metabolic). 데이터 정합성, 학술 정통성, 단위 명확성.

**Robustness check: Option B** 일부 직업(콜센터, 번역가, 코더 — 정보처리량이
잘 정의됨)에 대해 보조 분석.

**Option C는 다음 논문**에서 경제학자들과 대화할 때.

---

## Justification 영어 작성 가이드 (3~5 문장)

다음을 포함:
1. 어느 옵션을 primary로 선택했는지
2. 왜 — MEPP 문헌과의 align? 데이터 가용성? 변별력?
3. 약점을 어떻게 다룰지 — robustness check 또는 §7 Limitations에서 인정
4. (선택) 보조 옵션 사용 여부

### 예시 (참고용)

> *We adopt Option A — the metabolic baseline — as our primary operational
> definition. The choice is motivated by direct alignment with the MEPP and
> dissipative-adaptation literature on which §2 rests, by the unit-clarity of
> J/h, and by data availability for all 800 SOC codes via O\*NET and the
> Ainsworth Compendium. The principal weakness — that metabolic cost is
> approximately uniform across cognitive occupations because the human brain
> consumes ≈ 20 W regardless of cognitive load — we address with a robustness
> check using Option B (information-throughput) for the subset of occupations
> with well-defined symbolic output rates. Cost-based definitions (Option C)
> conflate economic and thermodynamic variables and are deferred to future
> work.*

---

## 본인 작성 영역

**선택**: [ ] Option A    [ ] Option B    [ ] Option C    [ ] Other

```
[여기에 3~5 문장 영어 정당화를 작성하세요.]




```

---

## 작성 후 다음 단계

1. 위 텍스트를 `paper.md` Section 4 끝의 `[Author note]` 박스에 복사
2. 선택한 Option에 따라 §5 데이터 소스 절을 약간 조정 (필요 시 제가 도와드림)
3. `notes/03_case_study.md`로 진행
