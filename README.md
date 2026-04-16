# WoW Retail Community Dashboard (Two-Phase Version)

This version is built to work **without Reddit API access first**.

## Phase 1
Run the project using local sample discussion data in `data/sample_reddit_posts.json`.

## Phase 2
Later, plug live Reddit collection into `src/collectors/reddit_collector.py` once your Reddit app works.

## Install
```bash
pip install pandas openpyxl matplotlib python-dotenv
```

## Run
```bash
python src/main.py
```

Optional:
```bash
python src/main.py --input data/sample_reddit_posts.json --outdir out
```

## Project Structure
```text
wow_reddit_dashboard_refactor/
├── data/
│   ├── sample_reddit_posts.json
│   └── processed/
├── out/
├── src/
│   ├── collectors/
│   │   ├── file_collector.py
│   │   └── reddit_collector.py
│   ├── analysis/
│   │   ├── sentiment.py
│   │   ├── themes.py
│   │   └── summaries.py
│   ├── dashboard/
│   │   ├── charts.py
│   │   └── excel_export.py
│   └── main.py
└── requirements.txt
```

## Output
- `out/wow_retail_dashboard.xlsx`
- `out/charts/*.png`

## Notes
- Retail-only starter sample data is included.
- Replace the sample JSON with your own exported posts/comments whenever you want.
- Reddit collector is left as a stub on purpose until API access is available.