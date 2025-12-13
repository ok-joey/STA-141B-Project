def check_msa_format(df, msa_col="MSA"):
    """
    Checks the MSA column for correct format:
      - Must be strings
      - Must be 5 digits
      - Must contain only digits (0-9)
    Prints a summary of any issues.
    """
    if msa_col not in df.columns:
        print(f"⚠️ Column '{msa_col}' not found in DataFrame.")
        return

    msa = df[msa_col].astype(str)

    # Check length
    wrong_length = msa[msa.str.len() != 5]
    if len(wrong_length) > 0:
        print(f"⚠️ {len(wrong_length)} MSAs are not 5 digits:")
        print(wrong_length.unique())

    # Check for non-digit characters
    non_digits = msa[~msa.str.match(r"^\d{5}$")]
    if len(non_digits) > 0:
        print(f"⚠️ {len(non_digits)} MSAs contain non-digit characters:")
        print(non_digits.unique())

    # Summary
    if len(wrong_length) == 0 and len(non_digits) == 0:
        print("✅ All MSAs appear correctly formatted (5-digit numeric strings).")
