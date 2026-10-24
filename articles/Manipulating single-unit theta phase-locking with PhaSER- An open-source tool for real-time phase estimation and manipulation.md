---
title: "Manipulating single-unit theta phase-locking with PhaSER: An open-source tool for real-time phase estimation and manipulation."
doi: "10.1101/2023.02.21.529420"
work_id: "W0270"
authors:
  - "Zoé Christenson Wick"
  - "Paul A Philipsberg"
  - "Sophia I Lamsifer"
  - "Cassidy Kohler"
  - "Elizabeth Katanov"
  - "Yu Feng"
  - "Corin Humphrey"
  - "Tristan Shuman"
year: 2023
journal: "bioRxiv : the preprint server for biology"
peer_reviewed: false
document_type: "preprint"
peer_review_basis: "pubmed: preprint (bioRxiv : the preprint server for biology)"
publication_type: "Preprint; Journal Article"
language: "eng"
keywords: []
identifiers:
  pmid: "36865324"
  pmcid: "PMC9980125"
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
      - "epmc:PPR:PPR619911"
      - "pubmed:36865324"
      - "s2:99a59318e2fec01c7a212b3757d4642dfa6ae478"
    keyword_check: "confirmed"
    duplicates_merged: 2
  screening:
    title_abstract: "pending"
    title_abstract_reason: null
    full_text: "pending"
    full_text_reason: null
    reviewers: []
    notes: ""
  included: null
---

The precise timing of neuronal spiking relative to the brain's endogenous oscillations (i.e., phase-locking or spike-phase coupling) has long been hypothesized to coordinate cognitive processes and maintain excitatory-inhibitory homeostasis. Indeed, disruptions in theta phase-locking have been described in models of neurological diseases with associated cognitive deficits and seizures, such as Alzheimer's disease, temporal lobe epilepsy, and autism spectrum disorders. However, due to technical limitations, determining if phase-locking causally contributes to these disease phenotypes has not been possible until recently. To fill this gap and allow for the flexible manipulation of single-unit phase-locking to on-going endogenous oscillations, we developed PhaSER, an open-source tool that allows for phase-specific manipulations. PhaSER can deliver optogenetic stimulation at defined phases of theta in order to shift the preferred firing phase of neurons relative to theta in real-time. Here, we describe and validate this tool in a subpopulation of inhibitory neurons that express somatostatin (SOM) in the CA1 and dentate gyrus (DG) regions of the dorsal hippocampus. We show that PhaSER is able to accurately deliver a photo-manipulation that activates opsin+ SOM neurons at specified phases of theta in real-time in awake, behaving mice. Further, we show that this manipulation is sufficient to alter the preferred firing phase of opsin+ SOM neurons without altering the referenced theta power or phase. All software and hardware requirements to implement real-time phase manipulations during behavior are available online (https://github.com/ShumanLab/PhaSER).
