from __future__ import annotations

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from analysis.summaries import build_summary_tables, add_roles
from analysis.insights import generate_insights
from analysis.recommendations import generate_recommendations
from analysis.trends import build_time_trends, build_popularity, build_role_theme_matrix
from collectors.file_collector import load_json_records


st.set_page_config(page_title="WoW Class Design Dashboard", layout="wide")


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = load_json_records(path)
    df = add_roles(df)
    df["created_iso"] = pd.to_datetime(df["created_iso"], errors="coerce", utc=True)
    return df


def filter_df(
    df: pd.DataFrame,
    selected_classes: list[str],
    selected_specs: list[str],
    selected_roles: list[str],
    selected_sources: list[str],
) -> pd.DataFrame:
    out = df.copy()

    if selected_classes:
        out = out[out["wow_class"].isin(selected_classes)]
    if selected_specs:
        out = out[out["spec"].isin(selected_specs)]
    if selected_roles:
        out = out[out["role"].isin(selected_roles)]
    if selected_sources:
        out = out[out["source"].isin(selected_sources)]

    return out


def make_sentiment_over_time_chart(trends_df: pd.DataFrame):
    if trends_df.empty:
        return None

    chart_df = trends_df.groupby("month", as_index=False)["avg_sentiment"].mean()
    fig = px.line(
        chart_df,
        x="month",
        y="avg_sentiment",
        markers=True,
        title="Average Sentiment Over Time",
        labels={"month": "Month", "avg_sentiment": "Average Sentiment"},
    )
    fig.update_layout(height=450)
    return fig


def make_popularity_scatter(popularity_df: pd.DataFrame):
    if popularity_df.empty:
        return None

    plot_df = popularity_df.copy()
    plot_df["label"] = plot_df["spec"] + " (" + plot_df["wow_class"] + ")"

    fig = px.scatter(
        plot_df,
        x="mentions",
        y="avg_sentiment",
        text="label",
        hover_data=["wow_class", "spec", "mentions", "avg_sentiment"],
        title="Popularity vs Sentiment by Spec",
        labels={"mentions": "Mentions", "avg_sentiment": "Average Sentiment"},
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(height=550)
    return fig


def make_role_theme_heatmap(role_theme_df: pd.DataFrame):
    if role_theme_df.empty:
        return None

    pivot = role_theme_df.pivot(index="role", columns="themes", values="count").fillna(0)

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=list(pivot.columns),
            y=list(pivot.index),
            text=pivot.values,
            texttemplate="%{text}",
            hovertemplate="Role: %{y}<br>Theme: %{x}<br>Count: %{z}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Role vs Theme Heatmap",
        xaxis_title="Theme",
        yaxis_title="Role",
        height=500,
    )
    return fig


def make_class_sentiment_chart(class_summary: pd.DataFrame):
    if class_summary.empty:
        return None

    plot_df = class_summary.copy()
    fig = px.bar(
        plot_df,
        x="wow_class",
        y="avg_sentiment",
        color="role" if "role" in plot_df.columns else None,
        hover_data=["records", "avg_score"],
        title="Average Sentiment by Class",
        labels={"wow_class": "Class", "avg_sentiment": "Average Sentiment"},
    )
    fig.update_layout(height=450)
    return fig


def make_spec_sentiment_chart(spec_summary: pd.DataFrame):
    if spec_summary.empty:
        return None

    plot_df = spec_summary.copy()
    plot_df["label"] = plot_df["spec"] + " (" + plot_df["wow_class"] + ")"

    fig = px.bar(
        plot_df,
        x="label",
        y="avg_sentiment",
        color="role" if "role" in plot_df.columns else None,
        hover_data=["records", "avg_score"],
        title="Average Sentiment by Spec",
        labels={"label": "Spec", "avg_sentiment": "Average Sentiment"},
    )
    fig.update_layout(height=500, xaxis_tickangle=-45)
    return fig


def main() -> None:
    st.title("WoW Class & Spec Community Analysis Dashboard")

    default_path = "data/blizzard_auto_threads.json"
    input_path = st.sidebar.text_input("Input JSON Path", value=default_path)

    try:
        df = load_data(input_path)
    except Exception as exc:
        st.error(f"Failed to load data: {exc}")
        return

    st.sidebar.header("Filters")

    all_classes = sorted(df["wow_class"].dropna().unique().tolist())
    all_specs = sorted(df["spec"].dropna().unique().tolist())
    all_roles = sorted(df["role"].dropna().unique().tolist())
    all_sources = sorted(df["source"].dropna().unique().tolist())

    selected_classes = st.sidebar.multiselect("Class", all_classes)
    selected_specs = st.sidebar.multiselect("Spec", all_specs)
    selected_roles = st.sidebar.multiselect("Role", all_roles)
    selected_sources = st.sidebar.multiselect("Source", all_sources)

    filtered_df = filter_df(df, selected_classes, selected_specs, selected_roles, selected_sources)

    if filtered_df.empty:
        st.warning("No records match the current filters.")
        return

    summaries = build_summary_tables(filtered_df)
    insights_df = generate_insights(filtered_df, summaries)
    recommendations_df = generate_recommendations(summaries)
    trends_df = build_time_trends(filtered_df)
    popularity_df = build_popularity(filtered_df)
    role_theme_df = build_role_theme_matrix(filtered_df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Records", len(filtered_df))
    c2.metric("Classes", filtered_df["wow_class"].nunique())
    c3.metric("Specs", filtered_df["spec"].nunique())
    c4.metric("Avg Sentiment", round(filtered_df["sentiment"].mean(), 3))

    st.subheader("Top Specs")
    left, right = st.columns(2)
    with left:
        st.markdown("**Most Loved Specs**")
        st.dataframe(summaries["top_loved_specs"], use_container_width=True)
    with right:
        st.markdown("**Most Complained About Specs**")
        st.dataframe(summaries["top_complained_specs"], use_container_width=True)

    st.subheader("Interactive Visuals")

    class_fig = make_class_sentiment_chart(summaries["class_summary"])
    if class_fig:
        st.plotly_chart(class_fig, use_container_width=True)

    spec_fig = make_spec_sentiment_chart(summaries["spec_summary"])
    if spec_fig:
        st.plotly_chart(spec_fig, use_container_width=True)

    trend_fig = make_sentiment_over_time_chart(trends_df)
    if trend_fig:
        st.plotly_chart(trend_fig, use_container_width=True)

    scatter_fig = make_popularity_scatter(popularity_df)
    if scatter_fig:
        st.plotly_chart(scatter_fig, use_container_width=True)

    heatmap_fig = make_role_theme_heatmap(role_theme_df)
    if heatmap_fig:
        st.plotly_chart(heatmap_fig, use_container_width=True)

    st.subheader("Role Summary")
    st.dataframe(summaries["role_summary"], use_container_width=True)

    st.subheader("Design Insights")
    st.dataframe(insights_df, use_container_width=True)

    st.subheader("Design Recommendations")
    st.dataframe(recommendations_df, use_container_width=True)

    st.subheader("Popularity Table")
    st.dataframe(popularity_df, use_container_width=True)

    st.subheader("Role Theme Matrix")
    st.dataframe(role_theme_df, use_container_width=True)

    st.subheader("Raw Data")
    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Filtered Data CSV",
        data=csv,
        file_name="wow_filtered_data.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()