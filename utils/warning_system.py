import pandas as pd

def style_warning_rows(df: pd.DataFrame):
    def apply_style(row):
        style = [''] * len(row)
        if "Kümüle Bütçe" in row and "Kümüle Fiili" in row:
            try:
                budget = row["Kümüle Bütçe"]
                actual = row["Kümüle Fiili"]
                if budget == 0:
                    usage_pct = 0
                else:
                    usage_pct = actual / budget

                if actual > budget:
                    style = ['background-color: #ffcccc'] * len(row)  # Red
                elif usage_pct < 0.1:
                    style = ['background-color: #e0e0e0'] * len(row)  # Grey
            except:
                pass
        return style

    return df.style.apply(apply_style, axis=1)
