"""
One-off CSV -> parquet conversion of the extract, so ethos_omop._read loads columns instead of whole CSVs.

    python csv_to_parquet.py [extract_dir]        # default ../../inputs/chest_pain_cohort/

Per table, <table>.parquet is written next to <table>.csv (the CSV is not touched):
  small tables (person, concept, concept_ancestor, death)  every column, through pandas with the
                                                           same read_csv call as _read (same dtypes)
  master_* event tables                                    only the columns the code reads
                                                           (EVENT_SOURCES), streamed in blocks so
                                                           the CSV never sits in memory
Dates stay strings, as in the CSV, so load_events' pd.to_datetime behaves as before.
Run again after every re-extract; a parquet older than its CSV is ignored by _read.
A column that is not in the parquet (a notebook asking _read for more) falls back to the CSV.
"""
import os, sys
import pandas as pd
import pyarrow as pa
import pyarrow.csv as pacsv
import pyarrow.parquet as pq
import ethos_omop as eo

SMALL_TABLES = ["person", "concept", "concept_ancestor", "death"]
TABLES = SMALL_TABLES + [t for t, *_ in eo.EVENT_SOURCES]       # what main() writes; the notebook tests these for freshness


def convert_small(csv, pqt):
    pd.read_csv(csv, low_memory=False).to_parquet(pqt + ".tmp", index=False)


def convert_master(csv, pqt, columns, date_col):
    types = {c: pa.string() if c == date_col else pa.int64() for c in columns}
    rd = pacsv.open_csv(
        csv,
        convert_options=pacsv.ConvertOptions(include_columns=columns, column_types=types,
                                             strings_can_be_null=True),
        read_options=pacsv.ReadOptions(block_size=64 << 20))
    with pq.ParquetWriter(pqt + ".tmp", rd.schema, compression="zstd") as w:
        for batch in rd:
            w.write_batch(batch)


def main(out_dir):
    jobs = [(t, None, None) for t in SMALL_TABLES]
    for table, cid, date, _ in eo.EVENT_SOURCES:
        jobs.append((table, ["person_id", cid, date], date))
    for table, columns, date_col in jobs:
        csv = os.path.join(out_dir, f"{table}.csv")
        pqt = os.path.join(out_dir, f"{table}.parquet")
        if not os.path.exists(csv):
            print(f"skip {table}: no CSV")
            continue
        convert_small(csv, pqt) if columns is None else convert_master(csv, pqt, columns, date_col)
        os.replace(pqt + ".tmp", pqt)                    # a half-written file never looks like a fresh parquet
        print(f"{table}: {os.path.getsize(csv) / 1e6:,.0f} MB csv -> {os.path.getsize(pqt) / 1e6:,.0f} MB parquet, "
              f"{pq.ParquetFile(pqt).metadata.num_rows:,} rows")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../../inputs/chest_pain_cohort/")
