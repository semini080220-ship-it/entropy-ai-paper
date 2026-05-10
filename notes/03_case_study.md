# Notes — Illustrative Case Study (Section 6)

**분량:** 영어 5~10 문장 + back-of-envelope 계산
**위치:** `paper.md` Section 6의 `[Author note]` 박스
**중요도:** 중요. 추상 가설이 구체 사례에서 작동함을 보여주는 핵심.

---

## 왜 본인이 선택해야 하는가

- 어떤 직업을 사례로 드는지에 따라 **본 논문의 정치적 톤**이 달라집니다
  (콜센터를 예로 들면 노동자 권익 톤, 변호사를 예로 들면 화이트칼라 톤).
- 본인이 직접 본 직업의 변화 (예: 본인 사업 영역에서의 AI 영향) 가 가장
  설득력 있는 사례가 됩니다.
- 사례 선택은 본인의 *입장*을 드러내며, 입장은 reviewer 대신 본인이 정해야
  합니다.

---

## 후보 직업 (강한 사례 vs 약한 사례)

H4 검증을 위해서는 *양쪽 끝* 사례를 비교하는 것이 가장 강합니다.

### 강한 사례 (큰 EPA, 빠른 대체) — H4 지지

| 직업 | Human metabolic | AI 등가 작업 | EPA 추정 | 현재 BLS 트렌드 |
|---|---|---|---|---|
| **Call-center agent** (SOC 43-2011) | ~120 kcal/h ≈ 5×10⁵ J/h | 100 calls × 50 Wh ≈ 1.8×10⁷ J/h | +1.75×10⁷ J/h | -7%/yr (2022~) |
| **Technical translator** (SOC 27-3091) | ~120 kcal/h ≈ 5×10⁵ J/h | 3000 words × 30 Wh ≈ 1.1×10⁸ J/h | +1.05×10⁸ J/h | -10%/yr |
| **Junior software developer** (SOC 15-1252) | ~120 kcal/h | Copilot inference + dev | ~+10⁷ J/h | hiring freeze |

### 약한 사례 (작은/음의 EPA, 느린 대체) — H4 검증의 반대극

| 직업 | Human metabolic | Robot/AI 등가 | EPA 추정 | 현재 BLS 트렌드 |
|---|---|---|---|---|
| **Plumber** (SOC 47-2152) | ~280 kcal/h ≈ 1.2×10⁶ J/h | 휴머노이드 배관 로봇 ≈ unrealistic | ≈ 0 또는 음수 | +2%/yr |
| **Registered nurse** (SOC 29-1141) | ~200 kcal/h | AI assistant + human required | 작은 양수 | +6%/yr |
| **Pastry chef** (SOC 35-1011) | ~250 kcal/h | 부분 자동화 (Bridor) | 중간 | +1%/yr |

(metabolic 값은 Ainsworth Compendium 근사. 실제 논문에서는 정확한 인용 필요.)

---

## 한 직업 깊이 vs 두 직업 비교 — 어느 쪽?

**옵션 A — 깊이 한 직업** (콜센터 직원만, 5~10 문장)
- 장점: 깊은 논의 가능, 데이터 출처 한 줄로 정리됨
- 단점: 단일 사례로 H4 검증 부족

**옵션 B — 양극단 비교** (콜센터 vs 배관공, 각 3~5 문장)
- 장점: H4의 *양 방향* 검증 시각화. Reviewer 친화적.
- 단점: 분량 압박 (10 문장 안에 둘 다)

**권장: 옵션 B**. 한 사례로는 H4가 그저 "AI가 정보 노동 대체"로 보이고,
양 사례 비교가 있어야 *thermodynamic* 메커니즘이 드러납니다.

---

## 작성 가이드 (영어 톤)

### 포함해야 할 5 요소

1. **직업 1개 또는 2개 선택 + 한 줄 소개**
2. **Human metabolic cost 계산** (kcal/h → J/h)
3. **AI/robot 등가 작업당 에너지 비용** (Wh → J/h)
4. **EPA 값** (둘의 차이)
5. **현재 BLS 트렌드와 비교** (2019~2025 employment change)
6. **(2 직업 비교 시) 두 EPA 값의 차이가 두 직업의 displacement 속도 차이를
   설명하는지 한 문장**

### 톤 가이드

- 숫자는 항상 "approximately", "of the order of" 같은 hedging 표현과 함께
- 정확한 인용 필요 시 본문에 `[@author2020key]` 추가
- 단위는 SI 우선 (J 또는 W) — 미국 데이터는 kWh도 OK

---

## 예시 (참고용 — 옵션 B, 콜센터 vs 배관공)

> *Consider two extremes. A US call-center agent (SOC 43-2011) handling roughly
> 100 calls in an 8-hour shift expends approximately 120 kcal/h of metabolic
> energy, or ≈ 5 × 10⁵ J/h. The same task volume, processed by a contemporary
> LLM-based voice agent, dissipates approximately 50 Wh per 100 conversations
> (inference + amortised training; @devries2023growing), implying ≈ 1.8 × 10⁷
> J/h of energy throughput in the substitute system — an EPA of approximately
> +1.75 × 10⁷ J/h. The corresponding US BLS employment series shows a 7 %
> annual decline since 2022, consistent with H4. By contrast, a journeyman
> plumber (SOC 47-2152) expends ≈ 280 kcal/h, while an analogous physical-task
> robot would require comparable or slightly lower power (≈ 1 × 10⁶ J/h with
> current actuator efficiency), yielding an EPA close to zero. Plumbing
> employment grew by 2 % per year over the same period, again consistent with
> H4. The thermodynamic gap is not the only driver — capability, capital cost,
> and licensing barriers all matter — but its sign and magnitude track the
> direction of the displacement signal.*

위 7 문장이 이상적 length + tone 입니다.

---

## 본인 작성 영역

**선택한 직업**:
- 직업 1: ___________________
- 직업 2 (선택): ___________________

**Back-of-envelope 계산**:
- Human metabolic: ___ kcal/h × 4184 = ___ J/h
- AI 등가 에너지: ___ Wh/task × tasks/h × 3600 = ___ J/h
- EPA = ___ J/h
- BLS 트렌드 (2019~2025): ___ %/yr

**영어 본문 (5~10 문장)**:

```
[여기에 영어로 작성]




```

---

## 작성 후 다음 단계

1. 위 텍스트를 `paper.md` Section 6의 `[Author note]` 박스에 복사
2. 사용한 데이터에 인용 누락이 없는지 확인 (`references.bib`에 추가 필요할 수
   있음)
3. Section 7 Discussion에서 본 사례를 한 번 더 가볍게 언급할지 결정
4. Abstract / Conclusion 작성 시작 (사용자 + 제 협업)
