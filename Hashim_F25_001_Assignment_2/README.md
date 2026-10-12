# Week 2 — Visual Perception assignment

## Contents
- task1.ipynb through task5.ipynb: executed Python notebooks with chart outputs and explanations.
- data/: all eight supplied CSV files, unchanged.
- figures/: exports at 300 DPI, including perception_redesign.png.
- results/: blank human-study response sheets, not invented measurements.
- TASKS.md and download_assignment_data.py: original brief and supplied preparation script (seed 42 unchanged).

## Run
Extract the ZIP first. Open a terminal in this folder:

    pip install -r requirements.txt
    jupyter notebook

Open each notebook and choose Run All. Data is already included; no downloads are required.

## Required human work before submission
The assignment requires real observations. These cannot honestly be supplied by an automated assistant.
1. Task 1: run the real-reader widget (18 trials), then rerun the response-time/slopes cell. Add a personal example of a conjunction-search chart you actually made.
2. Task 2: show panels separately, collect group counts/reasons, save actual answers, and write which principle won the conflict.
3. Task 4: run all 30 shuffled trials with a real reader, then rerun error/ranking cells. Write observed agreements/reversals.
4. Task 5: show only the redesign to an unfamiliar reader and save their exact one-sentence reading and your assessment.
5. Save each notebook with the updated outputs. Do not submit blank response sheets as completed experiments.

The widgets save into results/. No notebook waits for input during Run All. Clicking the first trial starts a new session; the widgets can overwrite the same trial rows, so finish a session before restarting. Trial 1 timing includes browser/kernel/render delay; use one machine and interpret slopes cautiously. The source request says 18 search trials but specifies cells requiring 30; the documented 18-trial selection uses set sizes 9, 25, 49.

No experiment results were fabricated. Static analysis and design work are complete; measured conclusions are explicitly pending. The historical Gapminder data ends in 2007.
