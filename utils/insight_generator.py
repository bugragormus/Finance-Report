import pandas as pd

def generate_insights(df):
    insights = []

    if "Kümüle Fiili" in df.columns and "Masraf Yeri Adı" in df.columns:
        masraf_sums = df.groupby("Masraf Yeri Adı")["Kümüle Fiili"].sum().sort_values(ascending=False)
        if not masraf_sums.empty:
            top_yer = masraf_sums.index[0]
            top_val = masraf_sums.iloc[0]
            insights.append(f"📌 En fazla harcama yapan masraf yeri: **{top_yer}** ({top_val:,.0f} ₺)")

    if "Kümüle Bütçe" in df.columns and "Kümüle Fiili" in df.columns:
        df["Fark"] = df["Kümüle Bütçe"] - df["Kümüle Fiili"]
        sapmalar = df[["Masraf Yeri Adı", "Fark"]].groupby("Masraf Yeri Adı").sum().sort_values(by="Fark")
        if not sapmalar.empty:
            en_cok_asan = sapmalar[sapmalar["Fark"] < 0]
            if not en_cok_asan.empty:
                en_cok_asan_row = en_cok_asan.iloc[0]
                insights.append(f"⚠️ Bütçeyi en fazla aşan masraf yeri: **{en_cok_asan_row.name}** ({en_cok_asan_row['Fark']:,.0f} ₺ fark)")

        en_az_kullanan = df[df["Kümüle Fiili"] == 0]
        if not en_az_kullanan.empty:
            yerler = en_az_kullanan['Masraf Yeri Adı'].dropna().unique().tolist()
            yerler_str = ', '.join(yerler[:5])
            insights.append(f"❗ Hiç harcama yapılmayan masraf yerleri: {yerler_str}")

    return insights
