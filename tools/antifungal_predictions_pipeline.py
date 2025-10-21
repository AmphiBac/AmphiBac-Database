#!/usr/bin/env python3
"""
Unified AmphiBac Antifungal Prediction Pipeline (multi-mode, version-aware)
--------------------------------------------------------------------------

This pipeline automates antifungal prediction using the AmphiBac reference
database hosted on GitHub. It supports multiple prediction subsets (full,
inhibitory, inhibitory_strict, facilitating) for a given database version.

Main workflow:
  1. Pull or update AmphiBac database from GitHub.
  2. Locate versioned QZA files within AmphiBac-<version>/qza/.
  3. Run QIIME2 closed-reference clustering for selected database subsets.
  4. Summarize total, proportion, and richness per sample.
  5. Merge results into user metadata for each subset.
  6. Optionally combine all results into a single summary table.

Author: Molly Bletz supported by ChatGPT (GPT-5)
Date: 2025-10-17
"""

import os
import subprocess
import pandas as pd
from pathlib import Path
import argparse
import tempfile
import shutil

# -------------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------------

def run_cmd(cmd, desc=None):
    """Run a shell command with a description and error checking."""
    if desc:
        print(f"\n- {desc}")
    print(">>>", " ".join(cmd))
    res = subprocess.run(cmd, text=True, capture_output=True)
    if res.returncode != 0:
        print(res.stderr)
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return res


def ensure_dir(path):
    """Ensure a directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)


def find_ref_qza(repo_dir, db_version, mode):
    """
    Locate the correct reference .qza file in the AmphiBac GitHub repo based on:
      - database version (e.g., 2025.1)
      - mode (full, inhibitory, inhibitory_strict, facilitating)
    """
    version_dir = Path(repo_dir) / f"AmphiBac-{db_version}" / "qza"

    if not version_dir.exists():
        raise FileNotFoundError(f" Could not find version directory: {version_dir}")

    name_map = {
        "full": f"AmphibBac_FullDatabase_{db_version}.qza",
        "inhibitory": f"AmphibBac_Inhibitory_{db_version}.qza",
        "inhibitory_strict": f"AmphibBac_InhibitoryStrict_{db_version}.qza",
        "facilitating": f"AmphibBac_Facilitating_{db_version}.qza"
    }

    if mode not in name_map:
        raise ValueError(f"Invalid mode '{mode}'. Must be one of: {list(name_map.keys())}")

    ref_path = version_dir / name_map[mode]
    if not ref_path.exists():
        raise FileNotFoundError(f" Could not find reference QZA for mode '{mode}': {ref_path}")

    return ref_path


# -------------------------------------------------------------------------
# Prediction workflow per mode
# -------------------------------------------------------------------------

def run_prediction(args, mode, ref_qza):
    """
    Run antifungal prediction for one subset (mode):
      - full
      - inhibitory
      - inhibitory_strict
      - facilitating
    """
    qiime_env = args.qiime_env
    qiime_cmd = ["conda", "run", "-n", qiime_env, "qiime"]

    output_dir = Path(args.output_dir).resolve() / mode
    work_dir = output_dir / "intermediate"
    metadata_dir = output_dir / "metadata"
    for d in [output_dir, work_dir, metadata_dir]:
        ensure_dir(d)

    print(f"\n Running prediction for mode: {mode.upper()}")

    # Step 1 — Filter representative sequences
    filt_repset = work_dir / f"filtered_rep_seqs_{mode}.qza"
    run_cmd(qiime_cmd + [
        "feature-table", "filter-seqs",
        "--i-table", args.otu_table,
        "--i-data", args.rep_seqs,
        "--p-no-exclude-ids",
        "--o-filtered-data", str(filt_repset)
    ], desc=f"Filtering representative sequences ({mode})")

    # Step 2 — Closed-reference clustering
    match_dir = work_dir / f"{mode}_Matches"
    
    # QIIME2 requires the output dir NOT to exist — delete it if present
    if match_dir.exists():
        print(f"  Removing existing QIIME output directory: {match_dir}")
        shutil.rmtree(match_dir)

    run_cmd(qiime_cmd + [
        "vsearch", "cluster-features-closed-reference",
        "--i-sequences", str(filt_repset),
        "--i-table", args.otu_table,
        "--i-reference-sequences", str(ref_qza),
        "--p-perc-identity", str(args.identity),
        "--p-strand", "both",
        "--output-dir", str(match_dir)
    ], desc=f"Closed-reference clustering ({mode})")

    clustered_table = match_dir / f"clustered_table.qza"
    presabs_table = match_dir / f"presence_absence.qza"

    # Step 3 — Presence/absence table
    run_cmd(qiime_cmd + [
        "feature-table", "presence-absence",
        "--i-table", str(clustered_table),
        "--o-presence-absence-table", str(presabs_table)
    ], desc=f"Generating presence/absence table ({mode})")

    # Step 4 — Export and convert to TSV
    export_dir = work_dir / f"exported_{mode}"
    if export_dir.exists():
        shutil.rmtree(export_dir)
    ensure_dir(export_dir)

    run_cmd(qiime_cmd + [
        "tools", "export",
        "--input-path", str(clustered_table),
        "--output-path", str(export_dir / "abundance")
    ], desc=f"Exporting abundance table ({mode})")

    run_cmd(qiime_cmd + [
        "tools", "export",
        "--input-path", str(presabs_table),
        "--output-path", str(export_dir / "presence_absence")
    ], desc=f"Exporting presence/absence table ({mode})")

    biom_abund = export_dir / "abundance" / "feature-table.biom"
    biom_pa = export_dir / "presence_absence" / "feature-table.biom"

    abundance_tsv = work_dir / f"{mode}_Abundance.tsv"
    pa_tsv = work_dir / f"{mode}_PresAbs.tsv"

    run_cmd([
        "conda", "run", "-n", qiime_env, "biom", "convert",
        "-i", str(biom_abund), "-o", str(abundance_tsv),
        "--to-tsv", "--header-key", "taxonomy"
    ], desc=f"Converting abundance BIOM → TSV ({mode})")

    run_cmd([
        "conda", "run", "-n", qiime_env, "biom", "convert",
        "-i", str(biom_pa), "-o", str(pa_tsv),
        "--to-tsv", "--header-key", "taxonomy"
    ], desc=f"Converting presence/absence BIOM → TSV ({mode})")

    # Step 5 — Summarize abundance and richness
    print(f"\n Summarizing results for mode: {mode}")
    abundance_df = pd.read_csv(abundance_tsv, sep="\t", skiprows=[0], index_col=0)
    pa_df = pd.read_csv(pa_tsv, sep="\t", skiprows=[0], index_col=0)

    total = abundance_df.sum(axis=0).rename(f"{mode.capitalize()}_Total")
    richness = (pa_df > 0).sum(axis=0).rename(f"{mode.capitalize()}_Richness")
    proportion = (total / args.rarefying_depth).rename(f"{mode.capitalize()}_Proportion")

    summary_df = pd.concat([total, proportion, richness], axis=1)
    summary_df.index.name = "SampleID"

    # Step 6 — Merge with user metadata
    metadata = pd.read_csv(args.metadata_file, sep="\t")
    merged = metadata.merge(summary_df.reset_index(), on=args.sample_id_col, how="left")

    out_tsv = metadata_dir / f"Metadata_{mode}_Predictions.txt"
    merged.to_csv(out_tsv, sep="\t", index=False)

    print(f" Completed {mode.upper()} predictions → {out_tsv}")
    return out_tsv


# -------------------------------------------------------------------------
# Main function and combined summary
# -------------------------------------------------------------------------

def main(args):
    """
    Main entry point:
      - Clones or updates AmphiBac repo
      - Finds versioned QZA files
      - Runs one or multiple prediction modes
      - Merges all results into a single summary file if multiple modes are run
    """
    # Step 1 — Pull or update AmphiBac repo
    repo_dir = Path(tempfile.gettempdir()) / "AmphiBac-Database"
    if repo_dir.exists() and (repo_dir / ".git").exists():
        run_cmd(["git", "-C", str(repo_dir), "pull"], desc="Updating AmphiBac database")
    else:
        run_cmd(["git", "clone", args.amphibac_repo, str(repo_dir)], desc="Cloning AmphiBac database")

    # Step 2 — Determine modes
    if args.modes == ["all"]:
        modes = ["full", "inhibitory", "inhibitory_strict", "facilitating"]
    else:
        modes = args.modes

    # Step 3 — Run predictions per mode
    results = []
    for mode in modes:
        ref_qza = find_ref_qza(repo_dir, args.db_version, mode)
        out_path = run_prediction(args, mode, ref_qza)
        results.append(out_path)

    # --- Merge all mode metadata outputs if user ran --modes all ---
    if "all" in args.modes or (isinstance(args.modes, str) and args.modes == "all"):
        print("\n Combining metadata results from all modes...")
    
    
        metadata_files = {}
        for mode in ["full", "inhibitory", "inhibitory_strict", "facilitating"]:
            f = Path(args.output_dir) / mode / "metadata" / f"Metadata_{mode}_Predictions.txt"
            if f.exists():
                metadata_files[mode] = pd.read_csv(f, sep="\t")
            else:
                print(f" Warning: expected metadata file not found: {f}")
    
        if metadata_files:
            # --- Use "full" as the base (includes all original metadata) ---
            combined = metadata_files.get("full")
            if combined is None:
                raise FileNotFoundError(" Could not find the 'full' mode metadata file; it is required for merging.")
    
            # --- Add only predicted columns from other modes ---
            for mode, df in metadata_files.items():
                if mode == "full":
                    continue
                # Keep only SampleID and predicted columns (those starting with the mode name)
                pred_cols = [c for c in df.columns if c.startswith(mode.capitalize())]
                df_subset = df[["SampleID"] + pred_cols]
                combined = combined.merge(df_subset, on="SampleID", how="left")
    
            combined_out = Path(args.output_dir).resolve() / "Combined_Metadata_Predictions.txt"
            combined.to_csv(combined_out, sep="\t", index=False)
            print(f" Combined metadata written to: {combined_out}")
        else:
            print(" No metadata files found to combine.")
    else:
        print("No files to combined, I'm COMPLETE!")
# -------------------------------------------------------------------------
# CLI Interface
# -------------------------------------------------------------------------

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="AmphiBac Antifungal Prediction Pipeline (multi-mode, version-aware)")
    ap.add_argument("--qiime-env", required=True, help="Conda environment with QIIME2 (e.g. qiime2-amplicon-2025.7)")
    ap.add_argument("--otu-table", required=True, help="Path to rarefied OTU table (.qza)")
    ap.add_argument("--rep-seqs", required=True, help="Path to representative sequences (.qza)")
    ap.add_argument("--metadata-file", required=True, help="Path to sample metadata TSV")
    ap.add_argument("--sample-id-col", default="SampleID", help="Column in metadata containing sample IDs")
    ap.add_argument("--amphibac-repo", default="https://github.com/AmphiBac/AmphiBac-Database.git",
                    help="GitHub URL for AmphiBac database repo")
    ap.add_argument("--db-version", required=True, help="AmphiBac database version (e.g., 2025.1)")
    ap.add_argument("--modes", nargs="+", default=["all"],
                    help="Prediction modes to run: full, inhibitory, inhibitory_strict, facilitating, or all")
    ap.add_argument("--output-dir", required=True, help="Directory to store results")
    ap.add_argument("--identity", type=float, default=0.99, help="Clustering identity threshold (default 0.99)")
    ap.add_argument("--rarefying-depth", type=int, required=True, help="Rarefying depth used for normalization")

    args = ap.parse_args()
    main(args)
