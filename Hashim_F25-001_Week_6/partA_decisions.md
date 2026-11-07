# Task A — decisions

| What | How detected | Rule applied | Rows affected |
|---|---|---|---|
| District 1/4: conflicting D11 duplicate | Repeated code; GeoJSON names Kotla, not Kotla City | Keep the unique row matching authoritative boundary name; drop conflicting alias; do not add values | 1 |
| District 2/4: D21 household scale | 182 yields 5939.56 persons/household; peers roughly 6–7 | Repair 182 to 182000 as inferred thousand-unit error, consistent with demographic range and published total; explicit assumption, not independent verification | 1 |
| District 3/4: mixed percentage strings | Two values end with percent sign; column is text | Strip percent suffix and parse percentage points; preserve three original nulls | 2 |
| District 4/4: duration sentinel | Two negative interruption durations | Replace -1 by missing; retain districts and counts; duration charts omit these two | 2 |
| Daily 1/6: mixed date formats | Regex finds ISO and day/month/year strings | Parse with dayfirst=True; slash block includes days >12, establishing day-first convention | 174 |
| Daily 2/6: shuffled chronology | All six zone timestamp sequences are nonmonotonic | Stable sort by zone and parsed date before differencing or plotting | 3061 |
| Daily 3/6: repeated zone-day keys | 12 exact repeats and 3 conflicting keys (6 candidates); counters agree | Drop 12 exact copies; consolidate 3 conflicting pairs with maximum peak and interruption duration (conservative upper bound, not a claim of true value); retain candidates separately | 15 |
| Daily 4/6: unreported zone-days | Full calendar anti-join shows 128 missing slots | Keep 3046 reported rows; export 128 absent keys separately; reindex plots so gaps remain missing | 128 |
| Daily 5/6: peak-load sentinel | 46 readings have peak -1 MW | Set to missing, never zero; preserve row and other valid measures | 46 |
| Daily 6/6: meter reset | Exactly one negative within-zone counter change: P4 2026-02-17 | Retain meter reading; flag reset; mask crossing interval as unknown; resume differencing thereafter; no invented reset-day energy | 1 |
| Counter semantics | Dictionary defines cumulative reading, not daily flow | Use endpoint changes only across nonreset intervals; gaps give interval energy, never assign it to one day | 3046 |
| Partial final daily month | Last observed day September 11, not month end | Keep raw observations; Task B trend stops at August 31; generation September is a separate published complete-month series | 66 |
| Generation 1/1: total mixed with parts | Each month contains eight leaf categories and an All sources / Total row; all rows double-count energy | Separate 18 total rows from 144 mutually exclusive leaves; verify unique month/source/subsource and reconciliation within 2 MWh | 18 |

The eleven defect kinds are explicitly numbered 4 + 6 + 1. Extra decisions explain semantics and partial periods. Conflict rules are conservative estimates; D21 is an inferred unit correction supported by the supplied validation anchors.
