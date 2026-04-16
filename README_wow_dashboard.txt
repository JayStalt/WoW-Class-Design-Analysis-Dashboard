WoW Retail Reddit Dashboard

Files:
- wow_retail_reddit_dashboard.py : main script
- .env.example : environment variable template

Install:
pip install praw python-dotenv pandas openpyxl matplotlib

Run:
python wow_retail_reddit_dashboard.py --days 120 --limit 60

Optional:
python wow_retail_reddit_dashboard.py --classes "Druid,Evoker" --days 180 --limit 80
