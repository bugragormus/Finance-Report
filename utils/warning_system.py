import pandas as pd
from config.constants import MONTHS


def style_warning_rows(df: pd.DataFrame):
    def apply_style(row):
        style = [""] * len(row)

        # Kümüle kontrolü
        if "Kümüle Bütçe" in row and "Kümüle Fiili" in row:
            try:
                budget = row["Kümüle Bütçe"]
                actual = row["Kümüle Fiili"]

                if actual > budget:
                    # Kümüle alanları boyama (kırmızı)
                    for col in ["Kümüle Bütçe", "Kümüle Fiili"]:
                        if col in row.index:
                            style[row.index.get_loc(col)] = "background-color: #ffcccc"

                    # Masraf bilgilerini boyama (kırmızı)
                    if "Masraf Yeri" in row.index:
                        style[
                            row.index.get_loc("Masraf Yeri")
                        ] = "background-color: #ffcccc"
                    if "Masraf Çeşidi" in row.index:
                        style[
                            row.index.get_loc("Masraf Çeşidi")
                        ] = "background-color: #ffcccc"

                    # Aylık bazda fiili > bütçe ise mavi renkle boyama
                    for month in MONTHS:
                        b_col = f"{month} Bütçe"
                        a_col = f"{month} Fiili"
                        if b_col in row.index and a_col in row.index:
                            try:
                                if row[a_col] > row[b_col]:
                                    style[
                                        row.index.get_loc(b_col)
                                    ] = "background-color: #ffcccc"
                                    style[
                                        row.index.get_loc(a_col)
                                    ] = "background-color: #ffcccc"
                            except:
                                continue

            except:
                pass

        return style

    return df.style.apply(apply_style, axis=1)


def style_overused_rows(df: pd.DataFrame):
    def apply_style(row):
        if "Kullanım (%)" in row and pd.notnull(row["Kullanım (%)"]):
            try:
                if row["Kullanım (%)"] >= 100:
                    return ["background-color: #ffcccc"] * len(row)
            except:
                pass
        return [""] * len(row)

    return df.style.apply(apply_style, axis=1)
