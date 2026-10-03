import json, sys
sys.path.insert(0, "scripts")
from acceptance_times import pubmed_times, crossref_times, summarize
PUBMED2 = {
 "Science of the Total Environment (Elsevier)": "Sci Total Environ",
 "Journal of Hazardous Materials (Elsevier)": "J Hazard Mater",
 "Environmental Research (Elsevier)": "Environ Res",
 "Water Research (Elsevier)": "Water Res",
 "Environment International (Elsevier)": "Environ Int",
 "Environmental Pollution (Elsevier)": "Environ Pollut",
 "Chemosphere (Elsevier)": "Chemosphere",
 "Journal of Environmental Management (Elsevier)": "J Environ Manage",
 "Bioresource Technology (Elsevier)": "Bioresour Technol",
 "Food Chemistry (Elsevier)": "Food Chem",
 "Talanta (Elsevier)": "Talanta",
 "Analytica Chimica Acta (Elsevier)": "Anal Chim Acta",
 "Spectrochim Acta A (Elsevier)": "Spectrochim Acta A Mol Biomol Spectrosc",
 "Biosensors and Bioelectronics (Elsevier)": "Biosens Bioelectron",
 "Scientific Reports (Springer Nature)": "Sci Rep",
 "iScience (Cell Press)": "iScience",
 "PLoS Computational Biology (PLOS)": "PLoS Comput Biol",
 "BMC Bioinformatics (Springer Nature)": "BMC Bioinformatics",
 "Nucleic Acids Research (OUP)": "Nucleic Acids Res",
 "Ecotoxicology and Environmental Safety (Elsevier)": "Ecotoxicol Environ Saf",
 "Environmental Science & Technology (ACS)": "Environ Sci Technol",
 "Journal of Translational Medicine (Springer Nature)": "J Transl Med",
 "Int J Biological Macromolecules (Elsevier)": "Int J Biol Macromol",
 "Computational Biology and Chemistry (Elsevier)": "Comput Biol Chem",
 "Ultrasonics Sonochemistry (Elsevier)": "Ultrason Sonochem",
 "Physica Medica (Elsevier)": "Phys Med",
}
res = {}
for n, ta in PUBMED2.items():
    try:
        res[n] = {"source": "PubMed history (received->accepted)", **summarize(pubmed_times(ta))}
    except Exception as e:
        res[n] = {"error": str(e)}
    print(n, res[n], flush=True)
json.dump(res, open("acceptance_times_round2.json", "w"), indent=2)
