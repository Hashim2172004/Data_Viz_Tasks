# Week 3 assignment - Matplotlib and Seaborn

Open **W3_Assignment.ipynb**. It contains all completed Parts A-E, code, executed outputs, original charts, redesigns, audits and appendix figures.

All data are synthetic and were supplied for CDB601220 Week 3. No results are real clinical or policy evidence. The optional five-classmate experiment was not completed because no participant observations were supplied; the original optional starter is included without invented timings.

## Reproduce
1. Extract this ZIP, retaining the folder structure.
2. In the extracted folder: `python -m pip install -r requirements.txt`.
3. Open the notebook in Jupyter or VS Code, select its Python kernel and Run All.
   Alternatively: `python run_all.py` regenerates every result and PDF.

The notebook uses a headless Matplotlib backend and displays exported images explicitly, so saved output is consistent across notebooks and scripts. Every chart is saved before display, at 300 dpi. Each figure starts with `plt.subplots`; the only dual-axis figure is the explicitly required misleading reconstruction in A7, never an honest redesign.

Required submission scripts, Part A diagnosis PDF, Part B output, Part C swatches, Part D PNG and script, and the one-page Part E PDF are included alongside all source data and original starters. Root PNGs are copies of their `figures/` counterparts. `outputs/` contains CSV audits, pairwise sample sizes, cleaned data, long-form LOS and printed output. No whole clinical rows are deleted; invalid cells and panel-specific exclusions are disclosed.

The brief's case-9 “4.4%” headline is inconsistent with these supplied SpO2 values under the default Scott KDE: the numerical integral is 1.565%. The notebook shows the calculation and retains the physical-boundary diagnosis rather than inventing a matching value.

Roll number was not provided. Rename the ZIP to `W3_<YourRollNo>.zip` before LMS submission.

## Sources and references
The actual sources used are the supplied TASKS.md, data/DATA_DICTIONARY.md, the supplied CSV files, vizlib.py, and starter code. The CVD model and course distance thresholds are implemented and documented in vizlib.py (Machado, Oliveira & Fernandes, 2009; OKLab). Quartet and matched-shape provenance is given in TASKS.md (Anscombe, 1973; Matejka & Fitzmaurice, 2017). No external source was used to supply or alter data.
