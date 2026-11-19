# References — 300-molecule dataset

The [dataset index](index.csv) lists all 300 molecules. The [provenance table](references.tsv) records the sources of each 2D drawing and 3D reference, its database identifier, and the corresponding reference numbers from this bibliography.

## Where each part of the set comes from

| source | entries | 3D coordinates | 2D picture | references |
|---|---|---|---|---|
| VSEPR, organic (tier A) | 1 | PubChem 3D conformer [1] | drawn from the xyz | [1] |
| VSEPR, main group from COD (15 tier B + 2 tier-C trigonal pyramidal: Tl, In) | 17 | molecule or fragment cut from a COD crystal structure [3], [4] | drawn from the xyz | [3], [4]; primary papers [50–63] |
| VSEPR, transition metal (tier C) | 41 | tmQM geometry of a CSD entry [6], [5] | drawn from the xyz | [6], [5]; primary papers [64–104] |
| natural products | 70 | PubChem 3D conformer (61) or PubChemQC-PM6 conformer (9) [1], [2] | SynArchive target drawing [7] | [1], [2], [7] |
| paper (SI coordinates) | 12 | SI of the cited paper | drawn from the xyz | ME_12 [10] ×5, ME_14 [11] ×7 |
| screenshot (published figure) | 58 | SI / data set of the cited paper | crop of the published figure | ME_03 [8] ×10, ME_09 [9] ×10, ME_19 [12] ×2, DU8 [13] ×5, MOR41 [14] ×9, ROST61 [15] ×22 |
| screenshot, organometallic (published figure) | 101 | SI of the cited paper | crop of the published figure, curated in organometallic_xyz2d | 31 papers [17–47] |
| **total** | **300** | | | |

Descriptors (`descriptors.tsv`): spacial score [48], computed with RDKit [49].

## Databases and data sets

1. Kim, S.; Chen, J.; Cheng, T.; Gindulyte, A.; He, J.; He, S.; Li, Q.; Shoemaker, B. A.; Thiessen, P. A.; Yu, B.; Zaslavsky, L.; Zhang, J.; Bolton, E. E. PubChem 2025 update. *Nucleic Acids Res.* **2025**, *53*, D1516–D1525. https://doi.org/10.1093/nar/gkae1059
2. Nakata, M.; Shimazaki, T.; Hashimoto, M.; Maeda, T. PubChemQC PM6: Data Sets of 221 Million Molecules with Optimized Molecular Geometries and Electronic Properties. *J. Chem. Inf. Model.* **2020**, *60*, 5891–5899. https://doi.org/10.1021/acs.jcim.0c00740
3. Gražulis, S.; Chateigner, D.; Downs, R. T.; Yokochi, A. F. T.; Quirós, M.; Lutterotti, L.; Manakova, E.; Butkus, J.; Moeck, P.; Le Bail, A. Crystallography Open Database – an open-access collection of crystal structures. *J. Appl. Crystallogr.* **2009**, *42*, 726–729. https://doi.org/10.1107/s0021889809016690
4. Gražulis, S.; Daškevič, A.; Merkys, A.; Chateigner, D.; Lutterotti, L.; Quirós, M.; Serebryanaya, N. R.; Moeck, P.; Downs, R. T.; Le Bail, A. Crystallography Open Database (COD): an open-access collection of crystal structures and platform for world-wide collaboration. *Nucleic Acids Res.* **2012**, *40*, D420–D427. https://doi.org/10.1093/nar/gkr900
5. Groom, C. R.; Bruno, I. J.; Lightfoot, M. P.; Ward, S. C. The Cambridge Structural Database. *Acta Crystallogr., Sect. B* **2016**, *72*, 171–179. https://doi.org/10.1107/s2052520616003954
6. Balcells, D.; Skjelstad, B. B. tmQM Dataset—Quantum Geometries and Properties of 86k Transition Metal Complexes. *J. Chem. Inf. Model.* **2020**, *60*, 6135–6146. https://doi.org/10.1021/acs.jcim.0c01041
7. SynArchive — The Synthesis Archive, browse syntheses by molecule name. https://synarchive.com/molecule (accessed Sep 24, 2026)

## Source papers for the paper and screenshot entries

8. Zhang, S.-Q.; Taylor, B. L. H.; Ji, C.-L.; Gao, Y.; Harris, M. R.; Hanna, L. E.; Jarvo, E. R.; Houk, K. N.; Hong, X. Mechanism and Origins of Ligand-Controlled Stereoselectivity of Ni-Catalyzed Suzuki–Miyaura Coupling with Benzylic Esters: A Computational Study. *J. Am. Chem. Soc.* **2017**, *139*, 12994–13005. https://doi.org/10.1021/jacs.7b04973
9. Anderson, T. E.; Thamattoor, D. M.; Phillips, D. L. Probing the alkylidene carbene–strained alkyne equilibrium in polycyclic systems via the Fritsch–Buttenberg–Wiechell rearrangement. *Nat. Commun.* **2024**, *15*, 8313. https://doi.org/10.1038/s41467-024-52390-7
10. Siedschlag, R. B.; Bernales, V.; Vogiatzis, K. D.; Planas, N.; Clouston, L. J.; Bill, E.; Gagliardi, L.; Lu, C. C. Catalytic Silylation of Dinitrogen with a Dicobalt Complex. *J. Am. Chem. Soc.* **2015**, *137*, 4638–4641. https://doi.org/10.1021/jacs.5b01445
11. Wang, J.; Feng, A.; Zhang, D. DFT Investigation of a Nonclassical Oxidative Addition-Reductive Elimination Pathway in the Pd(0)/Pd(II)/Pd(0) Cycle for Dual Hydroamination of Cycloheptatriene to Tropene. *J. Org. Chem.* **2025**, *90*, 11132–11141. https://doi.org/10.1021/acs.joc.5c01033
12. Paterson, A. J.; Dunås, P.; Rahm, M.; Norrby, P.-O.; Kociok-Köhn, G.; Lewis, S. E.; Kann, N. Palladium Catalyzed Stereoselective Arylation of Biocatalytically Derived Cyclic 1,3-Dienes: Chirality Transfer via a Heck-Type Mechanism. *Org. Lett.* **2020**, *22*, 2464–2469. https://doi.org/10.1021/acs.orglett.0c00708
13. Novitskiy, I. M.; Kutateladze, A. G. DU8+ Computations Reveal a Common Challenge in the Structure Assignment of Natural Products Containing a Carboxylic Anhydride Moiety. *J. Org. Chem.* **2021**, *86*, 17511–17515. https://doi.org/10.1021/acs.joc.1c02291
14. Dohm, S.; Hansen, A.; Steinmetz, M.; Grimme, S.; Checinski, M. P. Comprehensive Thermochemical Benchmark Set of Realistic Closed-Shell Metal Organic Reactions. *J. Chem. Theory Comput.* **2018**, *14*, 2596–2608. https://doi.org/10.1021/acs.jctc.7b01183
15. Maurer, L. R.; Bursch, M.; Grimme, S.; Hansen, A. Assessing Density Functional Theory for Chemically Relevant Open-Shell Transition Metal Reactions. *J. Chem. Theory Comput.* **2021**, *17*, 6134–6151. https://doi.org/10.1021/acs.jctc.1c00659
16. grimme-lab. benchmark-MOR41 (structures `MOR41/<name>/mol.xyz`). GitHub repository. https://github.com/grimme-lab/benchmark-MOR41
17. Zhou, Z.; Babson, A. J.; Wei, Z.; Petrukhina, M. A. Construction of Bimetallic and Trimetallic Aggregates with a [Y(COT)2]− Building Block: Solid-State Structures and Solution Behavior. *Organometallics* **2025**, *44*, 2092–2098. https://doi.org/10.1021/acs.organomet.5c00233
18. Feresin, J.; Ford, M. C.; Vascura, M. K.; Moore, C. E.; Barrett, S. M.; Thomas, C. M. Coordination-Induced Weakening of N–H Bonds Driven by Bimetallic Cooperativity in Zr/Co Compounds. *Inorg. Chem.* **2026**, *65*, 3115–3124. https://doi.org/10.1021/acs.inorgchem.5c05652
19. Jayasundara, R.; Kulathungage, L. W.; Baillie, B. J.; Ward, C. L.; Lord, R. L.; Groysman, S. The Effect of a Single Trifluoromethyl Substituent on the Reactivity of Chelating C2 and Cs-Symmetric Bis(alkoxide) Ligands on a Terphenyl Platform. *Inorg. Chem.* **2026**, *65*, 2110–2116. https://doi.org/10.1021/acs.inorgchem.5c05470
20. Button-Jennings, D.; Schley, N. D.; Hanusa, T. P. Sterically Stabilized Homoleptic Copper and Gold Allyl Complexes. *Organometallics* **2026**, *45*, 552–562. https://doi.org/10.1021/acs.organomet.5c00460
21. Stephan, J.; Bühler, R.; Napoli, F. E.; Gemel, C.; Fischer, R. A. Cooperative Reactivity Induced by All-Gallium Coordination at Nickel. *Inorg. Chem.* **2025**, *64*, 15707–15714. https://doi.org/10.1021/acs.inorgchem.5c02296
22. Sledesky, J. M.; Zimmerman, J. H.; London, H. C.; Lambert, E. C.; McMillen, C. D.; Barker, M.; Hanson, K.; Wagenknecht, P. S. Xylylethynyl Titanocene with a Microsecond Emission Lifetime Photosensitizes Singlet-Oxygen Formation and Photon Upconversion. *Inorg. Chem.* **2025**, *64*, 14977–14988. https://doi.org/10.1021/acs.inorgchem.5c01773
23. Sittel, S.; Naumann, R.; Förster, C.; Huber, M. E.; Meyer, J.; Heinze, K. Thermally Activated and Nonactivated Excited State Decay of [Cr(dgpy)2]3+. *Inorg. Chem.* **2025**, *64*, 20404–20414. https://doi.org/10.1021/acs.inorgchem.5c03668
24. Bajo, S.; Fernández-Buenestado, M.; López-Serrano, J.; Campos, J. Flash Communication: Strained and Bimetallic Structures of Rhodium and Iridium Germyl Complexes with Phosphinoamido Ligands. *Organometallics* **2025**, *44*, 2729–2732. https://doi.org/10.1021/acs.organomet.5c00403
25. Yang, W.; White, A. J. P.; Crimmin, M. R. Reactions of a Zn–Zn bond with main group carbene analogues as a prototypical case of reductive addition. *Nat. Synth.* **2025**, *4*, 995–1000. https://doi.org/10.1038/s44160-025-00790-y
26. Nieto-Vargas, I.; Cayuela-Castillo, J.; Fernández-de-Córdova, F. J.; Fernández, I.; Ríos, P. Haptotropic Phenomena in Digold(I) Triple-Bonded Complexes. *Inorg. Chem.* **2026**, *65*, 7153–7160. https://doi.org/10.1021/acs.inorgchem.5c04642
27. Morganti, M.; Kruse, J. C.; Gupta, S. K.; Dechert, S.; Demeshko, S.; Meyer, F. Redox and Spin States Series of an Organometallic Heme Analogue Based on a Non-Innocent NHC/N-Donor Hybrid Macrocycle. *Inorg. Chem.* **2026**, *65*, 2184–2202. https://doi.org/10.1021/acs.inorgchem.5c04599
28. Melnikov, S.; Multem, A. J. H.; Oostenbrug, P. N.; Lutz, M.; Broere, D. L. J. Metal–Ligand Cooperative Nitrile Activation Triggered by a Catalytic Amount of Weak Base. *Organometallics* **2026**, *45*, 2095–2103. https://doi.org/10.1021/acs.organomet.6c00104
29. Shiels, D.; Berlfein, A. C.; Peluzo, B. M. T. C.; Lopez, L. M.; Mitchell, A. W.; Brennessel, W. W.; Zeller, M.; Crawley, M. R.; Bart, S. C.; Ruggiero, M. T.; Matson, E. M. Probing the Framework Metal Dependent Properties of Actinide-Centered Polyoxoalkoxide Sandwich-Type Complexes. *Inorg. Chem.* **2025**, *64*, 9180–9194. https://doi.org/10.1021/acs.inorgchem.5c00780
30. Padilla, M.; Batuecas, M.; García-Orduña, P.; Oro, L. A.; Fernández-Álvarez, F. J. Triflate-Enabled Rhodium-Catalyzed Cross-Dehydrogenative Si–N Bond Formation from Hydrosiloxanes. *Inorg. Chem.* **2026**, *65*, 16283–16295. https://doi.org/10.1021/acs.inorgchem.6c01798
31. Gross, P.; Choi, H.; Pullara, W. A.; Im, H.; Ung, K.; Kang, S.; Baik, M.-H.; Blakey, S. B. Enantioselective Olefin 1,2-Arylamination Catalyzed by a Planar Chiral Indenyl-Rhodium(III) Complex. *ACS Catal.* **2026**, *16*, 3453–3463. https://doi.org/10.1021/acscatal.5c07589
32. Pita-Milleiro, A.; Landrini, M.; Navarro, M.; Moreno, J. J.; Guzmán, J.; Maya, C.; Campos, J. Bulky Terphenyl Phosphines Stabilize Otherwise Highly Reactive Iridium Fragments, Key in C–H Activation Reactions. *Inorg. Chem.* **2026**, *65*, 16869–16878. https://doi.org/10.1021/acs.inorgchem.6c01943
33. Ferrer-Bru, C.; Ferrer, J.; Passarelli, V.; Lahoz, F. J.; García-Orduña, P.; Carmona, D. Diverse and Selective Metal–Ligand Cooperative Routes for Activating Non-Functionalized Ketones. *Inorg. Chem.* **2025**, *64*, 2188–2206. https://doi.org/10.1021/acs.inorgchem.4c03214
34. García-Vega, S.; Pérez-Carreño, E.; Cabeza, J. A.; García-Álvarez, P. Pyridylalkenolato-Stabilized Heavier Tetrylenes: Air-Stability Studies and Preliminary Coordination Chemistry. *Inorg. Chem.* **2026**, *65*, 11592–11605. https://doi.org/10.1021/acs.inorgchem.5c05924
35. Webber, C. K.; Alférez, M. G.; Bastani, F.; Kumawat, J.; Kong, F.; Gehman, Z. M.; Ou, X.; Dickie, D. A.; Ess, D. H.; Reinke, P.; Gunnoe, T. B. Synthesis and Characterization of a Copper Complex Supported by a Z-type SbV Ligand: XPS and DFT Study of Electronic Structure. *Organometallics* **2026**, *45*, 438–448. https://doi.org/10.1021/acs.organomet.5c00420
36. Walsh, A. M.; Martín-Fernández, C.; Lowe, J. P.; Macgregor, S. A.; Mahon, M. F.; Whittlesey, M. K. Cationic and Neutral Heterometallic Ir-Group 12 Element Polyhydride Compounds: Synthesis, Structure and Reactivity. *Inorg. Chem.* **2026**, *65*, 1162–1171. https://doi.org/10.1021/acs.inorgchem.5c04368
37. Murray, A. J.; Wales, L. L.; Dietz, M.; Poland, E. M.; McManus, C.; Crumpton, A. E.; Struijs, J. J. C.; Aldridge, S. Homo- and Heteroleptic Silylstannylenes: Synthesis, Structure and Use as Precursors to Bimetallic Compounds. *Organometallics* **2026**, *45*, 828–836. https://doi.org/10.1021/acs.organomet.6c00001
38. Poater, A. Versatile deprotonated NHC: C,N-bridged dinuclear iridium and rhodium complexes. *Beilstein J. Org. Chem.* **2016**, *12*, 117–124. https://doi.org/10.3762/bjoc.12.13
39. Díaz-Jiménez, À.; Monreal-Corona, R.; Saha, A.; Álvarez-Núñez, A.; Company, A.; Parella, T.; Pérez, P. J.; Caballero, A.; Roglans, A.; Poater, A.; Pla-Quintana, A. Characterization of a Silver Vinylcarbene Intermediate in Carbene–Alkyne Metathesis and Its Concerted C(sp2)–H Bond Insertion. *J. Am. Chem. Soc.* **2026**, *148*, 3689–3696. https://doi.org/10.1021/jacs.5c19806
40. Benzan Lantigua, P. A.; Lutz, M.; Moret, M.-E. Synthesis, Characterization, and Catalytic Activity of Gold Complexes Bearing Bicyclic Silicon and Germanium Anionic Ligands. *Organometallics* **2025**, *44*, 2287–2294. https://doi.org/10.1021/acs.organomet.5c00299
41. Figueira, C. A.; Lopes, P. S.; Meyrelles, R.; Gomes, C. S. B.; Gomes, J. C. S.; Veiros, L. F.; Gomes, P. T. Unexpected Formation of Neutral Alkyl-Ni(II) Complexes Bearing Unsymmetrical C,N,N’-Pincer Iminopyrrolyl Ligands via Intramolecular C–H Bond Activation: A Distinct Type of Single-Component Ethylene Polymerization Catalysts. *Inorg. Chem.* **2025**, *64*, 24479–24496. https://doi.org/10.1021/acs.inorgchem.5c03794
42. Pagliaricci, N.; Pettinari, R.; Marchetti, F.; Pagliaricci, S.; Cuccioloni, M.; Eleuteri, A. M.; Galindo, A.; Fadaei-Tirani, F.; Glinkina, K.; Dyson, P. J. Half-Sandwich Ruthenium and Osmium Complexes with Hydrazinocurcuminoid-like Ligands. *Organometallics* **2025**, *44*, 1155–1164. https://doi.org/10.1021/acs.organomet.5c00082
43. Siano, P.; Diment, L. A.; Siela, D. J.; Ericson, M. N.; McGraw, M.; Song, B. C.; Livaudais, B. F.; Simpson, S. R.; Dickie, D. A.; Harman, W. D. Transition-Metal-Based Dearomatization Strategy for the Synthesis of Functionalized cis-Tetrahydro-2-Oxindoles. *Organometallics* **2025**, *44*, 2570–2578. https://doi.org/10.1021/acs.organomet.5c00371
44. Morello, M.; Dall’Anese, A.; Rocchigiani, L.; Ehm, C.; Cipullo, R.; Kulyabin, P. S.; Uborsky, D. V.; Voskoboynikov, A. Z.; Macchioni, A.; Busico, V.; Zuccaccia, C. Ligand-Assisted Formation of Heterobimetallic Adducts of AlMe3 and ZnMe2 with Zr and Hf Salan Catalysts for Olefin Polymerization. *Inorg. Chem.* **2025**, *64*, 23947–23960. https://doi.org/10.1021/acs.inorgchem.5c03732
45. Seith, M. C.; Fitzsimmons, M. C.; Muhammad, H. A.; Nieto, C. A.; Moore, C. E.; Lewis, L. C.; Thomas, C. M. Synthesis and Characterization of a Series of (PPR P)Co Complexes and Comparison of their Electronic Properties and Catalytic Activities. *Organometallics* **2026**, *45*, 1554–1570. https://doi.org/10.1021/acs.organomet.6c00131
46. Bermejo, J.; Santos, L. L.; Álvarez, E.; López-Serrano, J.; Suárez, A. Oxidation of Alcohols to Carboxylates with N2 O Catalyzed by Ruthenium(II)-CNC Complexes. *ACS Catal.* **2025**, *15*, 11530–11543. https://doi.org/10.1021/acscatal.5c02021
47. Isaac, C. J.; Miloserdov, F. M.; Pécharman, A.-F.; Lowe, J. P.; McMullin, C. L.; Whittlesey, M. K. Structure and Reactivity of [Ru–Al] and [Ru–Sn] Heterobimetallic PPh3-Based Complexes. *Organometallics* **2022**, *41*, 2716–2730. https://doi.org/10.1021/acs.organomet.2c00344

## Descriptor method and software

48. Krzyzanowski, A.; Pahl, A.; Grigalunas, M.; Waldmann, H. Spacial Score─A Comprehensive Topological Indicator for Small-Molecule Complexity. *J. Med. Chem.* **2023**, *66*, 12739–12750. https://doi.org/10.1021/acs.jmedchem.3c00689
49. RDKit: Open-Source Cheminformatics Software. https://www.rdkit.org

## Primary publications of the COD crystal structures (main-group VSEPR entries)

50. Husebye, S.; Törnroos, K. W.; Zhu, H. Chlorotris(N,N′-dicyclohexylthiourea-S)tellurium(II) chloride, a tellurium complex with a TeClS3coordination sphere. *Acta Crystallogr., Sect. C* **2001**, *57*, 854–856. https://doi.org/10.1107/s010827010100659x — COD 2012107
51. Akiba, K.-y.; Nadano, R.; Satoh, W.; Yamamoto, Y.; Nagase, S.; Ou, Z.; Tan, X.; Kadish, K. M. Synthesis, Structure, Electrochemistry, and Spectroelectrochemistry of Hypervalent Phosphorus(V) Octaethylporphyrins and Theoretical Analysis of the Nature of the PO Bond in P(OEP)(CH2CH3)(O). *Inorg. Chem.* **2001**, *40*, 5553–5567. https://doi.org/10.1021/ic010595e — COD 4320436
52. Yurkerwich, K.; Buccella, D.; Melnick, J. G.; Parkin, G. Monovalent indium in a sulfur-rich coordination environment: synthesis, structure and reactivity of tris(2-mercapto-1-tert-butylimidazolyl)hydroborato indium, [TmBut]In. *Chem. Commun.* **2008**, 3305. https://doi.org/10.1039/b803037e — COD 7103222
53. Dohi, T.; Takenaga, N.; Fukushima, K.-i.; Uchiyama, T.; Kato, D.; Motoo, S.; Fujioka, H.; Kita, Y. Designer μ-oxo-bridged hypervalent iodine(iii) organocatalysts for greener oxidations. *Chem. Commun.* **2010**, *46*, 7697. https://doi.org/10.1039/c0cc03213a — COD 7112903
54. Rong, Y.; Palmer, J. H.; Parkin, G. Benzannulated tris(2-mercapto-1-imidazolyl)hydroborato ligands: tetradentate κ 4 -S 3 H binding and access to monomeric monovalent thallium in an [S 3 ] coordination environment. *Dalton Trans.* **2014**, *43*, 1397–1407. https://doi.org/10.1039/c3dt52418c — COD 7028634
55. Prasad, P.; Singh, H.; Butcher, R. Synthesis, Structure and Antioxidant Activity of Cyclohexene-Fused Selenuranes and Related Derivatives. *Molecules* **2015**, *20*, 12670–12685. https://doi.org/10.3390/molecules200712670 — COD 1529356
56. Hill, E. A.; Kelty, M. L.; Filatov, A. S.; Anderson, J. S. Isolable iodosylarene and iodoxyarene adducts of Co and their O-atom transfer and C–H activation reactivity. *Chem. Sci.* **2018**, *9*, 4493–4499. https://doi.org/10.1039/c8sc01167b — COD 1549283
57. Hartmann, D.; Schädler, M.; Greb, L. Bis(catecholato)silanes: assessing, rationalizing and increasing silicon's Lewis superacidity. *Chem. Sci.* **2019**, *10*, 7379–7388. https://doi.org/10.1039/c9sc02167a — COD 1551460; COD 1551467
58. Hokamp, T.; Wirth, T. Structurally Defined α-Tetralol-Based Chiral Hypervalent Iodine Reagents. *J. Org. Chem.* **2019**, *84*, 8674–8682. https://doi.org/10.1021/acs.joc.9b01315 — COD 4034108
59. Kadu, R.; Batabyal, M.; Kadyan, H.; Koner, A. L.; Kumar, S. An efficient copper-catalyzed synthesis of symmetrical bis(N -arylbenzamide) selenides and their conversion to hypervalent spirodiazaselenuranes and hydroxy congeners. *Dalton Trans.* **2019**, *48*, 7249–7260. https://doi.org/10.1039/c8dt04832k — COD 7048787
60. Hartmann, D.; Braner, S.; Greb, L. Bis(perchlorocatecholato)silane and heteroleptic bidonors: hidden frustrated Lewis pairs resulting from ring strain. *Chem. Commun.* **2021**, *57*, 8572–8575. https://doi.org/10.1039/d1cc03452a — COD 7128773; COD 7128774
61. Luo, Y.-a.; Zhao, Z.; Chen, T.; Li, Y.; Zhao, Y.; Stephan, D. W.; Wu, Y. Stannyl phosphaketene as a synthon for phosphorus analogues of β-lactams. *Chem. Commun.* **2023**, *59*, 10956–10959. https://doi.org/10.1039/d3cc03117a — COD 7132025; COD 7132027
62. Gon, M.; Morisaki, Y.; Tanimura, K.; Tanaka, K. Preparation of seven-coordinated hypervalent tin(iv)-fused azobenzene and applications for stimuli-responsive π-conjugated polymer films. *Dalton Trans.* **2024**, *53*, 11858–11866. https://doi.org/10.1039/d4dt01738b — COD 7716481
63. Baryshnikova, S. V.; Shisterova, P. O.; Arsenyev, M. V.; Meshcheryakova, I. N.; Kolevatov, D. S.; Yakushev, I. A.; Kocherova, T. N.; Aysin, R. R.; Piskunov, A. V. Antimony(v) complexes with tetradentate ONNO redox-active ligands: optical, electrochemical and photothermal properties. *Dalton Trans.* **2026**, *55*, 835–844. https://doi.org/10.1039/d5dt02666k — COD 7719983

## Primary publications of the CSD crystal structures (tier C VSEPR entries, via tmQM)

64. Hering, F.; Nitsch, J.; Paul, U.; Steffen, A.; Bickelhaupt, F. M.; Radius, U. Bite-angle bending as a key for understanding group-10 metal reactivity of d 10 -[M(NHC) 2 ] complexes with sterically modest NHC ligands. *Chem. Sci.* **2015**, *6*, 1426–1432. https://doi.org/10.1039/c4sc02998d — CSD NOTQEU
65. Gao, J.-F.; Nie, R.-R.; Feng, Z.; Zhu, D.-R. *Chin. J. Inorg. Chem.* (Wuji Huaxue Xuebao) **2021**, *37*, 1707. https://doi.org/10.11862/CJIC.2021.190 — CSD CARLIU
66. Di Santo, A.; Pérez, H.; Echeverría, G. A.; Piro, O. E.; Iglesias, R. A.; Carbonio, R. E.; Ben Altabef, A.; Gil, D. M. Exploring weak intermolecular interactions in thiocyanate-bonded Zn(ii) and Cd(ii) complexes with methylimidazole: crystal structures, Hirshfeld surface analysis and luminescence properties. *RSC Adv.* **2018**, *8*, 23891–23902. https://doi.org/10.1039/c8ra04452j — CSD CICBIC
67. Jones, D.; Roberts, A.; Cavell, K.; Keim, W.; Englert, U.; Skelton, B. W.; White, A. H. Synthesis of new adducts and co-ordination complexes of zirconium and titanium containing β-aminoketone ligands. Crystal structures of isostructural adducts MCl4·2PriHNCMeCHCMeO (M = Ti or Zr) and the complex [Zr(PhNCMeCHCMeO)2Cl2]. *J. Chem. Soc., Dalton Trans.* **1998**, 255–262. https://doi.org/10.1039/a707422k — CSD DAPQOA
68. Shimada, S.; Tanaka, M.; Shiro, M. The First Silylpalladium(IV) Complex. *Angew. Chem. Int. Ed. Engl.* **1996**, *35*, 1856–1858. https://doi.org/10.1002/anie.199618561 — CSD NAHBAZ
69. Hückstädt, H.; Homborg, H. Synthesis and Properties of trans-Bisnitro-phthalocyaninato(2-)iridate(III) and Pyridine-nitro-phthalocyaninato(2-)iridium(III); Crystal Structure of linear-Bis(triphenylphosphine)iminium trans-Bisnitro-phthalocyaninato(2-)iridate(III). *Z. Naturforsch., B: Chem. Sci.* **1997**, *52*, 1003–1010. https://doi.org/10.1515/znb-1997-0822 — CSD RILVOX
70. Cybulski, M. K.; McKay, D.; Macgregor, S. A.; Mahon, M. F.; Whittlesey, M. K. Room Temperature Regioselective Catalytic Hydrodefluorination of Fluoroarenes with trans‐[Ru(NHC)4H2] through a Concerted Nucleophilic Ru−H Attack Pathway. *Angew. Chem., Int. Ed.* **2017**, *56*, 1515–1519. https://doi.org/10.1002/anie.201610820 — CSD SAHBIP
71. Marchetti, F.; Pampaloni, G.; Zacchini, S. Complexes of Niobium(V) and Tantalum(V) Halides with Ligands that Contain N–C=O and P=O Functionalities: A Synthetic and Structural Study. *Eur. J. Inorg. Chem.* **2008**, *2008*, 453–462. https://doi.org/10.1002/ejic.200700911 — CSD SIVCAC
72. Lu, W.; Barber, P. S.; Kelley, S. P.; Rogers, R. D. Coordination and extraction of mercury(ii) with an ionic liquid-based thione extractant. *Dalton Trans.* **2013**, *42*, 12908. https://doi.org/10.1039/c3dt50410g — CSD VEZXUV
73. Nikiforov, G. B.; Roesky, H. W.; Jones, P. G.; Magull, J.; Ringe, A.; Oswald, R. B. Preparation of Ti(IV) Fluoride N-Heterocyclic Carbene Complexes. *Inorg. Chem.* **2008**, *47*, 2171–2179. https://doi.org/10.1021/ic701751r — CSD VOBDAS
74. Pérez, H.; Di Santo, A.; Piro, O. E.; Echeverría, G. A.; González, M.; Ben Altabef, A.; Gomila, R. M.; Frontera, A.; Gil, D. M. Novel ‘main-part’ isostructuralism in metal complexes with 1-methylimidazole: crystal structures, energy calculations and magnetic properties. *Dalton Trans.* **2021**, *50*, 17029–17040. https://doi.org/10.1039/d1dt03159g — CSD ZARGIM
75. Manakin, Y. V.; Mironov, V. S.; Bazhenova, T. A.; Lyssenko, K. A.; Gilmutdinov, I. F.; Bikbaev, K. S.; Masitov, A. A.; Yagubskii, E. B. (Et 4 N)[Mo III (DAPBH)Cl 2 ], the first pentagonal-bipyramidal Mo(iii) complex with a N 3 O 2 -type Schiff-base ligand: manifestation of unquenched orbital momentum and Ising-type magnetic anisotropy. *Chem. Commun.* **2018**, *54*, 10084–10087. https://doi.org/10.1039/c8cc06038j — CSD IFETEV
76. Manakin, Y. V.; Mironov, V. S.; Bazhenova, T. A.; Yakushev, I. A.; Gilmutdinov, I. F.; Simonov, S. V.; Yagubskii, E. B. (Et 4 N)[W III (DAPBH)(CN) 2 ], the first pentagonal-bipyramidal W(iii) complex with unquenched orbital angular momentum: a novel Ising-type magnetic building block for single-molecule magnets. *Chem. Commun.* **2023**, *59*, 643–646. https://doi.org/10.1039/d2cc05998c — CSD ZEYQON
77. Malassa, A.; Agthe, C.; Görls, H.; Podewitz, M.; Yu, L.; Herrmann, C.; Reiher, M.; Westerhausen, M. Synthesis, Structures, and Magnetic Properties of N ‐Trialkylsilyl‐8‐amidoquinoline Complexes of Chromium, Manganese, Iron, and Cobalt as well as of Wheel‐Like Hexanuclear Iron(II) and Manganese(II) Bis(8‐amidoquinoline). *Eur. J. Inorg. Chem.* **2010**, *2010*, 1777–1790. https://doi.org/10.1002/ejic.200901158 — CSD LUYXEJ
78. Rheingold, A. L.; Theopold, K. H. CSD Communication (private communication to the CSD), **2019**. — CSD QOTSUQ
79. Schendzielorz, F. S.; Finger, M.; Volkmann, C.; Würtele, C.; Schneider, S. A Terminal Osmium(IV) Nitride: Ammonia Formation and Ambiphilic Reactivity. *Angew. Chem., Int. Ed.* **2016**, *55*, 11417–11420. https://doi.org/10.1002/anie.201604917 — CSD DAKMEK
80. Wieder, N. L.; Carroll, P. J.; Berry, D. H. Structure and Reactivity of Acetylene Complexes of Bis(imino)pyridine Ruthenium(0). *Organometallics* **2011**, *30*, 2125–2136. https://doi.org/10.1021/om100953g — CSD DAMBEA
81. Askevold, B.; Khusniyarov, M. M.; Herdtweck, E.; Meyer, K.; Schneider, S. A Square‐Planar Ruthenium(II) Complex with a Low‐Spin Configuration. *Angew. Chem., Int. Ed.* **2010**, *49*, 7566–7569. https://doi.org/10.1002/anie.201002296 — CSD GUZHOZ
82. Lake, B. R. M.; Shaver, M. P. Iron(ii) β-ketiminate complexes as mediators of controlled radical polymerisation. *Dalton Trans.* **2016**, *45*, 15840–15849. https://doi.org/10.1039/c6dt01208f — CSD ILOMAZ
83. Beck, W.; Fehlhammer, W. P.; Feldl, K.; Klapötke, T. M.; Kramer, G.; Mayer, P.; Piotrowski, H.; Pöllmann, P.; Ponikwar, W.; Schütt, T.; Schuierer, E.; Vogt, M. Crystal Structures of (PPh3)2Pd(N3)2, (AsPh3)2Pd(N3)2, (2-Chloropyridine)2Pd(N3)2, [(AsPh4)2][Pd2(N3)4Cl2], [(PNP)2][Pd(N3)4], [(AsPh4)2][Pt(N3)4] · 2 H2O, and [(AsPh4)2][Pt(N3)6]. *Z. anorg. allg. Chem.* **2001**, *627*, 1751–1758. https://doi.org/10.1002/1521-3749(200108)627:8<1751::aid-zaac1751>3.0.co;2-5 — CSD NEHJAL
84. Sukhikh, A. S.; Klyamer, D. D.; Basova, T. V. X-Ray Diffraction Study of Crystal Structure and Thin Films of Chromium(II) Phthalocyaninate. *Macroheterocycles* **2020**, *13*, 13–18. https://doi.org/10.6060/mhc191177b — CSD ZAHKAY
85. Sangtrirutnugul, P.; Stradiotto, M.; Tilley, T. D. Rhodium Complexes Containing a Tridentate Bis(8-quinolyl)methylsilyl Ligand: Synthesis and Reactivity. *Organometallics* **2006**, *25*, 1607–1617. https://doi.org/10.1021/om050859v — CSD CEGTUE
86. Noschang Cabral, B.; Fonseca Rodrigues, J.; Roca Jungfer, M.; Krebs, A.; Hagenbach, A.; Schulz Lang, E.; Abram, U. Oxidorhenium(V) and Rhenium(III) Complexes with Arylselenolato and ‐tellurolato Ligands. *Eur. J. Inorg. Chem.* **2023**, *26*, e202300023. https://doi.org/10.1002/ejic.202300023 — CSD CIJGIP
87. Huang, D.-s.; Liu, X.-r.; Zhao, S.-s.; Yang, Z.-w. Crystal structures of three transition metal complexes with salicylaldehyde-4-hydroxy phenylacetyl acylhydrazone and their interactions with CT-DNA and BSA. *Polyhedron* **2022**, *211*, 115516. https://doi.org/10.1016/j.poly.2021.115516 — CSD DAJNEL
88. Schaub, T.; Backes, M.; Radius, U. Nickel(0) Complexes of N-Alkyl-Substituted N-Heterocyclic Carbenes and Their Use in the Catalytic Carbon−Carbon Bond Activation of Biphenylene. *Organometallics* **2006**, *25*, 4196–4206. https://doi.org/10.1021/om0604223 — CSD DENRAQ
89. West, N. M.; White, P. S.; Templeton, J. L.; Nixon, J. F. Cycloaddition Reactions of Terminal Alkynes and Phosphaalkynes with an Isolable 5-Coordinate β-Diiminate Platinum(IV) Dihydrosilyl Complex. *Organometallics* **2009**, *28*, 1425–1434. https://doi.org/10.1021/om800968v — CSD DOZJIM
90. De Jesus Silva, J.; Pucino, M.; Zhai, F.; Mance, D.; Berkson, Z. J.; Nater, D. F.; Hoveyda, A. H.; Copéret, C.; Schrock, R. R. Boosting the Metathesis Activity of Molybdenum Oxo Alkylidenes by Tuning the Anionic Ligand σ Donation. *Inorg. Chem.* **2021**, *60*, 6875–6880. https://doi.org/10.1021/acs.inorgchem.0c03173 — CSD EKORII
91. Bierschenk, T. R.; Guerra, M. A.; Juhlke, T. J.; Larson, S. B.; Lagow, R. J. Synthesis of trifluorosilyl organometallic complexes from trifluorosilyl radicals and metal atoms. *J. Am. Chem. Soc.* **1987**, *109*, 4855–4860. https://doi.org/10.1021/ja00250a017 — CSD FODXOL
92. Abram, U.; Dilworth, J. R. Technetium Complexes with 2-Mercapto-methyltetrazolate. *Z. anorg. allg. Chem.* **1999**, *625*, 609–612. https://doi.org/10.1002/(sici)1521-3749(199904)625:4<609::aid-zaac609>3.0.co;2-r — CSD GOGQIC
93. Schultz, K. M.; Goldberg, K. I.; Gusev, D. G.; Heinekey, D. M. Synthesis, Structure, and Reactivity of Iridium NHC Pincer Complexes. *Organometallics* **2011**, *30*, 1429–1437. https://doi.org/10.1021/om101024x — CSD IVUCEI
94. Rosset, J. M.; Floriani, C.; Mazzanti, M.; Chiesi-Villa, A.; Guastini, C. Vanadium(III)-carbon and titanium(III)-carbon functionalities supported by a tetradentate Schiff base ligand. *Inorg. Chem.* **1990**, *29*, 3991–3996. https://doi.org/10.1021/ic00345a016 — CSD JEWMAZ
95. Gupta, D.; Gaur, A. K.; Chauhan, D.; Thakur, S. K.; Jeyapalan, V.; Singh, S.; Rajaraman, G.; Venkataramani, S. Solid-state photochromic arylazopyrazole-based transition metal complexes. *Inorg. Chem. Front.* **2022**, *9*, 2315–2327. https://doi.org/10.1039/d2qi00325b — CSD KECPIV
96. Yu, Y.-D.; Price, J. S.; Romero, P. E.; Emslie, D. J. H. Homoleptic 1-norbornyl complexes of group 4 and manganese: synthesis, structures, volatility, and thermal stability. *Can. J. Chem.* **2022**, *100*, 704–711. https://doi.org/10.1139/cjc-2022-0103 — CSD KOBTAA
97. Kakaliou, L.; Scanlon; Qian, B.; Baek, S. W.; Smith, M. R.; Motry, D. H. Five- and Six-Coordinate Group 4 Compounds Stabilized by β-Ketiminate and Diketiminate Ligands: Syntheses and Comparisons between Solid-State and Solution Structures. *Inorg. Chem.* **1999**, *38*, 5964–5977. https://doi.org/10.1021/ic981364j — CSD LIRDUL
98. Ortner, K.; Hilditch, L.; Zheng, Y.; Dilworth, J. R.; Abram, U. Gold Complexes with Potentially Tri- and Tetradentate Phosphinothiolate Ligands. *Inorg. Chem.* **2000**, *39*, 2801–2806. https://doi.org/10.1021/ic000015y — CSD MELFAK
99. Krause, J.; Haack, K.-J.; Pörschke, K.-R. Hepta-1,6-diene and diallyl ether complexes of palladium(0) and platinum(0):a route to L–M(alkene)2 complexes containing non-activated alkenes. *Chem. Commun.* **1998**, 1291–1292. https://doi.org/10.1039/a802381f — CSD PIJKOI
100. Li, J.; Lord, R. L.; Noll, B. C.; Baik, M.; Schulz, C. E.; Scheidt, W. R. Cyanide: A Strong‐Field Ligand for Ferrohemes and Hemoproteins?. *Angew. Chem., Int. Ed.* **2008**, *47*, 10144–10146. https://doi.org/10.1002/anie.200804116 — CSD QOVKIW
101. Davies, S. C.; Hughes, D. L.; Janas, Z.; Jerzykiewicz, L. B.; Richards, R. L.; Sanders, J. R.; Silverston, J. E.; Sobota, P. Vanadium Complexes of the N(CH2CH2S)33-and O(CH2CH2S)22-Ligands with Coligands Relevant to Nitrogen Fixation Processes. *Inorg. Chem.* **2000**, *39*, 3485–3498. https://doi.org/10.1021/ic9909476 — CSD XADXOP
102. Husebo, T. L.; Jensen, C. M. Formation of Indenyl Dihydride Complexes from an Iridium Polyhydride Complex: Molecular Structures of (.eta.5-C9H7)IrH2(PPri3) and the .eta.3-Indenyl Intermediate (.eta.3-C9H7)IrH2(PPri3)2. *Organometallics* **1995**, *14*, 1087–1088. https://doi.org/10.1021/om00003a004 — CSD YOSSII
103. Reckziegel, A.; Pietzonka, C.; Kraus, F.; Werncke, C. G. C−H Bond Activation by an Imido Cobalt(III) and the Resulting Amido Cobalt(II) Complex. *Angew. Chem., Int. Ed.* **2020**, *59*, 8527–8531. https://doi.org/10.1002/anie.201914718 — CSD YUDVIF
104. Minnick, J. L.; Raincrow, J.; Meinders, G.; Latifi, R.; Tahsini, L. Synthesis, Characterization, and Spectroscopic Studies of 2,6-Dimethylpyridyl-Linked Cu(I)–CNC Complexes: The Electronic Influence of Aryl Wingtips on Copper Centers. *Inorg. Chem.* **2023**, *62*, 15912–15926. https://doi.org/10.1021/acs.inorgchem.3c01973 — CSD ZIQKIX

## Which entries come from each paper

| paper | ref | entries (dataset name ← label in the paper) |
|---|---|---|
| ME_03 | [8] | shot_paper3_16 ← 16; shot_paper3_17 ← 17; shot_paper3_20 ← 20; shot_paper3_21 ← 21; shot_paper3_23 ← 23; shot_paper3_24 ← 24; shot_paper3_26 ← 26; shot_paper3_27 ← 27; shot_paper3_31 ← 31; shot_paper3_9 ← 9 |
| ME_09 | [9] | shot_paper9_10 ← 10; shot_paper9_11 ← 11; shot_paper9_12 ← 12; shot_paper9_13 ← 13; shot_paper9_33 ← 33; shot_paper9_39_endo ← 39_endo; shot_paper9_41_endo ← 41_endo; shot_paper9_42 ← 42; shot_paper9_47a ← 47a; shot_paper9_9 ← 9 |
| ME_12 | [10] | paper_pr12_A ← A; paper_pr12_B ← B; paper_pr12_D ← D; paper_pr12_D_2 ← D_2; paper_pr12_E ← E |
| ME_14 | [11] | paper_pr14_1 ← 1; paper_pr14_10 ← 10; paper_pr14_2 ← 2; paper_pr14_3 ← 3; paper_pr14_4 ← 4; paper_pr14_5 ← 5; paper_pr14_6 ← 6 |
| ME_19 | [12] | shot_paper19_3aaPdH ← 3aaPdH; shot_paper19_in1 ← in1 |
| DU8 | [13] | shot_du8_2 ← 2; shot_du8_3 ← 3; shot_du8_5 ← 5; shot_du8_18 ← 18; shot_du8_24 ← 24 |
| MOR41 | [14] | shot_mor41_PR25 ← PR25; shot_mor41_PR16 ← PR16; shot_mor41_PR41 ← PR41; shot_mor41_ED26 ← ED26; shot_mor41_PR36 ← PR36; shot_mor41_PR22 ← PR22; shot_mor41_PR04 ← PR04; shot_mor41_PR10 ← PR10; shot_mor41_PR24 ← PR24 |
| ROST61 | [15] | shot_rost61_m124 ← m124; shot_rost61_m110 ← m110; shot_rost61_m128 ← m128; shot_rost61_m116 ← m116; shot_rost61_m121 ← m121; shot_rost61_m53 ← m53; shot_rost61_m147 ← m147; shot_rost61_m144 ← m144; shot_rost61_m26 ← m26; shot_rost61_m39 ← m39; shot_rost61_m72 ← m72; shot_rost61_m98 ← m98; shot_rost61_m132 ← m132; shot_rost61_m133 ← m133; shot_rost61_m118 ← m118; shot_rost61_m87 ← m87; shot_rost61_m109 ← m109; shot_rost61_m67 ← m67; shot_rost61_m24 ← m24; shot_rost61_m61 ← m61; shot_rost61_m136 ← m136; shot_rost61_m131 ← m131 |
| PMC12458972 | [17] | shot_om_PMC12458972_3 ← 3; shot_om_PMC12458972_4 ← 4; shot_om_PMC12458972_2 ← 2 |
| PMC12892316 | [18] | shot_om_PMC12892316_2 ← 2; shot_om_PMC12892316_3 ← 3; shot_om_PMC12892316_4 ← 4 |
| PMC12869483 | [19] | shot_om_PMC12869483_4 ← 4; shot_om_PMC12869483_3 ← 3 |
| PMC12977057 | [20] | shot_om_PMC12977057_2 ← 2 |
| PMC12326349 | [21] | shot_om_PMC12326349_vi ← vi; shot_om_PMC12326349_ii ← ii; shot_om_PMC12326349_i ← i; shot_om_PMC12326349_iii ← iii; shot_om_PMC12326349_v ← v; shot_om_PMC12326349_iv ← iv |
| PMC12308804 | [22] | shot_om_PMC12308804_xylcpticubr ← xylcpticubr; shot_om_PMC12308804_phcpticubr ← phcpticubr |
| PMC12522133 | [23] | shot_om_PMC12522133_crdgpy23 ← crdgpy23 |
| PMC12690572 | [24] | shot_om_PMC12690572_1a ← 1a; shot_om_PMC12690572_1b ← 1b; shot_om_PMC12690572_2a ← 2a; shot_om_PMC12690572_2b ← 2b |
| PMC12334357 | [25] | shot_om_PMC12334357_3 ← 3; shot_om_PMC12334357_2a ← 2a |
| PMC13058889 | [26] | shot_om_PMC13058889_7 ← 7; shot_om_PMC13058889_6 ← 6; shot_om_PMC13058889_1 ← 1; shot_om_PMC13058889_3 ← 3 |
| PMC12869501 | [27] | shot_om_PMC12869501_3b ← 3b; shot_om_PMC12869501_2b ← 2b |
| PMC13580183 | [28] | shot_om_PMC13580183_5meso ← 5meso; shot_om_PMC13580183_5ssrr ← 5ssrr; shot_om_PMC13580183_a5 ← a5; shot_om_PMC13580183_a4 ← a4; shot_om_PMC13580183_a2 ← a2; shot_om_PMC13580183_a1mecndeprot ← a1mecn_deprot; shot_om_PMC13580183_a1mecn ← a1mecn |
| PMC12076555 | [29] | shot_om_PMC12076555_1naw4mo ← 1naw4mo |
| PMC13390040 | [30] | shot_om_PMC13390040_int2 ← int2; shot_om_PMC13390040_inti ← inti; shot_om_PMC13390040_intiii ← intiii; shot_om_PMC13390040_intii ← intii; shot_om_PMC13390040_int3 ← int3; shot_om_PMC13390040_int6 ← int6; shot_om_PMC13390040_3 ← 3; shot_om_PMC13390040_int1 ← int1 |
| PMC12930352 | [31] | shot_om_PMC12930352_ra10 ← ra10; shot_om_PMC12930352_rd12 ← rd12; shot_om_PMC12930352_rc7 ← rc7; shot_om_PMC12930352_ra7 ← ra7; shot_om_PMC12930352_rc5 ← rc5; shot_om_PMC12930352_ra5 ← ra5; shot_om_PMC12930352_rb5 ← rb5 |
| PMC13418093 | [32] | shot_om_PMC13418093_4 ← 4; shot_om_PMC13418093_7 ← 7; shot_om_PMC13418093_5 ← 5; shot_om_PMC13418093_i ← i; shot_om_PMC13418093_a1 ← a1; shot_om_PMC13418093_a2 ← a2; shot_om_PMC13418093_6 ← 6; shot_om_PMC13418093_fulvenech4 ← fulvenech4 |
| PMC11894599 | [33] | shot_om_PMC11894599_13a ← 13a; shot_om_PMC11894599_10 ← 10; shot_om_PMC11894599_viiiir ← viiiir; shot_om_PMC11894599_9 ← 9; shot_om_PMC11894599_xiiir ← xiiir; shot_om_PMC11894599_11a ← 11a; shot_om_PMC11894599_11 ← 11 |
| PMC13231423 | [34] | shot_om_PMC13231423_6auclge2 ← 6auclge2; shot_om_PMC13231423_6auge2cl ← 6auge2cl; shot_om_PMC13231423_6augeclge ← 6augeclge |
| PMC12933881 | [35] | shot_om_PMC12933881_3 ← 3 |
| PMC12820928 | [36] | shot_om_PMC12820928_5 ← 5; shot_om_PMC12820928_4a ← 4a; shot_om_PMC12820928_14c ← 14c; shot_om_PMC12820928_4c ← 4c; shot_om_PMC12820928_10 ← 10; shot_om_PMC12820928_8 ← 8; shot_om_PMC12820928_11b ← 11b; shot_om_PMC12820928_15b ← 15b |
| PMC13081111 | [37] | shot_om_PMC13081111_8 ← 8 |
| BJOC_12_13 | [38] | shot_om_BJOC_12_13_3hh ← 3hh; shot_om_BJOC_12_13_3ht ← 3ht; shot_om_BJOC_12_13_6 ← 6 |
| PMC12856905 | [39] | shot_om_PMC12856905_fr2och3 ← fr2och3; shot_om_PMC12856905_f ← f |
| PMC12522683 | [40] | shot_om_PMC12522683_3 ← 3; shot_om_PMC12522683_6 ← 6 |
| PMC12818750 | [41] | shot_om_PMC12818750_a ← a |
| PMC12153055 | [42] | shot_om_PMC12153055_1 ← 1; shot_om_PMC12153055_2 ← 2; shot_om_PMC12153055_3 ← 3; shot_om_PMC12153055_4 ← 4 |
| PMC12606712 | [43] | shot_om_PMC12606712_39d ← 39d; shot_om_PMC12606712_39p ← 39p; shot_om_PMC12606712_27d ← 27d |
| PMC12709582 | [44] | shot_om_PMC12709582_3hfdb ← 3hfdb; shot_om_PMC12709582_3hfda ← 3hfda |
| PMC13371084 | [45] | shot_om_PMC13371084_26 ← 26 |
| PMC12235671 | [46] | shot_om_PMC12235671_7 ← 7 |
| PMC9554919 | [47] | shot_om_PMC9554919_6 ← 6 |

## Notes

- MOR41 coordinates were taken from the MOR41 GitHub repository [16]; drawings are re-crops of Figure 1 of ref. [14]. ROST61 coordinates come from the ROST61 structure archive (rost61.tar.gz) released with ref. [15]; drawings are re-crops of the reaction schemes in its SI.
- shot_rost61_m61: the SI drawing shows a generic metal "M"; it was relabelled "Ru" to match the coordinates (the SI caption reads "m61 (Ru)").
- Natural-product 2D drawings are the target-molecule drawings of SynArchive [7]; the page of each molecule is listed in the appendix and in `references.tsv` (column `drawing_url`). All 70 names match a SynArchive entry.
- Natural-product CIDs taken from the xyz header where present, otherwise resolved from the compound name through PubChem PUG REST.
- The 101 `shot_om_*` entries come from the organometallic_xyz2d collection (d- and f-block complexes whose SI coordinates were matched atom by atom to a 2D structure printed in the same open-access paper). The picture is a crop of that published figure. The only edits are removing the compound label, converting colour to black, erasing counter-ions that the xyz does not contain, and replacing an icon defined only in the caption by the drawn group or a standard abbreviation; each entry lists its edits in `references.tsv` (column `drawing_origin`).
- All 31 papers behind the organometallic entries are published under CC BY; candidates from CC BY-NC and CC BY-NC-ND papers were not used.
- `descriptors.tsv` charge for the organometallic entries is the total charge of what the xyz contains: the complex ion when the counter-ion was not computed (the PMC13418093 iridium complexes, whose triflate was removed from both xyz and picture, are +1 cations), and 0 when the xyz holds both ions (the [HPCy₃]⁺ pair PMC13390040_intiii).
- The older published-figure crops were cleaned in the same way: in 14 pictures compound numbers, NMR locants and colour highlights were removed. In shot_paper3_9 the 2-Nap label, which overlapped the carbonyl O, was moved onto a horizontal hashed bond, which keeps the same configuration. `references.tsv` (column `drawing_origin`) lists the edit of each picture.
- Every picture of a charged species shows its charge: a bracket with the charge, or a single charged atom that carries the whole charge. In 26 pictures the mark was missing, mostly because the counter-ion that implied it had been erased, and it was added in the picture's own style; `references.tsv` (column `drawing_origin`) names each one.
- Spin: `descriptors.tsv` gives the multiplicity (2S+1) of every entry. The 35 open-shell species carry "S = …" under the structure: 22 ROST61 molecules (from the .UHF files of the ROST61 archive [15]), 5 pr12 dicobalt species (from the structure files of the benchmark the pr12 coordinates came from), and 7 organometallic complexes (from their papers). All other entries are closed-shell singlets; the tmQM entries are recorded with S = 0, and the electron count of every entry was checked against its charge and multiplicity.

## Appendix: PubChem CIDs and SynArchive pages

| entry | CID | coordinates | 2D drawing |
|---|---|---|---|
| vsepr_tierA_bent_imine_N_42609849_N10 | 42609849 | PubChem 3D conformer | drawn from the xyz |
| np_alkaloid_251f | 10868757 | PubChem 3D conformer | https://synarchive.com/syn/25 |
| np_alkaloid_gb_13 | 11415804 | PubChem 3D conformer | https://synarchive.com/syn/237 |
| np_aspidofractinine | 9548854 | PubChem 3D conformer | https://synarchive.com/syn/67 |
| np_aplysistatin | 100219 | PubChem 3D conformer | https://synarchive.com/syn/325 |
| np_aspidophytine | 11783895 | PubChem 3D conformer | https://synarchive.com/syn/38 |
| np_dodecahedrane | 123218 | PubChem 3D conformer | https://synarchive.com/molecule/dodecahedrane |
| np_dysinosin_a | 10439038 | PubChemQC-PM6 conformer | https://synarchive.com/syn/42 |
| np_echitamidine | 10991442 | PubChem 3D conformer | https://synarchive.com/syn/254 |
| np_endiandric_acid_a_methyl_ester | 11781740 | PubChem 3D conformer | https://synarchive.com/syn/281 |
| np_epolactaene | 6442272 | PubChem 3D conformer | https://synarchive.com/syn/85 |
| np_estrone | 5870 | PubChem 3D conformer | https://synarchive.com/syn/285 |
| np_fuchsiaefoline | 163184393 | PubChem 3D conformer | https://synarchive.com/syn/236 |
| np_gelsemine | 5390854 | PubChem 3D conformer | https://synarchive.com/syn/29 |
| np_azadiradione | 12308714 | PubChem 3D conformer | https://synarchive.com/syn/318 |
| np_caribenol_a | 23583031 | PubChem 3D conformer | https://synarchive.com/syn/146 |
| np_carpanone | 131876914 | PubChem 3D conformer | https://synarchive.com/syn/54 |
| np_chlorophyll_a | 12085802 | PubChemQC-PM6 conformer | https://synarchive.com/syn/24 |
| np_aspidospermidine | 6857472 | PubChem 3D conformer | https://synarchive.com/syn/301 |
| np_asteltoxin | 6438150 | PubChem 3D conformer | https://synarchive.com/syn/142 |
| np_daphnilactone_a | 101586923 | PubChem 3D conformer | https://synarchive.com/syn/173 |
| np_ginkgolide_b | 11973122 | PubChem 3D conformer | https://synarchive.com/syn/20 |
| np_chlorodysinosin_a | 16079152 | PubChemQC-PM6 conformer | https://synarchive.com/syn/44 |
| np_cholesterol | 5997 | PubChem 3D conformer | https://synarchive.com/molecule/cholesterol |
| np_cortistatin_a | 11561907 | PubChem 3D conformer | https://synarchive.com/molecule/cortistatin_a |
| np_cylindrospermopsin | 42628600 | PubChem 3D conformer | https://synarchive.com/syn/136 |
| np_doliculide | 10438804 | PubChem 3D conformer | https://synarchive.com/syn/104 |
| np_dragmacidin_f | 21576986 | PubChem 3D conformer | https://synarchive.com/syn/178 |
| np_englerin_a | 46242512 | PubChem 3D conformer | https://synarchive.com/syn/314 |
| np_erythromycin_a | 12560 | PubChemQC-PM6 conformer | https://synarchive.com/molecule/erythromycin_a |
| np_kendomycin | 5472093 | PubChem 3D conformer | https://synarchive.com/syn/328 |
| np_oscillarin | 5289082 | PubChem 3D conformer | https://synarchive.com/syn/43 |
| np_penitrem_d | 3035208 | PubChem 3D conformer | https://synarchive.com/syn/31 |
| np_reserpine | 5770 | PubChem 3D conformer | https://synarchive.com/molecule/reserpine |
| np_retigeranic_acid | 170283 | PubChem 3D conformer | https://synarchive.com/molecule/retigeranic_acid |
| np_strychnine | 441071 | PubChem 3D conformer | https://synarchive.com/molecule/strychnine |
| np_strychnofoline | 182369 | PubChem 3D conformer | https://synarchive.com/syn/327 |
| np_tirandamycin_b | 54728535 | PubChem 3D conformer | https://synarchive.com/syn/249 |
| np_tjipanazole_e | 11420375 | PubChem 3D conformer | https://synarchive.com/syn/312 |
| np_tunicamycin_v | 11104835 | PubChemQC-PM6 conformer | https://synarchive.com/syn/307 |
| np_xyloketal_a | 10994129 | PubChem 3D conformer | https://synarchive.com/syn/311 |
| np_ziziphine_n | 22524109 | PubChem 3D conformer | https://synarchive.com/syn/244 |
| np_zaragozic_acid_c | 11814656 | PubChemQC-PM6 conformer | https://synarchive.com/syn/41 |
| np_sarain_a | 101603871 | PubChem 3D conformer | https://synarchive.com/syn/33 |
| np_pactamycin | 5289124 | PubChem 3D conformer | https://synarchive.com/syn/134 |
| np_u_106305 | 10669141 | PubChem 3D conformer | https://synarchive.com/syn/26 |
| np_nominine | 11961129 | PubChem 3D conformer | https://synarchive.com/syn/133 |
| np_phyllanthocin | 5477680 | PubChemQC-PM6 conformer | https://synarchive.com/syn/63 |
| np_okilactomycin | 10477012 | PubChem 3D conformer | https://synarchive.com/syn/90 |
| np_buckminsterfullerene | 123591 | PubChemQC-PM6 conformer | https://synarchive.com/syn/100 |
| np_ryanodol | 14588813 | PubChem 3D conformer | https://synarchive.com/syn/16 |
| np_pseudolaric_acid_b | 6475943 | PubChem 3D conformer | https://synarchive.com/syn/103 |
| np_kinamycin_c | 135430800 | PubChem 3D conformer | https://synarchive.com/syn/109 |
| np_maritimol | 101277366 | PubChem 3D conformer | https://synarchive.com/syn/174 |
| np_ingenol | 442042 | PubChem 3D conformer | https://synarchive.com/molecule/ingenol |
| np_progesterone | 5994 | PubChem 3D conformer | https://synarchive.com/syn/302 |
| np_yohimbine | 8969 | PubChem 3D conformer | https://synarchive.com/syn/88 |
| np_pentacycloanammoxic_acid | 9972184 | PubChemQC-PM6 conformer | https://synarchive.com/syn/30 |
| np_laurenene | 91747181 | PubChem 3D conformer | https://synarchive.com/molecule/laurenene |
| np_murrayazoline | 21770913 | PubChem 3D conformer | https://synarchive.com/syn/81 |
| np_wodeshiol | 10927155 | PubChem 3D conformer | https://synarchive.com/syn/27 |
| np_maoecrystal_v | 21575535 | PubChem 3D conformer | https://synarchive.com/syn/295 |
| np_leuconoxine | 70698272 | PubChem 3D conformer | https://synarchive.com/syn/287 |
| np_minfiensine | 5388292 | PubChem 3D conformer | https://synarchive.com/syn/308 |
| np_trifarienol_b | 11107418 | PubChem 3D conformer | https://synarchive.com/syn/248 |
| np_malayamycin_a | 9819404 | PubChem 3D conformer | https://synarchive.com/syn/37 |
| np_punctatin_a | 101101 | PubChem 3D conformer | https://synarchive.com/syn/304 |
| np_kinamycin_f | 135618571 | PubChem 3D conformer | https://synarchive.com/molecule/kinamycin_f |
| np_morphine | 5288826 | PubChem 3D conformer | https://synarchive.com/molecule/morphine |
| np_gymnomitrol | 14109432 | PubChem 3D conformer | https://synarchive.com/molecule/gymnomitrol |
| np_tetrodotoxin | 11174599 | PubChem 3D conformer | https://synarchive.com/syn/35 |
