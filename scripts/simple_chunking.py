import os
import pandas as pd

def process_small_csv():
    print("Processing small CSV (customers-100000.csv)...")
    
    df = pd.read_csv('data/customers-100000.csv')
    
    print(f"Loaded {len(df):,} rows")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    country_stats = df['Country'].value_counts().head(3)
    print("Top 3 countries:", country_stats.to_dict())
    
    return df

def process_csv_chunked():
    """
    For large files like customers-2000000.csv, chunking would be essential
    to process 2M+ records without running out of memory
    """
    print("\nProcessing same CSV with chunking for demonstration...")
    
    chunk_size = 25000
    country_counts = {}
    total_rows = 0
    
    for chunk_num, chunk in enumerate(pd.read_csv('data/customers-100000.csv', chunksize=chunk_size), 1):
        
        total_rows += len(chunk)
        chunk_memory = chunk.memory_usage(deep=True).sum() / 1024**2
        
        print(f"Chunk {chunk_num}: {len(chunk):,} rows, {chunk_memory:.2f} MB")
        
        chunk_countries = chunk['Country'].value_counts()
        for country, count in chunk_countries.items():
            country_counts[country] = country_counts.get(country, 0) + count
    
    print(f"\nTotal processed: {total_rows:,} rows")
    
    top_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    print("Top 3 countries:", dict(top_countries))


def compare_approaches():
    """
    For comparison: customers-2000000.csv would be ~330MB and require
    chunking to avoid memory issues on most systems
    """
    file_size = os.path.getsize('data/customers-100000.csv') / 1024**2
    
    print(f"\nFile size: {file_size:.2f} MB")
    print("\n" + "="*50)
    print("KEY DIFFERENCES:")
    print("Small file approach: Load all data at once")
    print("  - Faster processing")
    print("  - Higher memory usage")
    print("  - Risk of out-of-memory on large files")
    print("\nChunking approach: Process data in pieces")
    print("  - Slower processing")
    print("  - Lower memory usage")
    print("  - Can handle files larger than available RAM")
    print("  - Requires aggregation for final results")
    print("="*50)

if __name__ == "__main__":
    compare_approaches()
    process_small_csv()
    process_csv_chunked()
    print("\nDemonstration complete!")