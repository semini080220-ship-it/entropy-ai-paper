# Entropy-Production Account of AI-Driven Job Displacement

선택 (확정):
- 언어: **영어**
- 주장 형태: **약한 형태 — MEPP 해석** (목적론 회피)
- 출판: **PhilSci-Archive preprint**

## 파일 구조

```
entropy-ai-paper/
├── README.md                # (이 파일) 작업 가이드
├── paper.md                 # 영문 초고 (약 70% 작성됨)
├── references.bib           # BibTeX 참고문헌 (16개)
└── notes/                   # 본인이 채울 3 부분
    ├── 01_thesis_statement.md       # Section 1 마지막 단락
    ├── 02_operational_definition.md # Section 4 Option 선택
    └── 03_case_study.md             # Section 6 직업 사례
```

## 작업 흐름 (총 6 단계)

1. `notes/01_thesis_statement.md` — 영어 5~7 문장 작성
2. `notes/02_operational_definition.md` — Option A/B/C 선택 + 3~5 문장 정당화
3. `notes/03_case_study.md` — 직업 1개 선택, 영어 5~10 문장
4. 채운 내용을 `paper.md`의 `[Author note]` 박스에 복사해 붙여넣기
5. Abstract / Discussion / Conclusion 마무리 (제가 도와드릴 수 있음)
6. PDF 빌드 → PhilSci-Archive 업로드

## 가설 요약 (간단히)

- **H1**: MEPP — 우주 거시 동역학은 엔트로피 생산을 가속하는 경로를 선호한다.
- **H2**: 생명은 비-생명보다 엔트로피 효율적인 dissipator이다 (England).
- **H3**: 정보처리 기술 진화는 H2의 연속이다.
- **H4 (★ 검증 가능, 본 논문의 진짜 기여):** AI 일자리 대체의 시간 순서는 인간↔AI 엔트로피 생산 격차에 의해 부분적으로 예측된다.

## PDF 빌드 (검증됨 2026-05-10)

```powershell
pandoc paper.md --citeproc --bibliography=references.bib --pdf-engine=typst -o paper.pdf
```

설치된 도구 (winget으로 자동 설치됨):
- Pandoc 3.9.0.2
- Typst 0.14.2

향후 paper.md 수정 후 v0.2 빌드 시 위 한 줄만 실행.

## Zenodo 업로드

1. https://zenodo.org/ 가입 (Google 계정으로 즉시 가능)
2. 로그인 후 우상단 "+ New upload"
3. 파일 영역에 `paper.pdf` drag & drop
4. Upload type: **Publication** → **Preprint**
5. **Publication date**: 2026-05-10
6. **Title**, **Authors**, **Description** 입력 (아래 cheat sheet)
7. **License**: Creative Commons Attribution 4.0 International (CC-BY 4.0)
8. **Version**: v0.1
9. **Save** → **Publish** → 즉시 DOI 발급 + 공개

### Zenodo 메타데이터 cheat sheet

복사해서 그대로 붙여넣기:

**Title:**
> Thermodynamic Selection of Labor: Why High-Dissipation Occupations Are Preserved Under AI-Driven Substitution

**Authors:**
- Family name: Eom
- Given names: Semin (엄세민)
- Affiliation: Independent Researcher
- ORCID: (없으면 비워두면 됨, 5분이면 https://orcid.org/ 에서 무료 발급 가능)

**Description (Abstract 그대로 — v0.2 업데이트 반영):**
> We propose a thermodynamic reframing of the empirical phenomenon of AI-driven labor displacement. Existing models of automation exposure (Acemoglu and Restrepo 2020; Eloundou et al. 2023) explain which occupations are technically substitutable, but leave residual variation in the speed of substitution. We hypothesise that occupations characterised by high human metabolic entropy production per unit time are differentially preserved under AI-driven substitution; the temporal order of displacement is inversely related to the human dissipation rate of the occupation. Equivalently, surviving occupations are those for which the entropy-production gap between human worker and AI substitute is small or negative, so that the marginal entropy gain from substitution is too small to drive MEPP-consistent selection. Building on the Maximum Entropy Production Principle (Kleidon 2010; Martyushev and Seleznev 2006) and on Jeremy England's dissipative-adaptation programme (England 2013, 2015), we develop the framework, propose an operational definition based on metabolic-equivalent ratings (O*NET / Ainsworth Compendium), sketch a regression strategy using BLS occupational data for 2019–2025, and illustrate the framework with a case-study comparison of call-center work and skilled trades. We then survey five strands of existing empirical evidence — the routinisability gradient (Autor, Levy and Murnane 2003), capability-based AI exposure measures (Frey and Osborne 2017; Eloundou et al. 2023), recent generative-AI experiments (Noy and Zhang 2023; Brynjolfsson, Li and Raymond 2023), BLS occupational data, and the energy-economy linkage (Garrett 2014) — all consistent with H4. The cosmological proposals of Smolin (1992) and Crane (1994) inspire but do not constrain the empirical claim. We conclude with policy implications for redistribution and for the regulation of AI energy consumption.

**Keywords (콤마로 구분, Zenodo는 한 줄에 입력):**
> maximum entropy production principle, dissipative adaptation, artificial intelligence, labor displacement, non-equilibrium thermodynamics, future of work, entropy-production asymmetry

**Additional notes:**
> Preliminary preprint, v0.1. Comments and corrections welcome at semini080220@gmail.com. Subsequent versions will refine the case study and incorporate empirical regression results.

## 키워드 제안 (제출 시)

- maximum entropy production principle
- dissipative adaptation
- artificial intelligence
- labor displacement
- thermoeconomics
- non-equilibrium thermodynamics
- future of work

## 후속 단계 (Preprint 이후 정식 저널을 원할 때)

| 저널 | IF | APC | 적합도 |
|---|---|---|---|
| Entropy (MDPI) | 2.7 | ~2600 CHF | ★★★★★ |
| Futures (Elsevier) | 4.4 | hybrid | ★★★★ |
| Foundations of Science | 1.6 | hybrid | ★★★★ |

## 작성 시 주의 (CLAUDE.md 규칙 적용)

- 목적론 표현(teleology) 금지: "for the sake of", "in order to" 등 X
- 메커니즘 표현(MEPP) 사용: "selected for", "predicts", "correlates with" O
- "I'm pretty sure" → 검증 후 작성
- 출판 전 모든 인용을 한 번 더 검증 (특히 연도, DOI)
