---
title: "Robust Neural Stimulation Response Modeling Through Meta-Learning and Pretraining"
doi: "10.48550/arxiv.2608.26649"
work_id: "W0061"
authors:
  - "Matthew J Bryan"
  - "Daniel C Muir"
  - "Felix Schwock"
  - "Azadeh Yazdan-Shahmorad"
  - "Rajesh P N Rao"
year: 2026
journal: "arXiv"
peer_reviewed: false
document_type: "preprint"
peer_review_basis: "openalex-doi: preprint (arXiv (Cornell University))"
study_type: "original-research"
publication_type: "preprint"
language: null
keywords: []
identifiers:
  pmid: null
  pmcid: null
  arxiv: "2608.26649"
  openalex: null
other_dois: []
abstract_source: "arxiv"
authors_source: "arxiv"
prisma:
  identification:
    search_date: "2026-10-23"
    search_rule: "(optogenet* OR opto-genet* OR optigenet* + non-Latin forms) AND (alzheimer* OR parkinson* + non-Latin forms) in title/abstract/keywords"
    databases:
      - "arxiv"
      - "s2"
    n_databases: 2
    source_records:
      - "arxiv:2608.26649"
      - "s2:39619bfbca2f3c5c424381d82644a490a4b7fa75"
    keyword_check: "confirmed"
    duplicates_merged: 1
  eligibility:
    criteria: "year >= 2020 AND peer_reviewed"
    eligible: false
    reason: "not_peer_reviewed"
  screening:
    title_abstract: "pending"
    title_abstract_reason: null
    full_text: "pending"
    full_text_reason: null
    reviewers: []
    notes: ""
  included: null
topico: "T04"
topico_nome: "Estimulação cerebral profunda"
n_termos: 3
tags: ["artigo", "tema/4"]
---
Objective: Model-based closed-loop neural stimulation holds promise for [[grafo/termos/therapeutic applications|therapeutic applications]] ranging from Parkinson's disease to sensory restoration, but deployment has been limited by two obstacles: 1) forecasting models for predicting the consequences of stimulation fail catastrophically on a meaningful fraction of sessions, and 2) per-session calibration requirements are often incompatible with clinical constraints. We address both by demonstrating, for the first time, that meta-learning and pretraining can be applied to neural stimulation response modeling. Methods: Temporal basis function models (TBFMs) forecast state-dependent neural responses to stimulation. We extend TBFMs with cross-session pretraining using a novel architecture and algorithm based on model-agnostic meta-learning (MAML), evaluating them on 40 sessions of optogenetic stimulation in primary sensorimotor cortex of two [[grafo/termos/nonhuman primates|non-human primates]]. Results: Meta-learning substantially reduces catastrophic forecast failure: for a 1k calibration set size, sessions with test R-squared < 0.05 drop from 16 of 40 (single-session training) to 1 (MAML-pretrained), and prediction intervals become significantly narrower (p < 0.05). Calibration requirements are reduced by 50-90% at matched accuracy, enabling experiments otherwise infeasible within clinical session-time constraints. Conclusion: Our results demonstrate that cross-session structure in stimulation responses is consistent enough to support pretraining, providing the first empirical evidence that meta-learning approaches are viable for neural stimulation. Significance: The robustness and sample efficiency gains directly address known obstacles to deploying model-based stimulation controllers. Our results motivate community efforts to assemble standardized multi-site stimulation datasets and to further explore meta-learning for robust [[grafo/termos/closed-loop stimulation|closed-loop stimulation]].

<!-- vinculos:inicio -->
**Tópico:** [[grafo/topicos/T04 Estimulação cerebral profunda|T04 · Estimulação cerebral profunda]]

**Termos (3):** [[grafo/termos/closed-loop stimulation|closed-loop stimulation]] · [[grafo/termos/nonhuman primates|nonhuman primates]] · [[grafo/termos/therapeutic applications|therapeutic applications]]
<!-- vinculos:fim -->
