from __future__ import annotations

import argparse
from pathlib import Path
from datetime import datetime

from analysis.summaries import build_summary_tables
from analysis.insights import generate_insights
from analysis.recommendations import generate_recommendations
from analysis.trends import build_time_trends, build_popularity, build_role_theme_matrix
from collectors.file_collector import load_json_records
from dashboard.charts import make_charts
from dashboard.excel_export import write_excel



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the WoW retail discussion dashboard from local JSON data.")
    parser.add_argument("--input", default="data/sample_reddit_posts.json", help="Path to local JSON input")
    parser.add_argument("--outdir", default="out", help="Output directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outdir = Path(args.outdir)
    charts_dir = outdir / "charts"
    outdir.mkdir(parents=True, exist_ok=True)

    df = load_json_records(args.input)
    summaries = build_summary_tables(df)
    insights_df = generate_insights(df, summaries)
    recommendations_df = generate_recommendations(summaries)
    chart_paths = make_charts(df, summaries, charts_dir)
    trends_df = build_time_trends(df)
    popularity_df = build_popularity(df)
    role_theme_df = build_role_theme_matrix(df)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    workbook_path = outdir / f"wow_retail_dashboard_{timestamp}.xlsx"

    write_excel(
        workbook_path,
        df,
        summaries,
        chart_paths,
        insights_df,
        recommendations_df,
        trends_df,
        popularity_df,
        role_theme_df
    )

    print("Done.")
    print(f"Workbook: {workbook_path}")
    print(f"Charts:   {charts_dir}")


if __name__ == "__main__":
    main()