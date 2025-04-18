# Group Size Simulation for Comparative Inequality Research

This repository contains a simulation framework for exploring how group size affects measured inequality in incarceration rates across different causal models. This work is based on the research of Sebastian Spitz, John Clegg, and Adaner Usmani on comparative-historical studies of racial inequality in punishment.

## Project Overview

When comparing racial inequality in incarceration across different countries or time periods, researchers face methodological challenges because the demographic composition of societies varies significantly. This simulation explores how the relative size of racial groups mathematically affects measured inequality, independent of actual differences in treatment.

## Core Research Question

**How does the relative size of racial/ethnic groups in a population affect our measurements of inequality in incarceration rates between these groups?**

For example, comparing inequality between Black Americans (≈13% of US population) and Black South Africans (≈81% of South African population) may be problematic because group size itself mathematically affects possible disparity ratios.

## Key Concepts

### Causal Pathways

The simulation explores two potential causal pathways:

1. **Indirect Pathway**: Race → Class Position → Incarceration Risk
   - Race affects economic position, which then affects incarceration
   - No direct racial bias in the criminal justice system

2. **Direct Pathway**: Race → Incarceration Risk
   - Race directly affects incarceration probability independent of class
   - Captures direct discrimination in the criminal justice system


## Repository Structure

The repository is organized into separate modules for each causal pathway:

- **direct_pathway/**: Simulation for the direct effect of race on incarceration
  - `README.md`: Detailed explanation of the direct pathway model
  - `src/`: Source code for the direct pathway simulation
  - `output/data/`: CSV and data files from simulation runs
  - `output/figures/`: Generated plots and visualizations

- **indirect_pathway/**: Simulation for the indirect effect through economic position
  - `README.md`: Detailed explanation of the indirect pathway model
  - `src/`: Source code for the indirect pathway simulation
  - `output/data/`: CSV and data files from simulation runs
  - `output/figures/`: Generated plots and visualizations

Each pathway module is self-contained with its own implementation, documentation, and output directories to facilitate clear comparison between the different causal models.



## Getting Started

[Will add installation and usage instructions as the project develops]

## Contributing

This is a research project in collaboration with Sebastian Spitz and the research team. Please contact the repository owner before making contributions.

## License

[Appropriate license information]

## References

Spitz, Sebastian, John Clegg, and Adaner Usmani. "Punishing Categories: The Comparative-Historical Study of Racial Inequality in Punishment." [PUBLISH DATE].