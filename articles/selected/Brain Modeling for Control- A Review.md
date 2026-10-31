---
title: "Brain Modeling for Control: A Review"
doi: "10.3389/fcteg.2022.1046764"
work_id: "W0317"
authors:
  - "Gagan Acharya"
  - "Sebastian F. Ruf"
  - "Erfan Nozari"
year: 2022
journal: "arXiv"
peer_reviewed: true
document_type: "journal-article"
peer_review_basis: "openalex-doi: article in Frontiers in Control Engineering"
study_type: "original-research"
publication_type: "preprint"
language: null
keywords: []
identifiers:
  pmid: null
  pmcid: null
  arxiv: "2210.15957"
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
      - "arxiv:2210.15957"
      - "s2:4efa4cfdd1f5543c9ff93d32d68c622d8f53a8d5"
    keyword_check: "confirmed"
    duplicates_merged: 1
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
n_termos: 8
tags: ["artigo", "tema/4"]
---
[[grafo/termos/neurostimulation|Neurostimulation]] technologies have seen a recent surge in interest from the neuroscience and controls communities alike due to their proven potential to treat conditions such as Parkinson's Disease, and [[grafo/termos/depression|depression]]. The provided stimulation can be of different types, such as electric, and optogenetic, and is generally applied to a specific region of the brain in order to drive the local and/or global dynamics to a desired state of (in)activity. However, an underlying theoretical understanding of the efficacy of neurostimulation is still lacking. From a control-theoretic perspective, it is important to understand how each stimulus modality interacts with the complex [[grafo/termos/brain network|brain network]] in order to assess the controllability of the system and develop neurophysiologically relevant [[grafo/termos/computational model|computational models]] that can be used to design the stimulation profile in a closed-loop manner. In this paper, we review the [[grafo/termos/computational modeling|computational modeling]] studies of (i) [[grafo/termos/deep brain stimulation|deep brain stimulation]], (ii) [[grafo/termos/transcranial magnetic stimulation|transcranial magnetic stimulation]], (iii) direct current stimulation, (iv) transcranial [[grafo/termos/electrical stimulation|electrical stimulation]], and (v) optogenetics as five of the most popular neurostimulation technologies in research and clinical settings. For each technology, we split the reviewed studies into (a)theory-driven biophysical models capturing the low-level physics of the interactions between the stimulation source and neuronal tissue, (b) data-driven stimulus-response models which capture the end-to-end effects of stimulation on various biomarkers of interest and (c) data-driven dynamical system models that extract the precise dynamics of the brain's response to neurostimulation from neural data. While our focus is particularly on the latter category due to their greater utility in control design, we review key works in the former two categories as the basis and context in which dynamical system models have been and will be developed.

<!-- vinculos:inicio -->
**Tópico:** [[grafo/topicos/T04 Estimulação cerebral profunda|T04 · Estimulação cerebral profunda]]

**Termos (8):** [[grafo/termos/brain network|brain network]] · [[grafo/termos/computational model|computational model]] · [[grafo/termos/computational modeling|computational modeling]] · [[grafo/termos/deep brain stimulation|deep brain stimulation]] · [[grafo/termos/depression|depression]] · [[grafo/termos/electrical stimulation|electrical stimulation]] · [[grafo/termos/neurostimulation|neurostimulation]] · [[grafo/termos/transcranial magnetic stimulation|transcranial magnetic stimulation]]
<!-- vinculos:fim -->
