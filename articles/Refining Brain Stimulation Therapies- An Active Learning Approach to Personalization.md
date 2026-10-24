---
title: "Refining Brain Stimulation Therapies: An Active Learning Approach to Personalization."
doi: "10.21203/rs.3.rs-4876094/v1"
work_id: "W0216"
authors:
  - "Mohammad S E Sendi"
  - "Eric R Cole"
  - "Brigitte Piallat"
  - "Charles A Ellis"
  - "Thomas E Eggers"
  - "Nealen G Laxpati"
  - "Babak Mahmoudi"
  - "Claire-Anne Gutekunst"
  - "Annaelle Devergnas"
  - "Helen Mayberg"
  - "Robert E Gross"
  - "Vince D Calhoun"
year: 2024
journal: "Research square"
peer_reviewed: false
document_type: "preprint"
peer_review_basis: "pubmed: preprint (Research square)"
publication_type: "Journal Article; Preprint"
language: "eng"
keywords: []
identifiers:
  pmid: "39281886"
  pmcid: "PMC11398577"
  arxiv: null
  openalex: null
other_dois:
  - "10.1101/2024.09.02.610880"
abstract_source: "pubmed"
authors_source: "pubmed"
prisma:
  identification:
    search_date: "2026-10-23"
    search_rule: "(optogenet* OR opto-genet* OR optigenet* + non-Latin forms) AND (alzheimer* OR parkinson* + non-Latin forms) in title/abstract/keywords"
    databases:
      - "pubmed"
      - "epmc"
      - "s2"
    n_databases: 3
    source_records:
      - "epmc:PPR:PPR905063"
      - "epmc:PPR:PPR906142"
      - "pubmed:39281886"
      - "pubmed:39282412"
      - "s2:26c2a3e4749c4eeb6a9f69d2a100779423a233b8"
      - "s2:4d58164eee37585889486e24df0df81edc69a452"
    keyword_check: "confirmed"
    duplicates_merged: 5
  screening:
    title_abstract: "pending"
    title_abstract_reason: null
    full_text: "pending"
    full_text_reason: null
    reviewers: []
    notes: ""
  included: null
---

Brain stimulation holds promise for treating brain disorders, but personalizing therapy remains challenging. Effective treatment requires establishing a functional link between stimulation parameters and brain response, yet traditional methods like random sampling (RS) are inefficient and costly. To overcome this, we developed an active learning (AL) framework that identifies optimal relationships between stimulation parameters and brain response with fewer experiments. We validated this framework through three experiments: (1) in silico modeling with synthetic data from a Parkinson's disease model, (2) in silico modeling with real data from a non-human primate, and (3) in vivo modeling with a real-time rat optogenetic stimulation experiment. In each experiment, we compared AL models to RS models, using various query strategies and stimulation parameters (amplitude, frequency, pulse width). AL models consistently outperformed RS models, achieving lower error on unseen test data in silico ( p < 0.0056 , N = 1000 ) and in vivo ( p = 0.0036 , N = 20 ) . This approach represents a significant advancement in brain stimulation, potentially improving both research and clinical applications by making them more efficient and effective. Our findings suggest that AL can substantially reduce the cost and time required for developing personalized brain stimulation therapies, paving the way for more effective and accessible treatments for brain disorders.
