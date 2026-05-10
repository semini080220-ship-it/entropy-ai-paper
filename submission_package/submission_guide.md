# v2.0 Submission Package — 사용자 가이드

논문은 v2.0 (`paper.pdf` 335KB)이 학술지 제출 준비 완료 상태입니다. 이 폴더에는 제출 시 필요한 보조 자료가 들어있습니다.

## 추천 저널 (1순위)

### Entropy (MDPI) — 1순위 추천
- IF: 2.7
- APC: ~2,600 CHF (≈ 400만원) — **학생/independent researcher waiver 가능**
- 평균 심사 기간: 30~40일
- Open access (CC-BY 4.0 호환)
- 학제간 (열역학 + 정보이론 + 경제학 다 환영)
- 제출: https://susy.mdpi.com/login.php

**APC waiver 신청 방법:**
1. 제출 portal에서 "Discount voucher / Fee waiver request" 칸
2. 본문에 적기: "Independent researcher, undergraduate student, no institutional funding"
3. 보통 30~50% 할인 가능 (full waiver는 드물지만 신청 권장)

### Futures (Elsevier) — 2순위
- IF: 4.4
- APC: hybrid — non-open access는 무료, open access는 ~3,000 USD
- 미래학 저널, AI 사회적 함의 부분 강조 가능
- 제출: https://www.editorialmanager.com/jftr/

### Foundations of Science (Springer) — 3순위
- IF: 1.6
- 학제간 철학+과학
- 제출: https://www.editorialmanager.com/foos/

## 제출 체크리스트 (Entropy 기준)

### 원고
- [x] Title under 200 chars
- [x] Abstract 150~300 words (~280)
- [x] Keywords 3~10 (7개)
- [x] Author affiliation 기재
- [x] Corresponding author email 기재
- [x] References (BibTeX 28개)
- [x] Tables + figures 포함
- [ ] **MDPI LaTeX 템플릿 변환** (선택, MDPI가 typesetting 해주기도 함)
- [ ] Line numbers 추가 (review용, 권장)

### 데이터 가용성 명시
- [x] Companion dataset DOI 인용 (`paper.md` §9.5)
- [x] Construction code 공개 (Python)
- [x] License: CC-BY 4.0

### Conflict of interest
- [x] None to declare (cover letter에 명시)

### Funding
- [x] No funding (independent researcher)

### 추천 reviewer (선택, 권장)
- **Axel Kleidon** (Max Planck Institute, Jena) — MEPP 권위자, 본문 핵심 인용
- **Jeremy England** (Georgia Tech / GSK) — dissipative adaptation
- **Edward Felten** (Princeton) — AIOE 데이터 소스 (혹은 conflict)
- **L.M. Martyushev** (Ural Federal University) — MEPP 리뷰

## Submission 절차 (Entropy 기준)

1. https://susy.mdpi.com/login.php 가입 (Zenodo 계정과 별도)
2. "Submit a manuscript" → "Entropy" 선택
3. Article type: **Article** (또는 **Concept Paper**)
4. Manuscript 파일 업로드: `paper.pdf`
5. Cover letter 업로드: `cover_letter.txt`
6. References: 자동 추출
7. 메타데이터 (제목, abstract, 저자, keywords)
8. APC 페이지: waiver request 작성
9. 추천 reviewer 입력 (선택)
10. **Submit** 버튼

## 제출 후

- Editorial assessment: 보통 1주
- Peer review (편집자가 reviewer 모집): 1~2개월
- Major / Minor revision 받을 가능성 높음 (첫 학술 paper에서 정상)
- Revision 1~2회 후 accept

## 만약 reject되면

- Entropy → Futures → Foundations of Science 순서로 재제출
- 각 저널마다 cover letter 약간 수정 필요
- arXiv에 미리 올려두면 동시에 다른 저널 시도 가능 (가장 안전)

## 학술 인용 형식 (정식 출판 후)

```
Um, S. (2026). Informational Task Entropy and the Selection of
Occupations Under AI-Driven Substitution. Entropy [or other journal],
[volume](issue), pages. https://doi.org/...
```

Preprint 인용 (출판 전):
```
Um, S. (2026). Informational Task Entropy and the Selection of
Occupations Under AI-Driven Substitution (v2.0). Zenodo.
https://doi.org/10.5281/zenodo.20111227
```

## 한 줄 메시지

**제출은 본인이 직접 하셔야 합니다** (저널 portal 로그인 + 메타데이터 입력 + click submit). 제가 도울 수 있는 것은 cover letter, response-to-reviewer letter, formatting 변환 등. 첫 reject 받으셔도 좌절 마세요 — 학계 표준입니다.
