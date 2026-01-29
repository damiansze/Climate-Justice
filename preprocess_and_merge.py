from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np


YEAR_START = 1995
YEAR_END = 2023  # inkl.


def get_year_columns(df: pd.DataFrame) -> list[str]:
    """Return year columns (as strings) that look like digits, e.g. '1995'."""
    cols = []
    for c in df.columns:
        s = str(c).strip()
        if s.isdigit():
            cols.append(s)
    # Normalize to strings
    # (in case years were ints in columns, we keep them as strings downstream)
    return sorted(cols, key=lambda x: int(x))


def _ensure_year_cols_numeric(df: pd.DataFrame, year_cols: list[str]) -> pd.DataFrame:
    """Coerce year columns to numeric (NaN if not parseable)."""
    df = df.copy()
    for c in year_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _combine_two_countries_mean(
    df: pd.DataFrame,
    iso_col: str,
    name_col: str,
    iso_a: str,
    iso_b: str,
    new_iso: str,
    new_name: str,
) -> pd.DataFrame:
    """
    Combine iso_a and iso_b into new_iso by averaging all year columns.
    Removes iso_a and iso_b, appends new row.
    """
    df = df.copy()

    # Normalize ISO codes
    df[iso_col] = df[iso_col].astype(str).str.strip()

    year_cols = get_year_columns(df)
    df = _ensure_year_cols_numeric(df, year_cols)

    a = df[df[iso_col] == iso_a]
    b = df[df[iso_col] == iso_b]

    if a.empty or b.empty:
        raise ValueError(
            f"Cannot combine {iso_a} and {iso_b} -> {new_iso}: "
            f"missing rows: {iso_a}={len(a)}, {iso_b}={len(b)}"
        )

    # Take first row as template
    new_row = a.iloc[[0]].copy()
    new_row.loc[:, iso_col] = new_iso
    new_row.loc[:, name_col] = new_name

    # Average year cols (row-wise mean between the two rows)
    # (keeps NaN if both NaN; if one exists and one NaN -> mean becomes NaN, same as your original code)
    for c in year_cols:
        new_row.loc[:, c] = (a[c].values[0] + b[c].values[0]) / 2

    df = df[~df[iso_col].isin([iso_a, iso_b])]
    df = pd.concat([df, new_row], ignore_index=True)
    return df


def clean_data(
    ghg_capita_df: pd.DataFrame,
    gain_df: pd.DataFrame,
    gdp_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Implements your step 5 (Bereinigung).
    """
    ghg = ghg_capita_df.copy()
    gain = gain_df.copy()
    gdp = gdp_df.copy()

    # Normalize code columns
    ghg["EDGAR Country Code"] = ghg["EDGAR Country Code"].astype(str).str.strip()
    gain["ISO3"] = gain["ISO3"].astype(str).str.strip()
    gdp["ISO3"] = gdp["ISO3"].astype(str).str.strip()

    # 1) KNA entfernen
    ghg = ghg[ghg["EDGAR Country Code"] != "KNA"]
    gain = gain[gain["ISO3"] != "KNA"]
    gdp = gdp[gdp["ISO3"] != "KNA"]

    # 2) SRB + MNE -> SCG (jeweils gemittelt)
    gain = _combine_two_countries_mean(
        gain, iso_col="ISO3", name_col="Name",
        iso_a="SRB", iso_b="MNE",
        new_iso="SCG", new_name="Serbia and Montenegro"
    )
    gdp = _combine_two_countries_mean(
        gdp, iso_col="ISO3", name_col="Name",
        iso_a="SRB", iso_b="MNE",
        new_iso="SCG", new_name="Serbia and Montenegro"
    )

    # 3) AND, LIE, MCO, SMR aus ND-GAIN und GDP löschen
    remove_small = ["AND", "LIE", "MCO", "SMR"]
    gain = gain[~gain["ISO3"].isin(remove_small)]
    gdp = gdp[~gdp["ISO3"].isin(remove_small)]

    # 3b) Länder im GHG umbenennen (nur Country-Name; Codes bleiben gleich)
    country_renames = {
        "France and Monaco": "France",
        "Italy, San Marino and the Holy See": "Italy",
        "Spain and Andorra": "Spain",
        "Switzerland and Liechtenstein": "Switzerland",
    }
    ghg = ghg.copy()
    ghg["Country"] = ghg["Country"].replace(country_renames)

    # 4) EU27 und GLOBAL TOTAL entfernen
    ghg = ghg[~ghg["EDGAR Country Code"].isin(["EU27", "GLOBAL TOTAL"])]

    # 5) PRK und CUB im GDP auf NaN setzen (alle Jahr-Spalten)
    gdp_year_cols = get_year_columns(gdp)
    gdp = _ensure_year_cols_numeric(gdp, gdp_year_cols)
    for iso_code in ["PRK", "CUB"]:
        mask = gdp["ISO3"] == iso_code
        gdp.loc[mask, gdp_year_cols] = np.nan

    # 6) NRU, FSM, TUV, MHL aus ND-GAIN und GDP löschen
    remove_no_ghg = ["NRU", "FSM", "TUV", "MHL"]
    gain = gain[~gain["ISO3"].isin(remove_no_ghg)]
    gdp = gdp[~gdp["ISO3"].isin(remove_no_ghg)]

    # 7) Länder nur in GHG entfernen
    countries_only_in_ghg = {
        "VGB", "HKG", "NCL", "PRI", "PYF", "MAC", "SHN", "CYM", "GIB", "SPM",
        "COK", "GLP", "MTQ", "BMU", "GUF", "FRO", "TWN", "ESH", "TCA", "ABW",
        "FLK", "ANT", "GRL", "AIA", "REU",
    }
    ghg = ghg[~ghg["EDGAR Country Code"].isin(countries_only_in_ghg)]

    return ghg.reset_index(drop=True), gain.reset_index(drop=True), gdp.reset_index(drop=True)


def to_long_format(
    df: pd.DataFrame,
    id_vars: list[str],
    value_name: str,
    years_to_keep: list[str],
) -> pd.DataFrame:
    """Melt wide year columns to long format with 'Year' int column."""
    cols = [c for c in df.columns if str(c).strip() in years_to_keep]
    long_df = df.melt(
        id_vars=id_vars,
        value_vars=cols,
        var_name="Year",
        value_name=value_name,
    )
    long_df["Year"] = long_df["Year"].astype(int)
    return long_df


def build_merged_df(
    data_dir: str | Path = "data",
    year_start: int = YEAR_START,
    year_end: int = YEAR_END,
) -> pd.DataFrame:
    """
    Loads raw CSVs, cleans them, melts to long, merges, sorts, and returns merged_df.
    """
    data_dir = Path(data_dir)

    ghg_capita_df = pd.read_csv(data_dir / "EDGAR_GHG_per_capita.csv")
    gain_df = pd.read_csv(data_dir / "gain.csv")
    gdp_df = pd.read_csv(data_dir / "gdp_input.csv")

    ghg, gain, gdp = clean_data(ghg_capita_df, gain_df, gdp_df)

    years_to_keep = [str(y) for y in range(year_start, year_end + 1)]

    # GHG long
    ghg_long = to_long_format(
        ghg,
        id_vars=["EDGAR Country Code", "Country"],
        value_name="GHG_per_capita",
        years_to_keep=years_to_keep,
    ).rename(columns={"EDGAR Country Code": "ISO3"})

    # GAIN long
    gain_long = to_long_format(
        gain,
        id_vars=["ISO3", "Name"],
        value_name="ND_GAIN",
        years_to_keep=years_to_keep,
    )

    # GDP long
    gdp_long = to_long_format(
        gdp,
        id_vars=["ISO3", "Name"],
        value_name="GDP_per_capita",
        years_to_keep=years_to_keep,
    )

    # Merge: GHG as base (Country names from GHG)
    merged_df = ghg_long.merge(
        gain_long[["ISO3", "Year", "ND_GAIN"]],
        on=["ISO3", "Year"],
        how="left",
    ).merge(
        gdp_long[["ISO3", "Year", "GDP_per_capita"]],
        on=["ISO3", "Year"],
        how="left",
    )

    merged_df = merged_df.sort_values(["ISO3", "Year"]).reset_index(drop=True)
    return merged_df


def build_and_save_merged_df(
    data_dir: str | Path = "data",
    output_csv: str | Path | None = None,
    year_start: int = YEAR_START,
    year_end: int = YEAR_END,
) -> pd.DataFrame:
    """
    Convenience wrapper: builds merged_df and writes it to data/merged_df.csv (default).

    - Builds the merged dataset for the given year range
    - Writes the result to CSV (default: data/merged_df.csv)
    - Ensures the output directory exists
    - Returns the merged DataFrame for further use

    """
    data_dir = Path(data_dir)
    if output_csv is None:
        output_csv = data_dir / "merged_df.csv"
    else:
        output_csv = Path(output_csv)

    merged_df = build_merged_df(data_dir=data_dir, year_start=year_start, year_end=year_end)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    merged_df.to_csv(output_csv, index=False)
    return merged_df


def main() -> None:
    merged_df = build_and_save_merged_df(data_dir="data")
    print("✅ merged_df gespeichert unter: data/merged_df.csv")
    print(f"Shape: {merged_df.shape}")
    print(merged_df.head(5))


if __name__ == "__main__":
    main()
