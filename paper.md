---
title: "Informational Task Entropy and the Selection of Occupations Under AI-Driven Substitution"
author:
  - name: Semin Um (UM, Semin)
    affiliation: Independent Researcher
    email: semini080220@gmail.com
date: 2026-05-11
abstract: |
  We propose a thermodynamic-informational reframing of the empirical
  phenomenon of AI-driven labor displacement. Existing models of automation
  exposure (Acemoglu and Restrepo 2020; Eloundou et al. 2023) explain which
  occupations are technically substitutable, but leave residual variation
  in the *speed* of substitution. We hypothesise that occupations
  characterised by **high informational task entropy** --- high
  variability, unpredictability, and non-routinizability of the work
  activities --- are differentially preserved under AI-driven substitution;
  the temporal order of displacement is inversely related to the
  informational entropy of the occupational task profile. The companion
  thermodynamic notion of entropy (human metabolic dissipation rate,
  $E^{\text{thermo}}$) is a noisier secondary measure that is dominated by
  non-AI confounders (COVID-era service-sector contraction, offshoring,
  demographic ageing of the manual workforce). Building on the Maximum
  Entropy Production Principle (Kleidon 2010; Martyushev and Seleznev
  2006), Jeremy England's dissipative-adaptation programme (England 2013,
  2015), and Shannon's informational entropy, we develop the framework,
  propose operational definitions of both entropies, and test the joint
  hypothesis on the full US BLS 2019--2024 occupational panel
  ($N = 707$ detailed national cross-industry SOC codes). The
  informational-entropy specification is strongly confirmed
  ($\hat{\beta}_{H^{\text{info}}} > 0$, $p < 10^{-5}$ in the joint
  specification, $p < 10^{-13}$ once AI exposure is conditioned out).
  The thermodynamic-entropy specification is specification-dependent and
  on its own runs against the prediction. We accordingly classify the
  informational form of H4 as **empirically supported on the BLS panel
  for 2019--2024** and the thermodynamic form as not supported on the
  same data. In v2.1--v2.2 we address the principal critique of v2.0 (mechanical
  co-dependence between the $1-\alpha$ $H^{\text{info}}$ proxy and the
  GPT-exposure control) by reconstructing $H^{\text{info}}$ from
  Autor-Levy-Murnane-style routine task intensities computed from O\*NET
  task profiles *without* any AI-exposure information; the two proxies
  are statistically independent ($r = +0.027$, $p = 0.47$), yet the
  RTI-only specification yields $\hat{\beta} = +9.79 \times 10^{-3}$,
  $t = +3.25$, one-sided $p = 6 \times 10^{-4}$. The H4-info prediction
  therefore survives the strongest available robustness check: an
  AI-content-free task-intensity measure predicts employment growth in
  the predicted direction. We conclude with policy implications for
  redistribution and for the regulation of AI energy consumption.
bibliography: references.bib
---

# 1. Introduction

The displacement of human labor by artificial intelligence is usually framed as
an engineering question: which tasks are technically automatable, and which are
not? Recent assessments [@eloundou2023gpts; @goldmansachs2023] suggest that
approximately 80 % of the United States workforce is exposed to large-language-
model–driven automation, and that some 300 million jobs may be affected
globally. Existing models of automation exposure typically rest on task
decompositions and on AI capability benchmarks [@acemoglu2020robots], and
explain *which* occupations are substitutable. They explain less well the
observed variation in the *speed* with which different occupations are
substituted.

This paper proposes a complementary lens. Rather than asking *what AI can do*,
we ask *what AI does to the entropy budget* of the economic systems in which
it is embedded. Two entropies are relevant. The first is **thermodynamic**:
the rate of metabolic free-energy dissipation per unit working time,
$E^{\text{thermo}}$ (joules per hour). The second is **informational**: the
Shannon entropy of the task profile, $H^{\text{info}}$ (bits, or a normalised
$[0,1]$ proxy), capturing the variability and unpredictability of the work.
Across SOC codes the two are positively correlated ($r \approx 0.40$ in the
BLS sample below) but they are *not* the same construct: a hotel-housekeeping
occupation is high-$E^{\text{thermo}}$ but low-$H^{\text{info}}$ (much
physical labor, little task variability), while a litigation lawyer is
low-$E^{\text{thermo}}$ but high-$H^{\text{info}}$ (sedentary but every case
different).

Our hypothesis (formally stated as **H4** in §3) is that the temporal order
of AI-driven occupational displacement is inversely related to
$H^{\text{info}}_i$, the informational task entropy of occupation $i$. The
parallel thermodynamic statement --- that displacement is inversely related
to $E^{\text{thermo}}_i$ --- is offered as a secondary, weaker version of
the same hypothesis; we test both and find that the data strongly support
the informational form and do not support the thermodynamic form.

The empirical claim of this paper is restricted to a falsifiable
correlation in labor-market data.[^cosmology]

[^cosmology]: Speculative thermodynamic-cosmological proposals (e.g.,
Smolin's Cosmological Natural Selection, @smolin1992did; Crane's
Meduso-anthropic Principle, @crane1994possible) inspired the present
framing during early drafting but do *not* constrain any conclusion
below. We do not endorse or engage with those proposals further. Section 2
sets out the theoretical framework. Section 3 states four nested hypotheses,
of which only the last (H4) is the empirical contribution. Section 4
proposes operational definitions. Section 5 reports the empirical results
on the full BLS 2019--2024 panel. Section 6 illustrates the framework with
a case study. Section 7 surveys existing empirical evidence consistent with
H4. Section 8 discusses limitations and policy implications.

We propose that the temporal order of AI-driven occupational displacement
is inversely related to the informational task entropy of the occupation.
Occupations whose work activities are highly variable and unpredictable
--- emergency physicians, surgeons, skilled chefs, litigators, repair
technicians dealing with novel failures --- tend to be preserved under
MEPP-consistent selection; occupations of low task variability ---
call-center scripts, simple translation, data entry, junior coding ---
are displaced first. This claim is offered as a complement, not a
replacement, for capability-based exposure measures such as
routinisability or GPT-task-coverage. We test it by regressing 2019--2024
BLS occupational employment changes against an informational-entropy
proxy ($H^{\text{info}}_i = 1 - \alpha_i$, where $\alpha_i$ is the
Eloundou et al. direct-LLM-exposure score) and against a parallel
metabolic-entropy proxy ($E^{\text{thermo}}_i$ from O\*NET Work Context
sitting/standing/walking time). The empirical content of the paper rests
on these regressions; the broader thermodynamic framing is heuristic and
not load-bearing.

# 2. Theoretical Framework

## 2.1 The Maximum Entropy Production Principle

In a far-from-equilibrium open system subject to multiple constraints, the
steady state realised is often the one that maximises the rate of entropy
production subject to those constraints [@martyushev2006maximum]. MEPP is
not a fundamental theorem but a heuristic with substantial empirical
support in atmospheric circulation, mantle convection, and ecosystem
dynamics [@kleidon2010nonequilibrium; @lorenz2003reconsidered]. We treat
MEPP throughout as a *selection principle*: among the kinetically
accessible non-equilibrium configurations, those producing more entropy
per unit time tend to be dynamically favoured. The principle is heuristic,
not deductive; we adopt it because the alternative selection principles
(least dissipation, minimum entropy production) have narrower empirical
scope.

## 2.2 Dissipative Adaptation: Life as an Entropy Accelerator

Schrödinger [@schrodinger1944] argued that living systems sustain
themselves by importing free energy and exporting entropy. Prigogine
[@prigogine1977dissipative] generalised this into the theory of
dissipative structures. England's recent work [@england2013statistical;
@england2015dissipative] derives, from non-equilibrium statistical
mechanics, the proposition that under a sufficiently strong external
drive, matter that self-replicates while dissipating rapidly is
statistically favoured over inert matter. Michaelian
[@michaelian2011thermodynamic] extends this argument to the origin of
life itself, identifying primordial photochemistry as a dissipator of
solar UV photons.

Two claims relevant for the present argument follow:

1. Life is, on average, a more efficient dissipator than non-living
   matter at comparable scale and substrate.
2. Selection within the biosphere tends to prefer configurations that
   increase the rate of free-energy throughput, all else equal.

These claims are well-supported in their domains. The contribution of the
present paper is to ask whether the same principle extends to *artificial*
information-processing infrastructures.

## 2.3 Two Entropies for Occupations

A central conceptual move of this paper is to distinguish two senses in
which an occupation can be said to have "high entropy".

**Thermodynamic entropy ($E^{\text{thermo}}_i$).** The rate of metabolic
free-energy dissipation by a human worker performing the duties of
occupation $i$, in joules per hour. This is direct dissipation in the
classical Clausius--Boltzmann sense. High-$E^{\text{thermo}}$ occupations
include skilled trades, hands-on care, food service with substantial
physical activity, and manufacturing roles. Low-$E^{\text{thermo}}$
occupations are sedentary cognitive-symbolic work.

**Informational entropy ($H^{\text{info}}_i$).** The Shannon entropy of
the distribution over tasks, problems, or environments encountered by a
worker performing occupation $i$ during a representative working
interval. High-$H^{\text{info}}$ occupations are those in which each
working hour brings novel problems drawn from a broad action space:
emergency medicine, surgery, skilled litigation, troubleshooting,
investigative journalism, creative writing, complex repair.
Low-$H^{\text{info}}$ occupations are those in which the same tasks
recur with high probability: scripted call-center work, data entry,
repetitive translation, simple clerical processing.

Across SOC codes the two measures are positively correlated ($r \approx
0.40$ in the BLS sample of §5) but the correlation is far from unity.
Counter-examples are common in both directions: hotel housekeepers are
high-$E^{\text{thermo}}$ but low-$H^{\text{info}}$ (each room follows a
similar protocol); litigation lawyers are low-$E^{\text{thermo}}$ but
high-$H^{\text{info}}$ (every case is different). The empirical question
of §5 is which entropy --- if either --- predicts occupational survival
under AI substitution.

## 2.4 The Energy Footprint of Artificial Intelligence

The deployment of large AI systems imposes a substantial and accelerating
energy load. The International Energy Agency [@iea2024electricity]
reports that data centres accounted for approximately 1.0--1.3 % of
global electricity demand in 2022 and projects 3--4 % by 2030. A single
ChatGPT query consumes roughly 2.9 Wh, approximately an order of
magnitude more than a comparable Google search [@devries2023growing].
Training-run estimates for frontier models range from approximately 1
GWh (GPT-3) to tens of GWh (GPT-4) [@patterson2021carbon]. For
comparison, the human brain consumes roughly 20 W. **AI systems are, in
MEPP terms, a new and exceptionally energetic class of dissipator.**
Symbolic-cognitive labor is therefore the natural first target of
substitution, and within that class, the most *predictable* (lowest
$H^{\text{info}}$) tasks are substituted first.

# 3. Hypotheses

We state four nested hypotheses, ordered from most general to most
empirically constrained:

**H1 (Meta-principle).** The macroscopic dynamics of open driven systems
exhibit a tendency toward configurations of higher entropy-production
rate, subject to constraints [MEPP, @kleidon2010nonequilibrium].

**H2 (Biological corollary).** Living systems, on average, produce more
entropy per unit metabolisable resource than abiotic structures of
comparable scale [@england2015dissipative].

**H3 (Technological extension).** The historical trajectory of human
information-processing technology --- pre-industrial labor, mechanised
industry, digital computing, large-scale AI --- has involved monotonic
increases in entropy production per unit symbolic operation.

**H4 (Labor-market prediction --- the empirical contribution).** The
temporal order in which occupations are displaced by AI systems is
partially predicted by the entropy of the occupational task profile.
Specifically, we test two parallel forms:

- **H4-info (primary).** Occupations characterised by *high informational
  task entropy* $H^{\text{info}}_i$ are *differentially preserved* under
  AI-driven substitution; occupations of low informational task entropy
  are differentially displaced.
- **H4-thermo (secondary).** Occupations characterised by *high
  thermodynamic dissipation rate* $E^{\text{thermo}}_i$ are
  *differentially preserved*; occupations of low thermodynamic
  dissipation are differentially displaced.

The mechanistic intuition behind H4-info: in occupations where the
distribution of tasks is broad and difficult to compress, an LLM-class
substitute would have to instantiate exemplars across a high-entropy
distribution to match the human's performance, and the marginal cost of
each additional exemplar grows. In MEPP terms, the AI substitute
captures only the high-probability, low-information "head" of the task
distribution; the human worker retains the long, low-probability "tail".
The mechanistic intuition behind H4-thermo: in occupations where the
human worker is already a high-thermodynamic-entropy dissipator, the
*marginal* entropy gain from AI substitution is small, so MEPP-driven
selection pressure on substitution is weak.

The two forms make the same qualitative prediction (high-entropy
preserved, low-entropy displaced) but they pick out different occupations
as "high-entropy", and §5 shows that the data supports the informational
form considerably more strongly than the thermodynamic form.

H1 and H2 are restatements of established literature. H3 is a synthesis.
H4 is the testable contribution of this paper.

# 4. Operationalisation

## 4.1 Informational task entropy ($H^{\text{info}}_i$)

We construct $H^{\text{info}}_i$ as the complement of the Eloundou et al.
direct-LLM-exposure score $\alpha_i$:

$$
H^{\text{info}}_i = 1 - \alpha_i \in [0, 1].
$$

Eloundou et al. [@eloundou2023gpts] define $\alpha_i$ as the share of
detailed work tasks in occupation $i$ for which "direct exposure" is
sufficient --- i.e., a contemporary GPT-class model alone, without
software augmentation, can perform the task with at least 50 percent time
saving relative to the human. High $\alpha_i$ corresponds to occupations
whose task distribution is *narrow* and *predictable* enough to be
captured by a generative model on its own; low $\alpha_i$ corresponds to
broad, unpredictable task distributions. $1 - \alpha_i$ therefore
provides a normalised proxy for informational task entropy. The data are
the per-SOC scores released with [@eloundou2023gpts] (sample mean 0.87,
SD 0.16, range $[0, 1]$).

## 4.2 Thermodynamic dissipation rate ($E^{\text{thermo}}_i$)

For each occupation, we construct a multi-element Work-Context index from
O\*NET 30.2: the *Spend Time* measures for sitting (negatively weighted),
standing, and walking (each on the 1--5 scale), aggregated to the
BLS-SOC level and mapped linearly to the $[1.5, 5.0]$ MET range, then
converted to J/h via $E^{\text{thermo}}_i = \text{MET}_i \times 70 \times
4184$ joules per hour (assuming a 70 kg body).

## 4.3 Combined index

For sensitivity, we also construct a standardised additive combined
index:

$$
E^{\text{combined}}_i = z(E^{\text{thermo}}_i) + z(H^{\text{info}}_i).
$$

This treats both entropies as equally weighted. Section 5 reports
results separately for the informational, thermodynamic, and combined
specifications and shows that the informational specification
substantially dominates.

# 5. Empirical Results

## 5.1 Specification

We estimate, for each of six specifications, an OLS regression of the
form

$$
\Delta \text{employment}_{i,2019\!-\!2024} = \alpha
+ \boldsymbol{\beta}^{\top} \mathbf{x}_i
+ \boldsymbol{\gamma}^{\top} \mathbf{c}_i
+ \epsilon_i,
$$

where $\Delta \text{employment}_i = (\text{emp}_{i,2024} /
\text{emp}_{i,2019})^{1/5} - 1$ is the annualised five-year employment
growth rate, $\mathbf{x}_i$ is the entropy specification under test (a
one- or two-element subset of $\{E^{\text{thermo}}_i, H^{\text{info}}_i,
E^{\text{combined}}_i\}$), and $\mathbf{c}_i$ is an optional control for
broader AI exposure. The data are the merged $N = 707$ national-level
detailed cross-industry SOC codes for which BLS Occupational Employment
data are available in both 2019 and 2024 [@bls2024oews] and for which
both the Eloundou exposure scores [@eloundou2023gpts] and the O\*NET
Work-Context elements are available.

## 5.2 Results

| Specification                                    | $\hat{\beta}_{E^{\text{thermo}}}$ | $\hat{\beta}_{H^{\text{info}}}$ | $\hat{\beta}_{E^{\text{combined}}}$ | $R^2$  | Verdict on H4               |
|--------------------------------------------------|-----------------------------------|---------------------------------|-------------------------------------|--------|-----------------------------|
| 1. $E^{\text{thermo}}$ only                      | $-2.31\times10^{-8\dagger}$       |                                 |                                     | $0.015$ | H4-thermo *rejected*        |
| **2. $H^{\text{info}}$ only**                    |                                   | $\mathbf{+0.0322^{\ast\ast}}$   |                                     | $0.010$ | **H4-info supported**       |
| 3. $E^{\text{combined}}$ (sum of $z$-scores)     |                                   |                                 | $-0.000364$                         | $0.000$ | combined ns (cancellation)  |
| **4. $E^{\text{thermo}}$ + $H^{\text{info}}$**   | $-3.67\times10^{-8\dagger\dagger}$ | $\mathbf{+0.0567^{\ast\ast\ast}}$ |                                   | $0.041$ | **H4-info supported**       |
| **5. (4) + GPT $\gamma$ control**                | $+1.18\times10^{-8}$ (ns)         | $\mathbf{+0.0775^{\ast\ast\ast}}$ |                                   | $0.089$ | **H4-info strongly supported** |
| 6. (4) + GPT $\beta$ control                     | $+1.18\times10^{-8}$ (ns)         | $\mathbf{+0.1290^{\ast\ast\ast}}$ |                                   | $0.089$ | **H4-info strongly supported** |

Significance: $\dagger\, p < 0.01$ in *opposite* direction; $\dagger\dagger\, p < 10^{-5}$ in *opposite* direction; $^{\ast\ast}\, p < 0.01$; $^{\ast\ast\ast}\, p < 10^{-5}$ in predicted direction. All $p$-values two-sided.

The pattern is striking. The informational form of the hypothesis is
supported in every specification in which it appears (specs 2, 4, 5, 6),
and the strength of the result *increases* monotonically as more
controls are added. The thermodynamic form, by contrast, is rejected in
its bare form (spec 1, 4) and becomes statistically indistinguishable
from zero only after broad AI-exposure is conditioned out (specs 5, 6).
The combined index (spec 3) cancels: the two entropies push the
employment-growth distribution in *opposite* directions in the
unconditional regression, leaving no aggregate effect.

## 5.3 Interpretation

We read these results as identifying the *informational* component of
occupational entropy as the empirically operative variable, with the
thermodynamic component acting as a noise-and-confounder source. The
gross labor-market change in 2019--2024 in high-$E^{\text{thermo}}$
occupations was strongly negative, driven by COVID-era contraction of
the physical service sector, manufacturing offshoring, and demographic
ageing of the manual workforce; these forces are not what H4 was meant
to predict. Conditioning on AI exposure absorbs the
displacement-attributable-to-AI variation, reduces the
$E^{\text{thermo}}$ coefficient to insignificance, and leaves the
informational signal alone, which then emerges still more strongly. The
clean reading is: **AI substitutes against low-informational-entropy
work first, and the thermodynamic-entropy signal that earlier drafts of
this paper relied on is not in fact about AI substitution at all.**

We accordingly classify **H4-info** as **empirically supported on the
US BLS 2019--2024 panel** at conventional significance thresholds, and
**H4-thermo** as **not supported on the same data**.

## 5.4 Phase A pilot regression (historical)

Earlier drafts (v0.1--v0.3) reported a small pilot regression on the ten
illustrative occupations of §7.4. That pilot used $E^{\text{thermo}}_i$
as the predictor and obtained a positive, marginally significant slope
($\hat{\beta} = +1.45 \times 10^{-7}$, one-sided $p = 0.028$,
$N = 10$). The pilot was not an independent test --- the same ten
occupations were used to motivate H4 in §7.4 --- and was itself
selective: the broader BLS panel does not exhibit the monotone pattern
in $E^{\text{thermo}}$ alone that the §7.4 table suggested. We retain
this note for transparency but treat it as superseded by §5.2.

# 6. Illustrative Case Study

We compare four occupations chosen to dissociate the two entropies, with
their BLS-derived annualised employment growth 2019--2024:

| Occupation                        | SOC     | $E^{\text{thermo}}$ (J/h) | $H^{\text{info}}$ ($1-\alpha$) | $\Delta\text{emp}$ p.a. |
|-----------------------------------|---------|----------------------------|--------------------------------|--------------------------|
| Litigation lawyer (proxy: 23-1011)| 23-1011 | low (~5 × 10⁵)            | very high (~0.95)             | $+1.2\%$ (preserved)     |
| Hotel housekeeper                 | 37-2012 | very high (~1.4 × 10⁶)     | low (~0.55)                   | $-2.1\%$ (displaced)     |
| Call-center agent                 | 43-2011 | low (~5 × 10⁵)            | low (~0.30)                   | $-7\%$ (heavily displaced) |
| Emergency physician (29-1217)     | 29-1217 | medium (~8 × 10⁵)          | very high (~0.97)             | $+5\%$ (preserved)       |

The four cells dissociate the two entropies cleanly. Among the
preserved occupations (lawyer, ER physician), what is shared is *high
$H^{\text{info}}$* --- both face genuinely novel problem distributions
each working day --- while $E^{\text{thermo}}$ varies. Among the
displaced occupations (housekeeper, call-center), what is shared is
*low $H^{\text{info}}$* --- both repeat near-identical task scripts ---
while $E^{\text{thermo}}$ ranges from very high to low. Hotel
housekeeping is the *critical* counter-example to H4-thermo: a
high-$E^{\text{thermo}}$ occupation that has been *displaced*, not
preserved. It is consistent with H4-info (low task variability), and
this is the population pattern in §5.

# 7. Existing Evidence (Empirical Patterns Consistent with H4-info)

We summarise five strands of existing evidence consistent with the
informational form of H4. None tests H4 directly --- the regression of
§5 is required for that --- but each is predicted by, and cumulatively
supports, the informational form of the framework.

## 7.1 The routinisability gradient

@autor2003skill introduced the now-canonical distinction between
*routine* and *non-routine* tasks. Routine tasks are precisely those of
*low informational entropy*: their distribution is narrow and
predictable, hence representable by an explicit rule. Non-routine tasks
are of high informational entropy. @autor2003skill and @acemoglu2011skills
document that US occupational employment over 1960--2010 shifted away
from routine tasks toward non-routine. The forty-year routinisability
literature is, on the present view, a long empirical signature of the
$H^{\text{info}}$ gradient that H4-info isolates.

## 7.2 Capability-based exposure measures

@frey2017future estimated 47 % of US employment as "high risk" of
automation; subsequent task-based work [@arntz2016risk] revised this to
~9 %. The framework here explains the gap: occupation-level estimates
aggregate across heterogeneous task mixes, but the *high-entropy* tasks
within an occupation are non-substitutable. Recent AI-specific
measures [@eloundou2023gpts; @brynjolfsson2018what; @felten2018method]
all rank cognitive-symbolic occupations highest in exposure --- which
is to say, lowest in $H^{\text{info}}$.

## 7.3 Direct generative-AI evidence

@noy2023experimental find a 37 % time reduction for mid-skill writing
tasks under ChatGPT use --- a paradigmatic
low-$H^{\text{info}}$ task. @brynjolfsson2023generative find a 14 %
productivity gain for call-center agents using generative-AI assistants
--- the case-study occupation of §6, also low-$H^{\text{info}}$.
Analogous experimental evidence for high-$H^{\text{info}}$ occupations
is scarce, and the absence is informative: those occupations are not
within the present substitution frontier.

## 7.4 BLS 2019--2024 panel

The aggregate BLS panel pattern is reported in §5. Among the 707 SOC
codes, $H^{\text{info}}$ is positively associated with employment growth
in every specification in which AI exposure is conditioned out;
$E^{\text{thermo}}$ is negatively associated with employment growth in
the unconditional specification and indistinguishable from zero
otherwise. The §7.4 table of earlier drafts (v0.1--v0.3) was a selective
illustration; the full panel does not show a monotone pattern in
$E^{\text{thermo}}$ alone, and that table should be read as case
illustration.

## 7.5 Energy-economy linkage

@garrett2014long shows that long-run economic growth correlates tightly
with cumulative energy consumption. This implies that whichever
occupations dominate the economy, their aggregate output is bounded by
their aggregate dissipation. Substitution toward higher-dissipation
production paths is therefore economically as well as thermodynamically
favoured at long horizons --- a mechanism that converts the
informational form of H4 into one that is also *economically* expected,
not merely a heuristic.

## 7.6 Synthesis

No single strand above tests H4-info directly. Their joint pattern,
however, is specific: all five are predicted by H4-info with the correct
sign, including the puzzles (the Frey-Osborne / Arntz et al.
discrepancy) that prior frameworks had to handle as exceptions. The §5
regression converts this consilience into a single quantitative test.

# 8. Discussion

The hypothesis advanced here is consistent with --- and strengthens the
empirical content of --- the dissipative-adaptation programme. Several
consequences follow.

**Theoretical.** AI is not a categorical break from biological
evolution; it is a continuation along the same MEPP-driven trajectory,
with humans serving as the upstream construction substrate. The labor
market becomes a thermodynamic phenomenon as much as an economic one.
The new framing --- that *high-informational-entropy occupations are
differentially preserved* --- provides a parsimonious unifying account
of why physical-but-routine occupations (housekeeping, dishwashing,
basic assembly) are vulnerable while cognitive-but-novel occupations
(litigation, ER medicine, complex repair) are preserved.

**Predictive.** H4-info implies that the AI substitution frontier
advances on the $H^{\text{info}}$ axis, not the $E^{\text{thermo}}$
axis. As the next generation of AI agents handle broader, less
predictable task distributions, the $H^{\text{info}}$ threshold rises:
occupations that were previously preserved by their task variability
will be substituted in order of decreasing variability. We therefore
predict that the next decade's substitution wave will move *into*
moderate-variability cognitive work (paralegals, junior radiologists,
mid-skill diagnostic work) before it reaches truly broad-distribution
work (frontier surgery, primary investigative law).

**Policy.** If displacement order is partially predicted by $H^{\text{info}}$,
redistribution policies --- universal basic income, retraining
programmes --- should be designed against the predicted *order*: the
lowest-$H^{\text{info}}$ occupations first. Retraining a displaced
call-center agent into another low-$H^{\text{info}}$ occupation merely
moves them to the next substitution wave; effective retraining must
move them across the $H^{\text{info}}$ axis, into genuinely novel
problem distributions.

**Limitations.**

(i) MEPP remains a heuristic, not a theorem; counterexamples exist [see
@martyushev2006maximum for review].

(ii) The proximate driver of substitution is cost, not entropy. We
conjecture that cost tracks entropy at long horizons [@garrett2014long]
but do not prove this here.

(iii) Selection effects in BLS occupational data --- reclassification,
gig-economy invisibility, off-shoring --- may bias the regression.
Robustness checks using alternative employment series (CPS, ADP) are
advisable.

(iv) The framework is silent on welfare. A thermodynamically or
informationally favoured outcome is not, on that account, a desirable
outcome.

# 9. An Operational Resilience Index (IRI)

The empirical results of §5 show that informational task entropy is a
quantitative predictor of occupational employment growth. We accordingly
propose an operational composite index --- the **Informational
Resilience Index (IRI)** --- for any occupation $i$, with unit weights
for theoretical neutrality:

$$
\text{IRI}_i = z(H^{\text{info}}_i) + z(\text{JobZone}_i) + z(\log w_i).
$$

The three components are:

- $H^{\text{info}}_i = 1 - \alpha_i$ (informational task entropy proxy,
  via Eloundou et al. direct-LLM-exposure score [@eloundou2023gpts]),
- $\text{JobZone}_i \in \{1, \ldots, 5\}$ (O\*NET Job Zone, encoding
  required preparation as an entry barrier),
- $\log w_i$ (log of the BLS A\_MEDIAN annual wage in 2024
  [@bls2024oews], a proxy for substitution capital cost).

Each component is standardised across the merged sample of $N = 698$
detailed national cross-industry US occupations.

## 9.1 Validation

The composite IRI correlates with annualised 2019--2024 employment
growth at:

- Pearson $r = +0.328$, $p = 5.8 \times 10^{-19}$,
- Spearman $\rho = +0.358$, $p = 1.4 \times 10^{-22}$.

The correlation is more than three times stronger than any single
component in isolation ($r \approx +0.10$ for $H^{\text{info}}$ alone,
§5.2), consistent with each component capturing a distinct dimension of
occupational resilience.

## 9.2 Robustness across weighting schemes

| Weighting           | Pearson $r$ | Notes                                                        |
|---------------------|-------------|--------------------------------------------------------------|
| Unit (1, 1, 1)      | $+0.328$    | Primary specification                                        |
| Regression-fitted   | $+0.331$    | Fitted weights $\approx (0.006, 0.008, 0.009)$ --- effectively equal |
| PCA first component | $+0.296$    | Weights $\approx (-0.13,\, +0.71,\, +0.70)$ --- JobZone and wage drive PC1 |

The unit-weight specification dominates and is recommended as the
headline definition. The regression-fitted specification is essentially
indistinguishable, which is itself informative: the three components
contribute approximately equally on the BLS panel for 2019--2024.

## 9.3 Top and bottom occupations

The ten highest-IRI and ten lowest-IRI occupations in the BLS sample
are reported below. The full $N = 698$ table is published as a
companion Zenodo dataset (CC-BY 4.0).

**Top 10 (most resilient under AI substitution):**

| SOC     | Occupation                                | $H^{\text{info}}$ | JobZone | Wage (USD) | IRI    |
|---------|-------------------------------------------|-------------------|---------|------------|--------|
| 29-1215 | Family Medicine Physicians                | $1.00$            | $5$     | $238{,}380$ | $+6.03$ |
| 29-1216 | General Internal Medicine Physicians      | $1.00$            | $5$     | $236{,}350$ | $+6.00$ |
| 29-1151 | Nurse Anesthetists                        | $1.00$            | $5$     | $223{,}210$ | $+5.86$ |
| 29-1221 | Pediatricians, General                    | $1.00$            | $5$     | $210{,}130$ | $+5.71$ |
| 23-1023 | Judges, Magistrate Judges, and Magistrates | $1.00$           | $5$     | $156{,}210$ | $+4.97$ |
| 29-1081 | Podiatrists                               | $1.00$            | $5$     | $152{,}800$ | $+4.91$ |
| 29-1021 | Dentists, General                         | $0.95$            | $5$     | $172{,}790$ | $+4.90$ |
| 23-1011 | Lawyers                                   | $1.00$            | $5$     | $151{,}160$ | $+4.88$ |
| 11-1011 | Chief Executives                          | $0.87$            | $5$     | $206{,}420$ | $+4.81$ |
| 29-1041 | Optometrists                              | $1.00$            | $5$     | $134{,}830$ | $+4.60$ |

**Bottom 10 (most exposed under AI substitution):**

| SOC     | Occupation                                          | $H^{\text{info}}$ | JobZone | Wage (USD) | IRI    |
|---------|-----------------------------------------------------|-------------------|---------|------------|--------|
| 43-4021 | Correspondence Clerks                               | $0.04$            | $2$     | $46{,}740$  | $-7.00$ |
| 43-9021 | Data Entry Keyers                                   | $0.14$            | $2$     | $39{,}850$  | $-6.71$ |
| 43-2021 | Telephone Operators                                 | $0.16$            | $2$     | $39{,}130$  | $-6.66$ |
| 31-9094 | Medical Transcriptionists                           | $0.18$            | $3$     | $37{,}550$  | $-5.72$ |
| 41-9041 | Telemarketers                                       | $0.39$            | $2$     | $34{,}410$  | $-5.49$ |
| 43-4071 | File Clerks                                         | $0.32$            | $2$     | $41{,}270$  | $-5.46$ |
| 43-9022 | Word Processors and Typists                         | $0.30$            | $2$     | $47{,}850$  | $-5.26$ |
| 43-9041 | Insurance Claims and Policy Processing Clerks        | $0.33$            | $2$     | $48{,}450$  | $-4.99$ |
| 43-9081 | Proofreaders and Copy Markers                       | $0.05$            | $4$     | $49{,}210$  | $-4.95$ |
| 27-3092 | Court Reporters and Simultaneous Captioners          | $0.08$            | $3$     | $67{,}310$  | $-4.86$ |

The lists are intuitively reasonable: high-IRI occupations are dominated
by clinical-medical and senior-legal roles (high information entropy +
high entry barrier + high wage), while low-IRI occupations are
dominated by routine clerical and low-variability transcription roles.

## 9.4 Caveats and limits

(i) IRI is a *probabilistic indicator*, not a deterministic prediction.
The current $R^{2} \approx 0.11$ implies that $\sim 89\%$ of
inter-occupation variation in employment change is *not* captured by
IRI and must be attributed to industry shocks, demographic effects,
capital cost, and other forces outside this paper.

(ii) IRI uses 2024 BLS wages and 2023 Eloundou exposure scores; the
score is calibrated to a specific point in time. As AI capability
advances, the $H^{\text{info}}$ frontier rises and an occupation's IRI
must be re-estimated.

(iii) IRI does not measure individual-worker resilience within an
occupation. A worker in a low-IRI occupation may be highly resilient
through specialisation, while a worker in a high-IRI occupation may be
displaced by personal supply-side shocks.

(iv) IRI is calibrated on US data only. International generalisation
requires re-calibration with country-specific exposure and wage data.

(v) The $H^{\text{info}}$ proxy and the $\alpha$-based GPT-exposure
control are derived from the same Eloundou data. A v1.2 robustness
check should replace $H^{\text{info}}$ with an Autor-RTI based measure
(an entirely different research programme) to break this mechanical
relationship.

## 9.5 Open data and code

The full IRI score table for the $N = 698$ US national-detailed
cross-industry SOC codes, together with the underlying components and
the construction code, is published as a companion Zenodo dataset
(CC-BY 4.0, computer-readable CSV). We invite replication, critique,
and re-weighting; we do *not* claim IRI as the unique correct
operationalisation of H4-info, only as a transparent first attempt.

## 9.6 Tautology break (v2.1): RTI as AI-independent $H^{\text{info}}$ proxy

The principal weakness of v2.0 (correctly identified in informal review)
was that $H^{\text{info}}_i = 1 - \alpha_i$ uses Eloundou et al.'s
direct-LLM-exposure score $\alpha_i$, which is itself an
AI-substitutability measure. Demonstrating that "occupations of low
$\alpha$ shrink slowly" using $1 - \alpha$ as a predictor risks
mechanical co-dependence with any AI-exposure control. To break this
co-dependence, v2.1 reconstructs an alternative $H^{\text{info}}$
proxy from Autor-Levy-Murnane-style routine/non-routine task
intensities, computed entirely from O\*NET 30.2 importance ratings of
fifteen non-AI-derived work-activity elements grouped into the
canonical five categories [@autor2003skill; @acemoglu2011skills]:

$$
\text{RTI}_i = \tfrac{1}{2}\bigl[z(\text{R}^{\text{cog}}_i) + z(\text{R}^{\text{man}}_i)\bigr]
- \tfrac{1}{3}\bigl[z(\text{NR}^{\text{anal}}_i) + z(\text{NR}^{\text{int}}_i) + z(\text{NR}^{\text{man}}_i)\bigr],
$$

with $H^{\text{info}}_{\text{RTI},i} = -\text{RTI}_i$ (higher value = more
non-routine = more informational task entropy).

The component categories use the following O\*NET Work Activities
elements (Importance scale, IM):

- Routine cognitive: 4.A.2.a.3, 4.A.4.c.1, 4.A.3.b.6.
- Routine manual: 4.A.3.a.3, 4.A.3.a.2, 4.A.3.a.1.
- Non-routine analytic: 4.A.2.a.4, 4.A.2.b.2, 4.A.2.b.4.
- Non-routine interactive: 4.A.4.a.4, 4.A.4.b.4, 4.A.4.b.5.
- Non-routine manual: 4.A.3.a.4, 4.A.3.b.4, 4.A.3.b.5.

**Critical finding.** The Pearson correlation between
$H^{\text{info}}_{\text{RTI}}$ and the original
$H^{\text{info}}_{\text{Eloundou}} = 1 - \alpha$ is

$$
r = +0.027 \quad (p = 0.47, N = 707).
$$

The two proxies are statistically *independent*. The RTI proxy uses
*no* AI-exposure information; it is constructed entirely from
occupation task profiles. Yet the labour-market regression on RTI
alone yields

$$
\hat{\beta}_{H^{\text{info}}_{\text{RTI}}} = +9.79 \times 10^{-3},
\quad t = +3.25, \quad p_{\text{one}} = 6.0 \times 10^{-4}.
$$

The H4-info prediction therefore survives the tautology check: an
$H^{\text{info}}$ proxy that has *zero AI content* still predicts
employment growth in the H4-direction.

A horse-race specification including both $H^{\text{info}}_{\text{RTI}}$
and $H^{\text{info}}_{\text{Eloundou}}$ keeps both significant
(RTI: $t = +3.19$; Eloundou: $t = +2.62$), with the RTI loading slightly
larger. Each proxy carries information the other lacks.

**IRI v2.** Replacing $H^{\text{info}}_{\text{Eloundou}}$ with
$H^{\text{info}}_{\text{RTI}}$ in the IRI definition (§9 main equation)
gives a fully AI-free composite index:

$$
\text{IRI}_{2,i} = z(H^{\text{info}}_{\text{RTI},i})
+ z(\text{JobZone}_i) + z(\log w_i).
$$

The IRI v2 score correlates with subsequent annualised employment
growth at $r = +0.275$ ($p = 1.3 \times 10^{-13}$, Spearman $\rho =
+0.322$, $p = 3.0 \times 10^{-18}$, $N = 698$). The cross-correlation
between IRI v2 and the original IRI v1 is $r = +0.834$, indicating that
the two indices order occupations similarly even though they share no
direct AI-exposure component. The IRI v2 top-10 occupations are Chief
Executives, Marketing Managers, Mathematicians, Sales Managers,
Economics/Engineering Teachers, Political Scientists, Astronomers,
Economists, and Financial Managers; the bottom-10 are Food Cooking
Machine Operators, Reservation Clerks, Veterinary Assistants, Couriers,
Orderlies, Machine Feeders, Cleaning-Equipment Operators, Medical
Equipment Preparers, Data Entry Keyers, and Foundry Workers. The
extreme cells of the AI-free IRI v2 are intuitively reasonable and
match the AI-derived IRI v1 in spirit.

The full IRI v2 score table for the same $N = 698$ occupations is
published as a v2 dataset alongside the v1 IRI dataset; replication and
re-weighting are explicitly invited.

## 9.7 Multi-source robustness (v1.2): Felten AIOE as alternative proxy

The headline IRI uses the Eloundou et al. $\alpha_i$ score
[@eloundou2023gpts] as the $H^{\text{info}}$ proxy. Because the same
exposure data also drives the controls in §5.2 specs 2a--2c, mechanical
co-dependence is possible. We accordingly construct an alternative
proxy from a fully independent research programme: Felten, Raj, and
Seamans [@felten2018method; @felten2021occupational] AI Occupational
Exposure (AIOE), which derives from a different methodology --- linking
advances in AI capabilities to O\*NET occupational abilities, rather
than rating LLM substitutability directly. We define $H^{\text{info}}_{\text{alt}, i}
= -\text{AIOE}_i$ so that higher values indicate lower AI exposure (higher
informational entropy).

The two proxies correlate at $r = +0.41$ ($p < 10^{-26}$) across
$N = 655$ SOC codes. The correlation is substantial but far from
perfect: the two research programmes capture overlapping but distinct
dimensions of AI exposure. Rebuilding IRI with the Felten-based proxy
yields a Pearson correlation with employment growth of $r = +0.258$
($p = 2.2 \times 10^{-11}$, Spearman $\rho = +0.280$), somewhat weaker
than the Eloundou-based version ($r = +0.327$). A joint OLS that
includes both standardised proxies, JobZone, and log wage retains a
positive significant Eloundou loading and a small but significant
*negative* Felten loading, indicating that the two have not collapsed
onto each other and each carries some information beyond the other. The
H4-info prediction therefore survives a robustness check using an
entirely different exposure-measurement programme.

## 9.8 Industry-level fixed effects (v1.3)

The aggregate regression in §5.2 pools across industries. Industry-level
shocks --- e.g., COVID-era contraction of hospitality versus the
expansion of healthcare --- may confound the H4-info signal. We
therefore re-estimate

$$
\Delta\text{employment}_i = \alpha
+ \beta \cdot \text{IRI}_i
+ \sum_{k} \gamma_k \cdot \mathbf{1}[\text{NAICS2}_i = k]
+ \epsilon_i,
$$

using the dominant industry of each occupation derived from BLS 2024
industry-level employment data and 2-digit NAICS codes. The sample is
$N = 653$ occupations spanning approximately 20 distinct 2-digit NAICS
classes.

Industry fixed effects *alone* explain $R^2 = 0.143$ of the
cross-occupational variation in employment growth. Adding IRI raises
$R^2$ to $0.220$ --- an increment of $\Delta R^2 = +0.077$ attributable
to IRI *after* industry effects are absorbed. The IRI coefficient is

$$
\hat{\beta}_{\text{IRI}} = +7.39 \times 10^{-3}
\quad (\text{SE } 9.41 \times 10^{-4}),
\quad t = +7.86, \quad p = 1.7 \times 10^{-14}.
$$

The H4-info signal is therefore not an industry-composition artefact:
it persists at very high statistical significance after industry fixed
effects, and contributes a non-trivial fraction of explained variation
on top of the industry effects themselves.

## 9.9 E^{thermo} robustness (v2.1): multi-element strength index

A complementary critique of v2.0 was that the $E^{\text{thermo}}_i$
proxy used only "spend time" body-position elements (sitting, standing,
walking) and may have been too noisy to give H4-thermo a fair test.
v2.1 reconstructs $E^{\text{thermo}}_{2,i}$ from a richer multi-element
basket: the original sitting (negative), standing, walking elements
plus climbing, kneeling, bending, repetitive motions (Work Context),
and Work Activities elements 4.A.3.a.1 (Performing General Physical
Activities, Importance) and 4.A.3.a.2 (Handling and Moving Objects,
Importance). All standardised; signs reflect the direction of metabolic
contribution.

The univariate regression on the enriched proxy yields

$$
\hat{\beta}_{E^{\text{thermo}}_2} = -9.26 \times 10^{-4},
\quad t = -3.78, \quad p = 1.7 \times 10^{-4}.
$$

The sign is *still negative*, in the *opposite* direction from H4-thermo.
The v2.1 enrichment therefore confirms the v2.0 finding that
H4-thermo is not supported on the BLS 2019--2024 panel; the failure is
not a measurement artefact.

## 9.10 Cross-country and causal identification (deferred)

A natural extension is to replicate the IRI--employment relationship on
OECD or EU labor-market panels. The principal obstacle is the
SOC--ISCO classification mapping: ISCO-08 1-digit groupings (10
categories) are too coarse for occupation-level regression, while
detailed-level cross-walks introduce substantial aggregation noise. A
preliminary attempt to assemble an OECD/Eurostat panel comparable to
the BLS 2019--2024 series at the detailed-occupation level was
unsuccessful within the scope of v2.0. Cross-country replication, with
a defensible SOC--ISCO bridge, remains the central task of v2.2+.

A second extension, attempted in v2.3, is *causal identification*
through state-level variation in AI adoption. We assemble a state ×
occupation panel from BLS OEWS state-level releases ($N = 27{,}356$
state-occupation cells, 51 states, $\sim 700$ occupations) and
estimate

$$
\Delta\text{emp}_{i,s} = \alpha + \beta_1 H^{\text{info}}_{\text{RTI},i}
+ \beta_2 \text{tech}^{\text{share}}_s
+ \beta_3 (H^{\text{info}}_{\text{RTI},i} \times \text{tech}^{\text{share}}_s)
+ \mu_i + \nu_s + \epsilon_{i,s},
$$

where $\text{tech}^{\text{share}}_s$ is the 2019 share of state-$s$
employment in Computer & Mathematical occupations (SOC 15-1xxx +
15-2xxx), $\mu_i$ is an occupation fixed effect, and $\nu_s$ is a
state fixed effect. The DiD coefficient $\beta_3$ tests whether the
H4-info effect is *stronger* in tech-intensive states, as we would
expect if the H_info-employment relationship is genuinely
AI-mediated.

The empirical result on the within-transformed (two-way FE)
specification is $\hat{\beta}_3 = +1.40 \times 10^{-3}$ ($t = +0.53$,
two-sided $p = 0.59$, one-sided $p = 0.30$). The sign matches the
H4-info prediction but the effect is not statistically significant at
conventional thresholds. Robustness with $H^{\text{info}}_{\text{Eloundou}}$
yields the same qualitative pattern ($\hat{\beta}_3 = +1.91 \times 10^{-3}$,
$p_{\text{one}} = 0.23$).

The most defensible interpretation is that AI diffusion across US
states between 2019 and 2024 has been *too uniform* to leave a
detectable state-level moderation in BLS occupational employment, and
that tech-occupation share is at best a noisy proxy for actual
AI-tool adoption. The state-level DiD therefore neither strengthens
nor weakens the H4-info claim established at the occupation level: it
identifies a null state-by-state moderation effect, which is consistent
with rapid and uniform diffusion of generative-AI tools through the
US labor market post-2022.

Cross-country generalisation against an ISCO-08-based panel and a more
defensible state-level AI-adoption instrument (e.g., NAICS-51
information-sector employment share, state-level AI patent density,
firm-level GenAI adoption surveys) remain the central tasks for v2.4+.

# 10. Conclusion

This is v2.3. We have argued that the *informational task entropy* of
an occupation, $H^{\text{info}}$, provides a partial but novel
predictor of the occupation's temporal robustness against AI-driven
substitution. The informational form is empirically supported on the
US BLS 2019--2024 panel under multiple operationalisations.

The most defensible result, added in v2.1 (§9.6), uses an
$H^{\text{info}}$ proxy reconstructed from Autor-Levy-Murnane-style
routine task intensities (RTI) computed from O\*NET task profiles
*without* any AI-exposure information. The Pearson correlation between
this AI-independent RTI proxy and the original $1 - \alpha$ proxy is
only $r = +0.027$ ($p = 0.47$): they are statistically independent.
The RTI-only regression yields $\hat{\beta}_{H^{\text{info}}_{\text{RTI}}}
= +9.79 \times 10^{-3}$, $t = +3.25$, one-sided $p = 6.0 \times 10^{-4}$.
The H4-info prediction therefore survives the strongest possible
robustness check: an entirely AI-content-free task-intensity measure
predicts employment growth in the predicted direction on the same
panel. This rules out the tautology objection that the v2.0 result
merely re-labels a known AI-exposure pattern.

The thermodynamic form (H4-thermo) is not supported on the same data
and is dominated by non-AI confounders. v2.1 enriches the
$E^{\text{thermo}}$ proxy with strength, climbing, kneeling, bending,
and repetitive-motion elements (§9.9); the negative-sign result
persists ($\hat{\beta} = -9.3 \times 10^{-4}$, $p = 1.7 \times 10^{-4}$),
ruling out the alternative that H4-thermo failed only because of a
crude proxy.

Earlier-version checks remain in place: the prediction also persists
under the Felten et al. AIOE alternative proxy ($r = +0.258$,
$p < 10^{-10}$, §9.7) and under 2-digit NAICS industry fixed effects
($\hat{\beta}_{\text{IRI}}$ at $t = +7.86$, $p = 1.7 \times 10^{-14}$,
with IRI contributing $\Delta R^2 = +0.077$ on top of industry effects,
§9.8). The policy implication is that redistribution and retraining
programmes should be designed against the *informational* order of
substitution: lowest-variability occupations first, then
mid-variability, with high-variability occupations slowest to
substitute. The high energy footprint of AI is, under MEPP, the feature
that selects the technology rather than a bug to be optimised away;
but the *targeting* of that selection on the labour side is
informational, not metabolic.

A state-level DiD attempted in v2.3 (§9.10) yields a sign-correct but
non-significant interaction ($\hat{\beta}_{\text{DiD}} = +1.4 \times
10^{-3}$, one-sided $p = 0.30$), most plausibly because AI diffusion
across US states between 2019 and 2024 has been too uniform to leave a
detectable state-level moderation. Cross-country replication against
an ISCO-08-based panel, and stronger state-level AI-adoption
instruments (NAICS-51 share, AI patent density), remain the principal
items of remaining work for v2.4+.

# References

(Compiled from `references.bib` via `pandoc --citeproc`.)
