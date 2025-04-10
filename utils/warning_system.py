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

                # Kümüle Bütçe ve Kümüle Fiili hücrelerine stil uygula
                if actual > budget:
                    style[row.index.get_loc("Kümüle Bütçe")] = 'background-color: #ffcccc'  # Red for Kümüle Bütçe
                    style[row.index.get_loc("Kümüle Fiili")] = 'background-color: #ffcccc'  # Red for Kümüle Fiili
                    style[row.index.get_loc("Masraf Yeri")] = 'background-color: #ffcccc'  # Red for Kümüle Bütçe
            except:
                pass
        return style

    return df.style.apply(apply_style, axis=1)
