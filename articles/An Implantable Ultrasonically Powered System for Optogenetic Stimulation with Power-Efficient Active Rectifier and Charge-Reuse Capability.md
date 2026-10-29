---
title: "An Implantable Ultrasonically Powered System for Optogenetic Stimulation with Power-Efficient Active Rectifier and Charge-Reuse Capability."
doi: "10.1109/tbcas.2019.2949154"
work_id: "W0505"
authors:
  - "Amin Rashidi"
  - "Kjeld Laursen"
  - "Seyedsina Hosseini"
  - "Hai-Au Huynh"
  - "Farshad Moradi"
year: 2019
journal: "IEEE transactions on biomedical circuits and systems"
peer_reviewed: true
document_type: "journal-article"
peer_review_basis: "pubmed: Journal Article; Research Support, Non-U.S. Gov't"
study_type: "original-research"
publication_type: "Journal Article; Research Support, Non-U.S. Gov't"
language: "eng"
keywords: []
identifiers:
  pmid: "31647446"
  pmcid: null
  arxiv: null
  openalex: null
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
      - "s2"
    n_databases: 3
    source_records:
      - "epmc:MED:31647446"
      - "pubmed:31647446"
      - "s2:f3714aa9362b17f3a90af7bff5e31a51ac02818a"
    keyword_check: "confirmed"
    duplicates_merged: 2
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

This paper presents a novel micro-scale ultrasonically powered optogenetic microstimulator with the vision of treating Parkinson's Disease. This system features a power-efficient active rectifier benefiting from a novel powering approach for its comparators. The main basis of the idea is to lower the Rail-to-Rail supply voltage of the comparators, thereby lowering their propagation delays. This technique improves the power conversion efficiency of the active rectifiers in two ways. First by decreasing the propagation delay of the comparators, and second by reusing the consumed power by the active diodes. The proposed system including the active rectifier, a novel double-pass regulator, a current reference, and a burst detection circuit is designed, simulated and fabricated in TSMC [Formula: see text]m CMOS technology with a total silicon area of [Formula: see text]. Based on the experimental results, the proposed active rectifier exhibits a voltage conversion ratio of [Formula: see text]% for input voltages of around 3 V, and a power conversion efficiency of up to [Formula: see text]% for a load of [Formula: see text] and over the frequency range of [Formula: see text]. A proof-of-concept system including the fabricated chip, a [Formula: see text]-sized lead zirconate titanate (PZT-4) piezoelectric receiver, and a custom-designed [Formula: see text] blue μ LED is designed and measured in a Water tank. For an acoustic intensity of [Formula: see text], the available electrical power at the crystal terminals, the output DC power, and the output light intensity were measured equal to [Formula: see text], [Formula: see text], and [Formula: see text], respectively. The quiescent current of the chip in absence of power bursts is measured equal to [Formula: see text]A.
