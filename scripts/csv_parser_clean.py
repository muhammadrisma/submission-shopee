import gc
import os
from typing import Any, Dict, Iterator

import pandas as pd


class CSVParser:

    def __init__(self, chunk_size: int = 10000):
        self.chunk_size = chunk_size

    def get_file_size_mb(self, filepath: str) -> float:
        return os.path.getsize(filepath) / (1024 * 1024)

    def parse_small_csv(self, filepath: str) -> pd.DataFrame:
        print(f"Parsing small CSV: {filepath}")
        file_size = self.get_file_size_mb(filepath)
        print(f"File size: {file_size:.2f} MB")

        df = pd.read_csv(filepath)
        print(f"Loaded {len(df):,} rows with {len(df.columns)} columns")

        return df

    def parse_large_csv_chunked(self, filepath: str) -> Iterator[pd.DataFrame]:
        """
        For large files like customers-2000000.csv, this method would process
        the file in chunks to keep memory usage low
        """
        print(f"Parsing large CSV with chunking: {filepath}")
        file_size = self.get_file_size_mb(filepath)
        print(f"File size: {file_size:.2f} MB")
        print(f"Chunk size: {self.chunk_size:,} rows")

        chunk_reader = pd.read_csv(filepath, chunksize=self.chunk_size)

        chunk_count = 0
        total_rows = 0

        for chunk in chunk_reader:
            chunk_count += 1
            total_rows += len(chunk)
            print(f"Processing chunk {chunk_count}: {len(chunk):,} rows")

            yield chunk

            gc.collect()

        print(f"Processed {total_rows:,} total rows in {chunk_count} chunks")

    def get_data_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        insights = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 * 1024),
            "null_counts": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.to_dict(),
        }

        if "Country" in df.columns:
            insights["top_countries"] = df["Country"].value_counts().head(5).to_dict()

        if "Subscription Date" in df.columns:
            df["Subscription Date"] = pd.to_datetime(df["Subscription Date"])
            insights["date_range"] = {
                "earliest": df["Subscription Date"].min().strftime("%Y-%m-%d"),
                "latest": df["Subscription Date"].max().strftime("%Y-%m-%d"),
            }

        return insights


def analyze_small_csv():
    print("=" * 60)
    print("ANALYZING SMALL CSV FILE")
    print("=" * 60)

    parser = CSVParser()

    df = parser.parse_small_csv("data/customers-100000.csv")

    insights = parser.get_data_insights(df)

    print("\nDATA INSIGHTS:")
    print(f"Total rows: {insights['row_count']:,}")
    print(f"Total columns: {insights['column_count']}")
    print(f"Memory usage: {insights['memory_usage_mb']:.2f} MB")
    print(
        f"Date range: {insights['date_range']['earliest']} to {insights['date_range']['latest']}"
    )

    print("\nTop 5 Countries:")
    for country, count in insights["top_countries"].items():
        print(f"  {country}: {count:,}")

    print("\nColumn Info:")
    for col in insights["columns"][:5]:
        print(f"  {col}")

    return df


def demonstrate_chunking():
    """
    This demonstrates chunking on the 100k file. For a real 2M+ record file
    like customers-2000000.csv, chunking would be essential to prevent
    out-of-memory errors
    """
    print("\n" + "=" * 60)
    print("DEMONSTRATING CHUNKING ON SAME FILE")
    print("=" * 60)

    parser = CSVParser(chunk_size=25000)

    total_rows = 0
    country_counts = {}
    earliest_date = None
    latest_date = None

    for chunk_num, chunk in enumerate(
        parser.parse_large_csv_chunked("data/customers-100000.csv"), 1
    ):

        chunk_insights = parser.get_data_insights(chunk)

        total_rows += chunk_insights["row_count"]

        for country, count in chunk_insights["top_countries"].items():
            country_counts[country] = country_counts.get(country, 0) + count

        chunk_earliest = pd.to_datetime(chunk_insights["date_range"]["earliest"])
        chunk_latest = pd.to_datetime(chunk_insights["date_range"]["latest"])

        if earliest_date is None or chunk_earliest < earliest_date:
            earliest_date = chunk_earliest
        if latest_date is None or chunk_latest > latest_date:
            latest_date = chunk_latest

    print("\nAGGREGATED INSIGHTS FROM CHUNKING:")
    print(f"Total rows processed: {total_rows:,}")
    print(
        f"Date range: {earliest_date.strftime('%Y-%m-%d')} to {latest_date.strftime('%Y-%m-%d')}"
    )

    top_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    print("\nTop 5 Countries (aggregated):")
    for country, count in top_countries:
        print(f"  {country}: {count:,}")


def explain_differences():
    print("\n" + "=" * 60)
    print("SMALL vs LARGE FILE PROCESSING DIFFERENCES")
    print("=" * 60)

    differences = [
        {
            "aspect": "Memory Usage",
            "small_file": "Loads entire file into RAM at once",
            "large_file": "Processes small chunks, keeps memory usage low",
        },
        {
            "aspect": "Processing Speed",
            "small_file": "Faster - single read operation",
            "large_file": "Slower - multiple read operations, but prevents crashes",
        },
        {
            "aspect": "Memory Footprint",
            "small_file": "High - entire dataset in memory",
            "large_file": "Low - only current chunk in memory",
        },
        {
            "aspect": "Data Analysis",
            "small_file": "Can perform complex operations on full dataset",
            "large_file": "Requires aggregation across chunks",
        },
        {
            "aspect": "Error Handling",
            "small_file": "Fails completely if file too large",
            "large_file": "Can handle files larger than available RAM",
        },
        {
            "aspect": "Use Case",
            "small_file": "Files < 100MB, sufficient RAM available",
            "large_file": "Files > 100MB, limited RAM, or very large datasets",
        },
    ]

    for diff in differences:
        print(f"\n{diff['aspect']}:")
        print(f"  Small File: {diff['small_file']}")
        print(f"  Large File: {diff['large_file']}")


if __name__ == "__main__":
    print("CSV Parser - Memory Efficient Processing Demo")
    small_df = analyze_small_csv()
    demonstrate_chunking()
    explain_differences()
    print("\nAnalysis complete!")
