def calculate_metrics(df):
    total_budget = df["Kümüle Bütçe"].sum() if "Kümüle Bütçe" in df.columns else 0
    total_actual = df["Kümüle Fiili"].sum() if "Kümüle Fiili" in df.columns else 0
    variance = total_budget - total_actual
    variance_pct = (variance / total_budget * 100) if total_budget != 0 else 0
    return total_budget, total_actual, variance, variance_pct
