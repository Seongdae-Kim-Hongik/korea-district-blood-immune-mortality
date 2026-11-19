# District geography of deaths from anemias and immune disorders, Republic of Korea, 2011-2025

Analysis code for the manuscript

> Kim S. *Is the excess of deaths from anemias and immune disorders in Busan, Korea, explained by anemia burden, deprivation or care?* Manuscript under review.

Archived version: Zenodo, https://doi.org/10.5281/zenodo.24366493 (v1.0.0).

## Contents

This repository contains code only. The processed district-year data (analytic panel, expected deaths, result tables, adjacency graph and boundary file) are not included; they are available from the author on reasonable request. All source statistics are public (see Data sources).

| Path | What it is |
|---|---|
| `01_스크립트/` | Analysis scripts (below) |
| `04_분석/BLDD/sets_BLDD_std3_main.json`, `sets_BLDD_sens_g577.json`, `sets_BLDD_sens_no80.json`, `sets_BLDD_sens_crude.json`, `sets_BLDD_sens_y24.json`, `config_BLDD_std3_main.json`, `run_chain.sh`, `run_post.sh` | Covariates with expected directions, forced controls, negative controls, comparison outcomes and model settings (principal model; sensitivity versions with the queen contiguity graph, without the share aged 80 or older, with crude expected deaths and restricted to 2011-2024) |
| `04_분석/BLDD/MS/` | Scripts that read the result tables and write every number, table and figure in the manuscript and supplementary material, including `content_bldd.py`, which generates the Methods and Results text (the draft source of the Introduction and Discussion is not included) |

Folder and some column names are in Korean because the source tables are Korean; each script has a header comment describing its inputs and outputs.

## Data sources

All inputs are public, aggregated statistics. No individual-level data are included.

- Deaths by underlying cause (diseases of the blood and blood-forming organs and certain disorders involving the immune mechanism, ICD-10 D50-D89; all causes) by district of residence: Statistics Korea, cause-of-death statistics (KOSIS DT_1B34E13), 2011-2025.
- National deaths by cause, sex and 5-year age group (to 85 years or older): Statistics Korea (KOSIS DT_1B34E01), fetched by `34_fetch_national_cause_age_deaths.py` and `55N_bldd_fetch_national_2025.py` (requires a personal KOSIS API key in `~/.kosis_key`; the key is not included).
- Population by sex and 5-year age group: Ministry of the Interior and Safety, resident registration statistics (2011-2024 files; December 2025 table for 2025). The 2023 age block of Changwon duplicated the 2022 block and was corrected.
- District covariates: national general health screening (suspected anaemia, suspected kidney disease), a harmonised public district panel (basic livelihood security recipients with corrected cells, tertiary education, long-term care hospitals, internal-medicine specialists, ill-defined causes of death), the Community Health Survey (unmet medical need) and Korean Statistical Information Service local indicators (forced and negative controls). Values not published for 2025 carry their 2024 values (rule table written by `99c_extra_canonical_pool_bldd.py`).

## Pipeline

Run from the repository root (set `ST_DATA_ROOT`, `ST_FBDZIP_CORRECTED` and `ST_GPT_DATASET` to the local copies of the public source files and the read-only district database).

| Step | Script | Output |
|---|---|---|
| 0 | `34_fetch_national_cause_age_deaths.py`, `55N_bldd_fetch_national_2025.py`, `99R_next5c_mort_counts.py`, `99R_next5c_mort_E.py` (use `50_build_master_panel.py`, `40_region_crosswalk.py`) | National cause-by-age deaths; district counts and sex-by-age expected deaths, 2011-2024 |
| 1 | `55E_bldd_Estd_2025.py` | District counts and expected deaths, 2011-2025 |
| 2 | `99c_extra_canonical_pool_bldd.py`; `55D_bldd_national.py` | District characteristics joined by district code; national rates by sex and age |
| 3 | `80_build_disease_panel_v.py BLDD` (`ST_VER=std3_main`) | Analytic panel |
| 4 | `81_fit_inla.R BLDD` (`ST_GRAPH=04_분석/BLDD/graph_593.graph`, `ST_THREADS=1`); `55K_bldd_likelihood.R` | Principal model, set comparison, 200-subset multiverse, window models; likelihood comparison |
| 5 | `85_window_maps.R`, `86_yearly_maps_ehsa_bldd.py`, `86b_ehsa_modified_mk.py`, `87_window_grid.py` | Period maps, yearly smoothed ratios, persistence and emerging hot spot analysis |
| 6 | `88g_sens_prep.py BLDD std3_main TRANS,GCA`, `88g_sens_suite.R` (`GROUP=1..6`), `88h_ppc_varpart.R`, `88k_struct_kh_bldd.R` (nb, struct, kh, review) with `kh_constraints_bldd.R`, `89g_sens_combine.py` | Sensitivity analyses, comparison outcomes, Knorr-Held models |
| 7 | `04_분석/BLDD/MS/build/run_all_bldd.sh` | Manuscript, supplementary material, figures and checks |

The boundary file is found at `data/boundary/final.shp` by default; set `ST_SHP` to use another path.

## Software

R 4.6.0 with R-INLA 25.10.19, spdep and sf; Python 3.9 with pandas, geopandas, numpy, scipy, matplotlib and python-docx.

## Licence

MIT (see `LICENSE`).
