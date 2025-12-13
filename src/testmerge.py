def test_merge_success(jobs_df, merged_df, county_col="county_fips", threshold=0.75):
    """
    Tests whether the merge successfully mapped county/MSA information.

    Parameters
    ----------
    jobs_df : pd.DataFrame
        Original jobs dataframe BEFORE merge.
    merged_df : pd.DataFrame
        Dataframe AFTER merge (with county/MSA columns).
    county_col : str
        The column added by the merge (e.g. 'county_fips').
    threshold : float
        Minimum acceptable non-NA match rate.
    """

    # Pre-merge NA rate (always 100% if county wasn't present)
    pre_na = jobs_df[county_col].isna().mean() if county_col in jobs_df.columns else 1.0

    # Post-merge NA rate
    post_na = merged_df[county_col].isna().mean()

    # Matching rate
    match_rate = 1 - post_na

    print("===== MERGE SUCCESS TEST =====")
    print(f"Pre-merge NA rate:   {pre_na:.4f}")
    print(f"Post-merge NA rate:  {post_na:.4f}")
    print(f"Match rate:          {match_rate:.4f}")
    print("----------------------------------")

    if match_rate >= threshold:
        print(f"✅ PASS — Merge successful (≥ {threshold*100:.0f}% matches)")
    else:
        print(f"❌ FAIL — Match rate < {threshold*100:.0f}%")

    print("----------------------------------")

    # Also return match_rate in case you need it programmatically
    return match_rate
