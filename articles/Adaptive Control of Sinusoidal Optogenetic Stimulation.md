---
title: "Adaptive Control of Sinusoidal Optogenetic Stimulation"
doi: "10.1109/ner49283.2021.9441180"
work_id: "W0374"
authors:
  - "Diego M. Vieira"
  - "Antje Kilias"
  - "Moritz Diehl"
  - "Carola A. Haas"
  - "Ulrich Egert"
year: 2021
journal: "International IEEE/EMBS Conference on Neural Engineering"
peer_reviewed: false
document_type: "conference-paper"
peer_review_basis: "openalex-doi: conference-paper"
study_type: "original-research"
publication_type: "JournalArticle; Conference"
language: null
keywords: []
identifiers:
  pmid: null
  pmcid: null
  arxiv: null
  openalex: null
other_dois: []
abstract_source: "s2"
authors_source: "openalex (DOI lookup)"
prisma:
  identification:
    search_date: "2026-10-23"
    search_rule: "(optogenet* OR opto-genet* OR optigenet* + non-Latin forms) AND (alzheimer* OR parkinson* + non-Latin forms) in title/abstract/keywords"
    databases:
      - "s2"
    n_databases: 1
    source_records:
      - "s2:a1a4add1693935c6265c533f0669322a4ce5af7b"
    keyword_check: "confirmed"
    duplicates_merged: 0
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
---

Hippocampal theta oscillations are associated with cognitive functions and their disorder has been linked with pathological conditions, such as temporal lobe epilepsy and Alzheimer's disease. Brief periods of theta-band stimulation have been shown to promote therapeutical effects in neurological disease models. However, an adequate tuning of stimulation intensity is required for longer periods of stimulation, since high amplitudes or strong transients may induce pathological hypersynchronization and seizures. We have developed and implemented an adaptive control strategy to regulate the amplitude of theta-band oscillations induced by sinusoidal optogenetic stimulation. Experimental validation on freely behaving mice showed that adaptive control maintained a stable oscillatory amplitude in the response across changes in brain state and consistently reduced the mean squared error to reference compared to open-loop control. The proposed method may aid in investigating the role and therapeutical benefits of theta oscillations in cognition and neurological disorders.
