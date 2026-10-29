---
title: "Abnormal activity in the brainstem affects gait in a neuromusculoskeletal model."
doi: "10.1186/s12984-025-01596-x"
work_id: "W0085"
authors:
  - "Daisuke Ichimura"
  - "Makoto Sawada"
  - "Kenji Wada"
  - "Ritsuko Hanajima"
year: 2025
journal: "Journal of neuroengineering and rehabilitation"
peer_reviewed: true
document_type: "journal-article"
peer_review_basis: "pubmed: Journal Article; Research Support, Non-U.S. Gov't"
study_type: "original-research"
publication_type: "Journal Article; Research Support, Non-U.S. Gov't"
language: "eng"
keywords:
  - "Brainstem"
  - "Parkinson’s Disease"
  - "Central Pattern Generator"
  - "Freezing Of Gait"
  - "Neuromusculoskeletal Model"
  - "Midbrain Locomotor Region"
  - "Pathological Locomotion"
identifiers:
  pmid: "40186175"
  pmcid: "PMC11969973"
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
      - "epmc:MED:40186175"
      - "pubmed:40186175"
      - "s2:4a3ab5c1798825d345f5b60021a32429be2b2d39"
    keyword_check: "confirmed"
    duplicates_merged: 2
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
---

BACKGROUND: The ability to start and stop locomotion in response to different situations is an essential survival strategy in mammals. Mammalian locomotion is controlled by central pattern generators in the spinal cord, which are modulated by higher centers, particularly by the stimulation of the midbrain locomotor region. The midbrain locomotor region consists of the pedunculopontine nucleus and cuneiform nucleus, each having different roles in animals. Optogenetic activation of the cuneiform nucleus increases locomotion activities, whereas that of pedunculopontine nucleus decreases them. In neurological disorders such as Parkinson's disease, patients exhibit disturbed locomotion controls, including freezing of gait, which is defined as "a brief, episodic absence or marked reduction in the forward progression of the feet despite the intention to walk." However, the details and pathophysiological mechanisms of freezing of gait remain unclear. METHODS: In this study, we aimed to elucidate the mechanisms underlying freezing of gait using a two-dimensional neuromusculoskeletal model fixed on the sagittal plane. This model consisted of a body with seven links and 18 muscles as well as a neural system including the brainstem and spinal cord. We developed a normal condition model and then derived a model of abnormal brainstem activity by modifying the parameters of the pedunculopontine nucleus and cuneiform nucleus during the initial 3 s of walking. RESULTS: The normal models walked successfully following internal parameter optimization using standard genetic algorithms. In an abnormal model, 156 freezing of gait events were detected among 40,000 parameter sets using a freezing of gait-identifying algorithm. Hierarchical cluster analysis identified four clusters of parameters, based on the intensities of the pedunculopontine nucleus and cuneiform nucleus activity, differentiated in physiological movement types during freezing of gait events that were similar to the clinical classification types of freezing of gait. CONCLUSIONS: Our results indicate that pedunculopontine nucleus and cuneiform nucleus activities could be linked with freezing of gait and that different modifications of those activities could generate observed freezing of gait subtypes. Our models can provide insights relevant for understanding the pathophysiological mechanisms of freezing of gait and are expected to assist in the classification of freezing of gait subtypes.
