# Week 4 assignment package

1. Extract this ZIP completely.
2. Install Python dependencies: `python -m pip install -r requirements.txt`.
3. Open `Week4_Assignment.ipynb` in Jupyter, VS Code or another notebook editor. Select Python 3 and run all cells from this folder.
4. Fill in your student name/roll number. The original brief requests a ZIP named `W4_<RollNo>.zip`; replace the placeholder with your own roll number.

## What is included

- `Week4_Assignment.ipynb`: executed computational work for Parts A–E, numerical answers, figures and explanations.
- `partA_charts.py`, `partB_windows.py`, `partC_shares.py`, `partD_figure.py`: standalone reproducible scripts.
- `common.py`: documented parsing, cleaning, auditing and export helpers.
- `partA_diagnosis.pdf`: nine pages; one diagnosis and both charts per case.
- `partE_justification.pdf`: one page, with editable Markdown copy.
- `outputs/`: 300 dpi figures, printed script output, all 60 sensitivity fits, index/cleaning audit, hierarchy reconciliation, negative SKUs, cleaned daily values and reader-results CSV.
- `originals/`: all 17 supplied files unchanged, including original toolkit filenames and assignment instructions.
- `data/`: all 12 CSV inputs under runnable names.
- `tslib.py`, `vizlib.py`: original toolkits, unchanged in content.

## Required human step — Part C

The assignment expressly requires a real reader and forbids invented responses. Both rows in `outputs/pie_ranking_results.csv` are marked `pending_real_reader`, with blank timings and responses. Do not submit those as observed results.

Use the final interactive cell in the notebook with a reader who has not seen the values. Set `RUN_REAL_READER = True`. It times, records and scores both responses, reports wrong rank positions and discusses limitations. After collecting the responses, save the notebook and re-zip the folder. No fake participant data is included.

## Declared limitations and choices

- Annual `seasonal_decompose(period=365)` is attempted and rejected because 518 days are available, fewer than the required 730. The notebook explains the expected interpretation without manufacturing an annual result.
- Optional Part F (5 bonus marks, separate from the required 100) is not attempted.
- All source data are synthetic, generated for CDB601220, Superior University Lahore.
- Slash timestamps are day-first; mixed-format auto-inference is deliberately avoided.
- Missing logger hours remain missing. Internal sentinel hours are linearly estimated and affected daily totals are marked. The raw dataset is preserved.
- The last partial month is excluded only from temporal analyses; catalogue totals cover the entire extract, as its rows cannot be split by date.
- Part B.5 defines the otherwise ambiguous start/window grid: April 2024–March 2025 start months, common end 31 August 2025, centered rolling windows 7/14/28/56/91 with minimum half-window support. Counts are conditional on this declared convention.
- Jupyter kernel networking is unavailable in the build environment. Every notebook code cell was instead executed sequentially in the same Python namespace with genuine stdout/figure capture. The notebook is valid nbformat 4 and runs as normal in Jupyter; no outputs are invented.

## Script alternative

Run `python run_all.py`. This regenerates analytical outputs and PDFs without collecting human responses or overwriting observed reader results. The notebook remains the primary assignment deliverable.
