---
title: "Closed-loop stimulation of a delayed neural fields model of parkinsonian STN-GPe network: a theoretical and computational study."
doi: "10.3389/fnins.2015.00237"
work_id: "W0697"
authors:
  - "Georgios Is Detorakis"
  - "Antoine Chaillet"
  - "Stéphane Palfi"
  - "Suhan Senova"
year: 2015
journal: "Frontiers in neuroscience"
peer_reviewed: true
document_type: "journal-article"
peer_review_basis: "pubmed: Journal Article"
study_type: "original-research"
publication_type: "Journal Article"
language: "eng"
keywords:
  - "Parkinson’s disease"
  - "optogenetics"
  - "Control theory"
  - "stability analysis"
  - "β-oscillations"
  - "closed-loop deep brain stimulation"
  - "Parkinson's Disease"
  - "Delayed Neural Fields"
  - "subthalamic nucleus"
  - "globus pallidus externus"
  - "closed-loop stimulation"
  - "deep brain stimulation"
  - "beta oscillations"
  - "oscillation suppression"
  - "photosensitization"
  - "neuromodulation"
  - "parameter uncertainty"
identifiers:
  pmid: "26217171"
  pmcid: "PMC4498106"
  arxiv: null
  openalex: "W1598024552"
other_dois: []
abstract_source: "pubmed"
authors_source: "pubmed"
prisma:
  identification:
    search_date: "2026-10-23"
    search_rule: "(optogenet* OR opto-genet* OR optigenet* + non-Latin forms) AND (alzheimer* OR parkinson* + non-Latin forms) in title/abstract/keywords"
    databases:
      - "pubmed"
      - "epmc"
      - "doaj"
      - "openalex"
      - "s2"
    n_databases: 5
    source_records:
      - "doaj:79d06c4289ed47c0a33f50f414254d60"
      - "epmc:MED:26217171"
      - "openalex:W1598024552"
      - "pubmed:26217171"
      - "s2:3047fdd1c82d86fdeb90d9b00104d581ee698aad"
    keyword_check: "confirmed"
    duplicates_merged: 4
  eligibility:
    criteria: "year >= 2020 AND peer_reviewed"
    eligible: false
    reason: "before_min_year"
  screening:
    title_abstract: "pending"
    title_abstract_reason: null
    full_text: "pending"
    full_text_reason: null
    reviewers: []
    notes: ""
  included: null
---

Several disorders are related to pathological brain oscillations. In the case of Parkinson's disease, sustained low-frequency oscillations (especially in the β-band, 13-30 Hz) correlate with motor symptoms. It is still under debate whether these oscillations are the cause of parkinsonian motor symptoms. The development of techniques enabling selective disruption of these β-oscillations could contribute to the understanding of the underlying mechanisms, and could be exploited for treatments. A particularly appealing technique is Deep Brain Stimulation (DBS). With clinical electrical DBS, electrical currents are delivered at high frequency to a region made of potentially heterogeneous neurons (the subthalamic nucleus (STN) in the case of Parkinson's disease). Even more appealing is DBS with optogenetics, which is until now a preclinical method using both gene transfer and deep brain light delivery and enabling neuromodulation at the scale of one given neural network. In this work, we rely on delayed neural fields models of STN and the external Globus Pallidus (GPe) to develop, theoretically validate and test in silico a closed-loop stimulation strategy to disrupt these sustained oscillations with optogenetics. First, we rely on tools from control theory to provide theoretical conditions under which sustained oscillations can be attenuated by a closed-loop stimulation proportional to the measured activity of STN. Second, based on this theoretical framework, we show numerically that the proposed closed-loop stimulation efficiently attenuates sustained oscillations, even in the case when the photosensitization effectively affects only 50% of STN neurons. We also show through simulations that oscillations disruption can be achieved when the same light source is used for the whole STN population. We finally test the robustness of the proposed strategy to possible acquisition and processing delays, as well as parameters uncertainty.
