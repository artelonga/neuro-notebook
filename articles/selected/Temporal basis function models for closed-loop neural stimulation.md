---
title: "Temporal basis function models for closed-loop neural stimulation."
doi: "10.1088/1741-2552/ae036a"
work_id: "W0149"
authors:
  - "Matthew J Bryan"
  - "Felix Schwock"
  - "Azadeh Yazdan-Shahmorad"
  - "Rajesh P N Rao"
year: 2025
journal: "Journal of neural engineering"
peer_reviewed: true
document_type: "journal-article"
peer_review_basis: "pubmed: Journal Article"
study_type: "original-research"
publication_type: "Journal Article"
language: "eng"
keywords:
  - "AI"
  - "Machine Learning"
  - "Neurostimulation"
  - "Optogenetics"
  - "Brain–computer Interface"
  - "Computational Models"
  - "Brain Co-processor"
identifiers:
  pmid: "40907530"
  pmcid: null
  arxiv: "2507.15274"
  openalex: null
other_dois:
  - "10.48550/arxiv.2507.15274"
abstract_source: "pubmed"
authors_source: "pubmed"
prisma:
  identification:
    search_date: "2026-10-23"
    search_rule: "(optogenet* OR opto-genet* OR optigenet* + non-Latin forms) AND (alzheimer* OR parkinson* + non-Latin forms) in title/abstract/keywords"
    databases:
      - "pubmed"
      - "epmc"
      - "arxiv"
      - "s2"
    n_databases: 4
    source_records:
      - "arxiv:2507.15274"
      - "epmc:MED:40907530"
      - "pubmed:40907530"
      - "s2:fb351ee515a8743571b8d7df18e55778ef76c411"
    keyword_check: "confirmed"
    duplicates_merged: 3
  eligibility:
    criteria: "year >= 2020 AND peer_reviewed"
    eligible: true
    reason: null
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
n_termos: 5
tags: ["artigo", "tema/4"]
---
Objective.Closed-loop neural stimulation provides novel therapies for neurological diseases such as Parkinson's disease (PD), but it is not yet clear whether [[grafo/termos/artificial intelligence|artificial intelligence]] (AI) techniques can tailor [[grafo/termos/closed-loop stimulation|closed-loop stimulation]] to individual patients or identify new therapies. Further advancements are required to address a number of difficulties with translating AI to this domain, including sample efficiency, training time, and minimizing loop latency such that stimulation may be shaped in response to changing [[grafo/termos/brain activity|brain activity]].Approach.We propose temporal basis function models (TBFMs) to address these difficulties, and explore this approach in the context of excitatory optogenetic stimulation. We demonstrate the ability of TBF models to provide a single-trial, spatiotemporal forward prediction of the effect of optogenetic stimulation on [[grafo/termos/local field potentials|local field potentials]] measured in two [[grafo/termos/nonhuman primates|non-human primates]]. The simplicity of TBF models allow them to be sample efficient (<20 min of training data), rapid to train (<5 min), and low latency (<0.2 ms) on desktop CPUs.Main results.We demonstrate the model on 40 sessions of previously published excitatory optogenetic stimulation data. Surprisingly, on test sets it achieved a prediction accuracy 44% higher than a complex nonlinear dynamical systems model that requires hours to train, and 158% higher than a linear state-space model requiring 90 min to train. Additionally, in two simulations we show that it successfully allows a closed-loop stimulator to drive neural trajectories, and to achieve the user-preferred trade-offs between under- and over-stimulation, given the uncertainty in the model; it achieves an area under curve of ∼0.7 in both cases.Significance.By optimizing for sample efficiency, training time, and latency, our approach begins to bridge the gap between complex AI-based approaches to modeling dynamical systems and the vision of using such forward prediction models to develop novel, clinically useful closed-loop stimulation protocols.

<!-- vinculos:inicio -->
**Tópico:** [[grafo/topicos/T04 Estimulação cerebral profunda|T04 · Estimulação cerebral profunda]]

**Termos (5):** [[grafo/termos/artificial intelligence|artificial intelligence]] · [[grafo/termos/brain activity|brain activity]] · [[grafo/termos/closed-loop stimulation|closed-loop stimulation]] · [[grafo/termos/local field potentials|local field potentials]] · [[grafo/termos/nonhuman primates|nonhuman primates]]
<!-- vinculos:fim -->
