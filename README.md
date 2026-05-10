# Informational Task Entropy and the Selection of Occupations Under AI-Driven Substitution

[![Paper DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20111476.svg)](https://doi.org/10.5281/zenodo.20111476)
[![Dataset DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20111527.svg)](https://doi.org/10.5281/zenodo.20111527)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

> **Open-access preprint + companion dataset.** A thermodynamic-informational
> reframing of AI-driven occupational displacement, with an Informational
> Resilience Index (IRI) for 698 US occupations.

## Summary

Existing models of AI-driven labor displacement (Acemoglu and Restrepo
2020; Eloundou et al. 2023) explain *which* occupations are technically
substitutable, but leave residual variation in the *speed* of substitution.
This paper proposes that occupations of **high informational task
entropy** — high variability and unpredictability of work activities —
are differentially preserved, while occupations of low informational
entropy are differentially displaced.

The hypothesis is tested on the full US BLS 2019–2024 occupational panel
(N = 707):

| Specification                              | $\hat{\beta}_{H^{\text{info}}}$ | $p$ (one-sided) |
|--------------------------------------------|---------------------------------|-----------------|
| H_info only                                | $+0.032$                        | $0.004$         |
| H_info + thermodynamic + JobZone + wage    | $+0.057$                        | $< 10^{-5}$     |
| + GPT-γ control                            | $+0.078$                        | $< 10^{-9}$     |
| + GPT-β control                            | $+0.129$                        | $< 10^{-13}$    |

A composite **Informational Resilience Index (IRI)** ─
$\text{IRI}_i = z(H^{\text{info}}_i) + z(\text{JobZone}_i) + z(\log w_i)$
─ correlates with subsequent employment growth at Pearson $r = +0.328$
(N = 698, $p = 5.8 \times 10^{-19}$). The result survives multi-source
robustness checks (Felten et al. 2021 AIOE alternative proxy,
$p < 10^{-10}$) and 2-digit NAICS industry fixed effects ($t = +7.86$,
$p = 1.7 \times 10^{-14}$, $\Delta R^2 = +0.077$ on top of industry
effects).

## Citation

```bibtex
@misc{um2026info_task_entropy,
  author = {Um, Semin},
  title  = {Informational Task Entropy and the Selection of Occupations
            Under AI-Driven Substitution},
  year   = {2026},
  doi    = {10.5281/zenodo.20111476},
  url    = {https://doi.org/10.5281/zenodo.20111476},
  note   = {v2.0, Zenodo preprint, CC-BY 4.0}
}

@dataset{um2026iri,
  author = {Um, Semin},
  title  = {Informational Resilience Index (IRI) -- Scores for 698 US
            Occupations, 2019-2024},
  year   = {2026},
  doi    = {10.5281/zenodo.20111527},
  url    = {https://doi.org/10.5281/zenodo.20111527},
  note   = {Companion dataset, CC-BY 4.0}
}
```

## Repository structure

```
entropy-ai-paper/
├── paper.md                  Source manuscript (Pandoc Markdown)
├── paper.pdf                 Compiled v2.0 (335 KB)
├── references.bib            BibTeX, 30 entries
├── README.md                 This file
├── README_ko.md              Korean working notes / Zenodo guide
├── LICENSE                   CC-BY 4.0
├── regression/               Analysis scripts and outputs
│   ├── pilot_regression.py           §5.1 Phase A pilot (N=10)
│   ├── process_onet.py               O*NET physical-demand index
│   ├── phase_b_regression.py         §5.2 Phase B (N=707, BLS x O*NET)
│   ├── phase_b_with_control.py       Phase B + GPT exposure controls
│   ├── phase_c_combined.py           v1.0 H_info reframe regression
│   ├── iri_construction.py           §9 IRI composite index
│   ├── v12_v13_robustness.py         §9.6 Felten + §9.7 Industry FE
│   ├── inspect_workcontext.py        Diagnostic
│   ├── *.json                        Per-step regression results
│   ├── iri_score_table.csv           ★ IRI scores for 698 SOC codes
│   └── phase_b_final.csv             Merged BLS x O*NET dataset
├── submission_package/       Journal submission materials
│   ├── cover_letter.txt              For Entropy (MDPI)
│   └── submission_guide.md           Korean step-by-step
└── notes/                    Author working notes (early drafts)
```

`regression/data/` (raw BLS, O\*NET, Eloundou, Felten archives, ~470 MB)
is **git-ignored**. Download instructions are below.

## Reproduction

### 1. Environment

- Python 3.12+ with `pandas`, `numpy`, `scipy`, `openpyxl`
- Pandoc 3.9+ and Typst 0.14+ (for PDF rebuild)

### 2. Raw data sources

| Source | URL | Approx. size |
|---|---|---|
| BLS OEWS 2024 | https://www.bls.gov/oes/special-requests/oesm24all.zip | 77 MB |
| BLS OEWS 2019 | https://www.bls.gov/oes/special-requests/oesm19all.zip | 70 MB |
| O\*NET 30.2 (Excel) | https://www.onetcenter.org/dl_files/database/db_30_2_excel.zip | 46 MB |
| Eloundou et al. (2023) GPT exposure | https://raw.githubusercontent.com/openai/GPTs-are-GPTs/main/data/occ_level.csv | 124 KB |
| Felten et al. (2021) AIOE | https://raw.githubusercontent.com/AIOE-Data/AIOE/main/AIOE_DataAppendix.xlsx | 168 KB |

> ⚠️ **BLS blocks automated retrieval.** Download the BLS archives
> manually from a browser; the other three can be fetched with `curl` or
> `wget`. Place archives under `regression/data/` and extract. The
> scripts expect `regression/data/bls_2024/oesm24all/all_data_M_2024.xlsx`,
> `regression/data/bls_2019/oesm19all/all_data_M_2019.xlsx`,
> `regression/data/onet/db_30_2_excel/`,
> `regression/data/eloundou_occ_level.csv`, and
> `regression/data/felten_aioe.xlsx`.

### 3. Run the pipeline

```bash
cd regression

# Phase A pilot (N=10, sign verification)
python pilot_regression.py

# Phase B (N=707, BLS panel × O*NET)
python phase_b_regression.py
python phase_b_with_control.py

# v1.0 reframe (H_info as primary)
python phase_c_combined.py

# v1.1 IRI construction
python iri_construction.py

# v1.2 + v1.3 robustness (Felten AIOE + Industry FE)
python v12_v13_robustness.py
```

Each script writes a JSON of results next to itself.

### 4. Rebuild the PDF

```bash
pandoc paper.md \
    --citeproc \
    --bibliography=references.bib \
    --pdf-engine=typst \
    -o paper.pdf
```

## Limitations (briefly; full discussion in §9.4 of the paper)

- IRI is a *probabilistic indicator* ($R^2 \approx 0.11$), not a
  deterministic prediction.
- Calibrated on US 2019–2024 panel. International generalisation
  requires re-calibration.
- $H^{\text{info}}$ proxy uses Eloundou α; multicollinearity with the
  GPT-exposure control. v9.6 uses Felten AIOE as an independent proxy
  to mitigate, but full independence requires Autor RTI replication
  (deferred to v2.1).
- The cosmological motivation (§2.3) is genuinely speculative and is
  *explicitly not load-bearing* for the empirical claim.

## Status

- v1.0 (2026-05-11): preprint, hypothesis + initial regression
- **v2.0 (2026-05-11)**: full BLS panel, IRI, multi-source robustness,
  industry FE — current
- v2.1+: Cross-country (OECD/EU LFS) replication, pre-registered
  specification grid

## License

[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).
Replication, critique, re-weighting, and translation are explicitly
welcomed.

## Author

Semin Um (UM, Semin) · Independent Researcher · semini080220@gmail.com
