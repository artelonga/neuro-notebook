---
title: "Adaptive Closed-loop Optical Stimulation Control Based on Dynamic Weighted Spectral Kurtosis for Parkinson's Disease"
doi: "10.1145/3822183.3822243"
work_id: "W0005"
authors:
  - "Yuhao Zhu"
  - "Li Xu"
year: 2026
journal: "Proceedings of the 2026 6th International Conference on Biomedicine and Bioinformatics Engineering"
peer_reviewed: false
document_type: "conference-paper"
peer_review_basis: "openalex-doi: conference-paper"
study_type: "original-research"
publication_type: "Book; Conference"
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
      - "s2:34c8599e22bee2a3eb80c2a8f20afba48c4f2b35"
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
topico: "T04"
topico_nome: "Estimulação cerebral profunda"
n_termos: 8
tags: ["artigo", "tema/4"]
---
Parkinson's disease (PD) is a [[grafo/termos/chronic neurodegenerative|chronic neurodegenerative]] disorder with no cure. Although the emerging optogenetic technology has brought new breakthroughs in precise intervention, its single-modal light regulation cannot simultaneously balance the excitatory and inhibitory balance of [[grafo/termos/neural circuits|neural circuits]], and the traditional open-loop stimulation strategy lacks a real-time feedback mechanism. To address these limitations, this study proposes a dynamic weighted adaptive spectral kurtosis algorithm (DWM-ASK) for nonlinear feature extraction and robust detection of pathological [[grafo/termos/beta oscillations|beta oscillations]]. Different from traditional spectral kurtosis methods, this approach introduces dynamic weighting and adaptive mechanisms, representing a computational improvement. Based on the CTX-BG-TH network model, a closed-loop adaptive control system was constructed through real-time neural signal monitoring. The proposed algorithm enhances pathological burst signals through nonlinear amplification while suppressing background noise, thereby improving detection sensitivity in non-stationary conditions. The single-target [[grafo/termos/light stimulation|light stimulation]] strategies of activating [[grafo/termos/external globus pallidus|GPe]] ([[grafo/termos/channelrhodopsin-2|ChR2]]), inhibiting GPi (NpHR), and their combined dual-target stimulation were systematically evaluated and compared. The combined stimulation mode showed clear advantages. In open-loop testing, it maintained GPi discharge within a narrow physiological range across all parameters, indicating strong robustness. It reduced the GPi inter-spike interval CV from 1.625 to 0.539 (healthy level), restoring firing regularity, and suppressed pathological beta oscillations (13–30 Hz). In [[grafo/termos/closed-loop control|closed-loop control]], it was highly sensitive to β-wave thresholds, enabling rapid, rebound-free β power reduction with the shortest stimulation interval (247.9 ± 52.1 ms), driving the network from pathological resonance to functional stability. Our results show that combined stimulation, via synergistic upstream regulation and downstream blocking, outperforms single-target strategies in inhibition depth, dynamic stability, and desynchronization, providing a key theoretical basis for [[grafo/termos/adaptive dbs|adaptive DBS]] and closed-loop optogenetic systems.

<!-- vinculos:inicio -->
**Tópico:** [[grafo/topicos/T04 Estimulação cerebral profunda|T04 · Estimulação cerebral profunda]]

**Termos (8):** [[grafo/termos/adaptive dbs|adaptive dbs]] · [[grafo/termos/beta oscillations|beta oscillations]] · [[grafo/termos/channelrhodopsin-2|channelrhodopsin-2]] · [[grafo/termos/chronic neurodegenerative|chronic neurodegenerative]] · [[grafo/termos/closed-loop control|closed-loop control]] · [[grafo/termos/external globus pallidus|external globus pallidus]] · [[grafo/termos/light stimulation|light stimulation]] · [[grafo/termos/neural circuits|neural circuits]]
<!-- vinculos:fim -->
