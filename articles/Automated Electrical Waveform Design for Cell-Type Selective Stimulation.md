---
title: "Automated Electrical Waveform Design for Cell-Type Selective Stimulation"
doi: "10.1109/ner52421.2023.10123784"
work_id: "W0254"
authors:
  - "Chaitanya Goswami"
  - "Pulkit Grover"
year: 2023
journal: "International IEEE/EMBS Conference on Neural Engineering"
peer_reviewed: false
document_type: "conference-paper"
peer_review_basis: "openalex-doi: conference-paper"
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
      - "s2:61de6e6737d9626b6d3bb89bd10da4636138d9dd"
    keyword_check: "confirmed"
    duplicates_merged: 0
  screening:
    title_abstract: "pending"
    title_abstract_reason: null
    full_text: "pending"
    full_text_reason: null
    reviewers: []
    notes: ""
  included: null
---

Being able to selectively stimulate a particular neuron type while not activating other neuron types is key to many proposed treatments for several neurological diseases such as Parkinson's disease. Such selective stimulation has been achieved using optogenetic methods but owing to the hurdles present in the use of optogenetics in humans, there has been recent interest in achieving selectivity using more classical techniques such as current stimulation. Often, approaches for designing selective current stimulations are either model-based, thereby limiting their practical applicability, and/or use trial and error, which allows only a limited exploration of the waveform space. In this work, we propose SelStim, a systematic algorithm for designing electrical current waveforms to selectively stimulate different neuron types using only data. SelStim iteratively designs selective current waveforms by adaptively sampling waveforms with an increasing degree of selectivity. The adaptivity allows SelStim to design selective waveforms in a data-efficient manner. Using data obtained on computational neuron models, we show that SelStim designs current waveforms which achieve a high degree of selectivity in stimulating particular neuron types requiring as few as ~200 datapoints. This amounts to a greater than 300% reduction in data requirements compared to a naive brute-force search for achieving similar selectivity.
