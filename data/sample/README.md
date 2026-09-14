# Synthetic sample dataset

Run `python data/generate_synthetic.py` to materialize `sites.csv`, `patients.csv`, and `visits.csv`: exactly 200 fictional sites, 1,000 fictional participants, and 5,000 fictional visits. The API performs this step automatically on first start. The fixed seed makes the dataset reproducible. It contains no PHI and must never be merged with real clinical data.

