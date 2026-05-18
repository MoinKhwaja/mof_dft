High-Throughput Screening Method to Find Metal-Organic Frameworks for CO2 Hydrogenation

Method Contains 4 Screening Tiers with Additional Properties Added to Passing Materials

Screens

1. Porosity - First Principle Screen - (https://doi.org/10.1021/acscatal.2c05155) - The Porosity of the MOF needs to allow for CO2, CH4, and H20 to pass through the structures pores, A size safe size to allow this to happen would be 4.5A. 
2. Bandgap - First Principle Screen - (Adjusted by https://doi.org/10.1002/adfm.202003792) - The Bandgap of the materials needs to be greater than 1.2 eV to allow for light assisted hydrogenation to take place in the material.
3. Water Stability - Machine Learning Screen - (https://doi.org/10.1021/jacs.4c05879) - The material needs to be stable if water is produced during the reverse water gas shift reaction, only the most highly stable materials are selected.
4. MOF Structure Stability - Machine Learning Screen - (https://doi.org/10.1038/s41597-022-01181-0) - The material needs to be stable when it is being synthesized, only the most highly stable materials are selected.

Additional Screens

5. Gas Adsorption and CO2/N2 Selectivity - Machine Learning - (https://doi.org/10.1038/s41586-019-1798-7) - The material should have a high gas adsoption energy to allow for many CO2 molecules to fill the material to allow for high conversion rates.
6. Thermal Degradation Temperature - Machine Learning - (https://doi.org/10.1038/s41597-022-01181-0) - The material needs to withstand high temperatures needed to commence the hydrogenation reaction.

First, we start with the QMOF database, a computational database with 20,000 MOFs that have had first principle calculations done on it, this is required if we are looking for light assisted materials. From this database, screens 1 and 2 (porosity and bandgap) are simple database screens where we can search for materials with the properties that we require. For bandgap, since the database uses an inaccurate bandgap method, we adjust the bandgap using an imperical shift to significantly improve it general accuracy (reference leads to method). Screen 3 is the first machine learning screen where we have an adjusted model to find stable materials, this model is built on 1000 materials that have had their water stability determined expermentally, then their CIF files were fingerprinted by ZEO++ (https://www.zeoplusplus.org/) for structural data and RACS (https://doi.org/10.1021/acs.jpca.7b08750) to determine ligand data. The model runs quickly to determine the stability of each material from 0-100, where materials >75 are considered highly stable. Screen 4 uses a deep learning model built by literature mining method (https://doi.org/10.1038/s41597-022-01181-0), for this method since the number of materials has significantly shortened, we can automate a bot to use the web interface to plug and check the remaining materials. The final materials list is determined from materials that pass this final screen.

The 2 additional properties are to check the amount of gas adsorption and to check what temperature the material begins to degrade. The method was developed by using ZEO++ on MOFs with known adsorption properties. The Thermal degradation property is built into the MOF structure stability screen, the data was pulled and added to the spread sheet.

Further Work

I think we do need some sort of energy of adsorption method to put a final check on the materials to ensure that they have the specific ability to preform hydrogenation. Currently I am working on two methods, Nudging Elastic Band DFT using Quantum Espresso (https://pubs.acs.org/doi/10.1021/acscatal.3c03401) and/or Machine learning method to determine the energy requirements for hydrogenation (https://doi.org/10.1007/s43938-023-00031-8). Here I think I need help determine what level of analysis we need.
