---
title: "Towards the Connectome – Inching Closer Along the Frontiers of Neuroscience"
doi: "10.1093/neuros/nyz032"
work_id: "W0557"
authors:
  - "G. Damian Brusko"
  - "Michael Yufeng Wang"
year: 2019
journal: "Neurosurgery"
peer_reviewed: true
document_type: "journal-article"
peer_review_basis: "openalex-doi: article in Neurosurgery"
study_type: "original-research"
publication_type: "article"
language: "en"
keywords:
  - "human connectome"
  - "connectomics"
  - "compressed sensing"
  - "Caenorhabditis elegans"
  - "locomotion speed"
  - "chemotaxis"
  - "archaerhodopsin-3"
  - "neural activity mapping"
  - "human brain connectivity"
  - "neuroimaging limitations"
  - "consciousness"
  - "neurological disorders"
  - "measurement matrix"
  - "sparse signal recovery"
identifiers:
  pmid: "30892633"
  pmcid: null
  arxiv: null
  openalex: "W2922607718"
other_dois: []
abstract_source: "openalex"
authors_source: "openalex (DOI lookup)"
prisma:
  identification:
    search_date: "2026-10-23"
    search_rule: "(optogenet* OR opto-genet* OR optigenet* + non-Latin forms) AND (alzheimer* OR parkinson* + non-Latin forms) in title/abstract/keywords"
    databases:
      - "openalex"
    n_databases: 1
    source_records:
      - "openalex:W2922607718"
    keyword_check: "confirmed"
    duplicates_merged: 0
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

The completion of the Human Genome Project in 2003 signaled a new era of scientific achievement. A task that decades before seemed near impossible has come to fruition with the refinement of powerful tools capable of analyzing vast amounts of biological data. The importance of the Human Genome Project cannot be understated, as genetic links to diseases and subsequent medical therapies are rapidly becoming a mainstay of modern medicine. Similarly, neuroscientists have recently undertaken a more complex task, one that may provide even greater insight into human development than our own genetic framework. In 2009, the National Institutes of Health (NIH) launched the Human Connectome Project in an ambitious attempt to chart a global connection map of the human brain.1 Neuroscientists have since sought to answer some of neuroscience's toughest questions including how consciousness arises from neurobiological processes and how certain neurological diseases develop. However, the Human Connectome Project is far from complete. Current technology in the field of connectomics is a rate-limiting step at present. Therefore, new techniques are needed to hasten both the discovery of neural circuits and the analysis of key neurons in these pathways. A multi-disciplinary team from Harvard University recently published a paper in Nature Methods that describes a novel framework for identifying neural circuits that regulate locomotor speed in the nematode, Caenorhabditis elegans (commonly C. elegans).2 They applied a statistical technique termed “compressed sensing,” which relies upon 2 principles. First, N groups of neuron subtypes should be stimulated simultaneously, rather than individually, in order to analyze the resultant neural activity. Second, a smaller number of measurements can then be used to find the number n of key neuronal subtypes that drive a specific behavior. In this case, N corresponds to the number of neuronal subtypes involved in the network of C. elegans, with n amount of neurons responsible for movement speed. A total of 27 genetic promoters primarily expressed in interneurons were active in 88 out of 110 total neuron types found in C. elegans. Inputting these values enabled construction of a 27 × 88 dimensional measurement matrix for the compressed sensing analysis. Lines of transgenic C. elegans mutants that expressed archaerhodopsin-3 (Arch) under control of one of the 27 promoters were then created. Chemotaxis speed of the transgenic organisms was measured with exposure to 525 nm (green) light, which inhibited all neurons expressing Arch. The set of 27 locomotor measurements and a complex series of mathematical calculations derived from the measurement matrix determined the degree of individual contributions for each of the 88 neuron types. Next, validation of the compressed sensing analysis employed the use of a stabilization microscope that obtained images of C. elegans freely moving in a restricted environment based upon calcium-triggered changes in neuronal fluorescence. A precise light source targeted single neurons and specifically inhibited its function via Arch. This unique setup allowed for simultaneous monitoring and stimulation of neural activity from groups of neuron subtypes to identify their roles in C. elegans movement speed. Based upon the compressed sensing method, 3 key interneurons with the greatest contributions to locomotion were identified: SIA, RMG, and AVB. A series of targeted illumination tests described above determined that selective inhibition of either SIA, RMG, or AVB each led to significant locomotor speed reductions. In a separate experiment using the same imaging modalities, these 3 interneurons also modulated speed of C. elegans during foraging behavior for food. Furthermore, over 10 additional neuron types that contributed little to locomotion based on compressed sensing were found to have no significant effect on C. elegans speed further supporting the conclusion that SIA, RMG, and AVB play the most important role. Finally, researchers determined the precise affect that each of these interneurons had on movement. SIA appeared to control movement speed changes over the course of minutes and RMG acted over seconds to control pauses in movement. Particularly interesting is that AVB served specifically as a forward control neuron, decreasing its activity as C. elegans moved backward, and increasing activity as the organism transitioned from backward to forward motion. Taken together, the novel application of compressed sensing and the results of this study demonstrate great promise for the growing field of connectomics. Understanding not only the individual neurons that play a role in movement, but also exactly how their activity modulates movement holds the potential for wide-reaching impacts, particularly in neurosurgery. The importance of surgical localization techniques for Deep Brain Stimulation (DBS) including computational modeling3 and oscillations in local field potentials (LFPs)4 has previously been described. Furthermore, datasets from the Human Connectome Project are already being used for in Vivo mapping of connectivity to aid DBS targeting for Parkinson Disease.5 For spinal cord injury, corticospinal tract neuromodulation using trans-spinal direct current stimulation has been shown to significantly improve plasticity and function.6 However, continued improvements in surgical targeting using spinal optogenetics – which is similar to the imaging methods described in the study for C. elegans – may be the key to developing enhanced spinal cord stimulation techniques for the treatment of spinal cord injury7 and chronic pain.8 Future applications of connectomics to neurosurgery will undoubtedly bolster our specialty's place as a field on the forefront of medical innovation. More broadly, as the Human Connectome Project evolves over the coming decades, it will likely impact other fields as well, much like the human genome's influence on our understanding of medicine as a whole. Disclosures Dr Wang receives consulting fees from DePuy-Synthes Spine, K2M, Spineology, Globus, and Stryker, royalties from Children's Hospital of Los Angeles, DePuy-Synthes Spine, Springer Publishing, and Quality Medical Publishing, has grants from the Department of Defense, holds stock in Innovative Surgical Devices, and discloses MAB for Vallum. The authors have no personal, financial, or institutional interest in any of the drugs, materials, or devices described in this article.
