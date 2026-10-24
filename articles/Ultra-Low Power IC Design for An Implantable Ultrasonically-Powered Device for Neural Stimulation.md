---
title: "Ultra-Low Power IC Design for An Implantable Ultrasonically-Powered Device for Neural Stimulation"
doi: null
work_id: "W0434"
authors: []
year: 2021
journal: null
peer_reviewed: false
document_type: "other"
peer_review_basis: "openalex: other"
publication_type: "other"
language: "en"
keywords:
  - "biomedical implants"
  - "deep brain stimulation"
  - "Parkinson's disease"
  - "optogenetics"
  - "neurostimulation"
  - "neural recording"
  - "power management unit"
  - "energy harvesting"
  - "brain-computer interface"
  - "neuromodulation"
  - "drug delivery"
  - "beamforming"
  - "subthalamic nucleus"
  - "globus pallidus internus"
identifiers:
  pmid: null
  pmcid: null
  arxiv: null
  openalex: "W4412321071"
other_dois: []
abstract_source: "openalex"
authors_source: null
prisma:
  identification:
    search_date: "2026-10-23"
    search_rule: "(optogenet* OR opto-genet* OR optigenet* + non-Latin forms) AND (alzheimer* OR parkinson* + non-Latin forms) in title/abstract/keywords"
    databases:
      - "openalex"
    n_databases: 1
    source_records:
      - "openalex:W4412321071"
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

Parkinson's Disease (PD) is the second most common neurodegenerative disease after Alzheimer affecting millions of people worldwide. Nevertheless, the available pharmacological treatments (e.g. Levodopa) for PD have shown low long-term efficacy and side-effects due to not-localized drug release. Deep brain stimulation (DBS) systems are rather more successful for PD treatment. DBS systems try to compensate for the lost brain neural paths due to PD, by delivering precisely-controlled electrical stimuli to the target neurons in the subthalamic nucleus (STN) or internal globus pallidus (GPi). However, available commercial DBS systems mainly require large batteries implanted in the patient’s chest, long micro-electrode arrays implanted deep in the brain, and subcutaneous interconnects from the battery to the electrodes. Thus, a limited lifetime of batteries and increasing the risk of loose-connection of subcutaneous interconnects may force the patient to undergo several surgeries. Furthermore, electrical stimulation has a low spatial resolution that can lead to the inability to selective exciting of neurons and consequently undesirable side-effects. Finally, tolerable electromagnetic exposure can get limited by long conducting electrodes. This thesis aims to address the aforementioned challenges using ultrasonically powered micro-scale devices that can harvest energy in deep regions of the brain (e.g. STN), selectively stimulated the target neurons through optogenetics, communicate the associated recorded neural activity, and release drugs locally at the target tissue. In the recent decade, ultrasonically powered implants usually referred to as dusts, motes, or seeds due to their micro-scale dimensions, have received special attention from researchers within different fields. For deeply seated implants, ultrasonic powering offers three main advantages over other counterparts (i.e. near field and RF powering): (a) Higher Food and Drug Administration (FDA)-approved exposable power to the body (7.2mW/mm2); (b) lower attenuation through the tissue phantom; and (c) mm-scale wavelength of the ultrasonic in the body allows for high-precision beam-forming. As a result, ultrasonic powering is used in a variety of applications including neural recording, neuromodulation (optical or electrical stimulation), pressure measurement, temperature sensing, Imaging, etc. However such devices still encounter some substantial challenges which are partly addressed in this thesis with both system-level and circuit-level ideas. Available electrical power at micro-scale ultrasonic harvesters suitable for brain implants is limited, making it challenging for power-demanding applications such as optogenetics. Thus, in this thesis a high chip-efficiency using an energy-efficient power management unit is targeted . To this end, a power-efficient active rectifier with current-reuse capability is proposed for generating the DC supply voltage need for optogenetics out of the AC signal available at the dust. Accordingly, an integrated electronic die is designed and fabricated in TSMC 180-nm technology. Then, a proof-of-concept system including the fabricated chip, a $560 \times 560 \times 490 \mu m^3$-sized lead zirconate titanate (PZT-4) piezoelectric receiver, and a custom-designed $280 \times 180 \times 100 \mu m^3$ blue $\mu$LED is designed and measured successfully in a Water tank. Accordingly, chip efficiencies as high as 94\% is measured. In the next steps, a new overvoltage regulator and a fully-analog time to current converter are proposed and successfully simulated in transistor level, to avoid overvoltage breakdown and programmable optogenetics, respectively. Another challenge is the limited bandwidth of ultrasonic links due to the rather small wavelength of ultrasound inside the body and low-frequency power carrier. In this thesis, an analog method for modulation of the ultrasonic backscattered signals is proposed that allows for exploiting the full bandwidth of the ultrasonic link. Furthermore, a low-complexity time-conversion approach is proposed to up-modulate the low-bandwidth recorded neural signal (i.e. local field potentials) to frequencies proportional to the link bandwidth. Accordingly, the theory behind the proposed approach is presented and the associated circuits are simulated in transistor level. Finally, a multi-load regulation technique is proposed in order to regulate the total electrical load of a dust and consequently suppress the need for adaptive matching circuits, and overvoltage protection circuit. Based on the proposed technique, a novel wireless dual-color optogenetic system, capable of simultaneous neural excitation and inhibition is proposed. The electronic die for this system is designed and fabricated in TSMC 180-nm technology, and the proof-of-concept system is measured successfully in a Water tank. The measurements show Maximum chip and system efficiencies of 92.5\% and 31.5\%, respectively.
