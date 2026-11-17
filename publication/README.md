# Publication

The presentation slides for this work (the paper will follow), presented at the **Colombo Quantum Computing Meetup (CQCM) 2026**.

**Title:** Quantum Fourier Transform for Image Compression: A Two-Qubit Simulation and SpinQ NMR Demonstration

**Authors:** M. J. Marapperuma, H. R. J. R. Rashmika, W. D. S. Vindula, Osanda Chinthila
Research and Development Centre for Mathematical Modelling, Department of Mathematics, University of Colombo, Sri Lanka.

## Contents

| Path | Description |
|---|---|
| Paper | **Available soon** (link and DOI will be added here) |
| [`presentation/ICCMM_26_497.pptx`](presentation/ICCMM_26_497.pptx) | Presentation slides (editable PowerPoint) |
| [`presentation/ICCMM_26_497.pdf`](presentation/ICCMM_26_497.pdf) | The same slides as a PDF |

## How the publication relates to the code

The code in this repository recomputes the numbers reported here:

| Reported in | Reproduced by |
|---|---|
| Paper Sections 3 and 5.1 (Equations 3 to 27, Table 1) | group 1 "Grayscale example" of `scripts/run_all.py` |
| Paper Sections 4.2 and 4.4 (circuit and 2048-shot Aer run) | group 2 "Circuit" |
| Paper Tables 2 and 3 (SpinQ probabilities and errors) | group 3 "SpinQ hardware", data in [`../data`](../data) |
| Slides: analysis over K, eight test images, error law, brightness, random images | groups 4 and 5 "Analysis" and "Monte Carlo" |

The analysis over other values of K, other images and random images appears in the slides only; it is not part of the paper.
The full recomputed-versus-reported table is in [`../results/report.md`](../results/report.md).

## Citing

See [`../CITATION.cff`](../CITATION.cff), or use:

> M. J. Marapperuma, H. R. J. R. Rashmika, W. D. S. Vindula and O. Chinthila, "Quantum Fourier Transform for
> Image Compression: A Two-Qubit Simulation and SpinQ NMR Demonstration," Colombo Quantum Computing Meetup
> (CQCM) 2026.

## Rights

The slides (and the paper, when released) are copyright of the authors. The MIT licence in the repository root applies to the
code only, not to the documents in this folder. Do not redistribute them without the authors' permission.
