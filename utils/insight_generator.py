import pandas as pd


def generate_insights(df):
    insights = []

    if "Kümüle Fiili" in df.columns and "Masraf Yeri Adı" in df.columns:
        masraf_sums = (
            df.groupby("Masraf Yeri Adı")["Kümüle Fiili"]
            .sum()
            .sort_values(ascending=False)
        )
        if not masraf_sums.empty:
            top_yer = masraf_sums.index[0]
            top_val = masraf_sums.iloc[0]
            insights.append(
                f"📌 En fazla harcama yapan masraf yeri: **{top_yer}** ({top_val:,.0f} ₺)"
            )

    if "Kümüle Bütçe" in df.columns and "Kümüle Fiili" in df.columns:
        df["Fark"] = df["Kümüle Bütçe"] - df["Kümüle Fiili"]
        sapmalar = (
            df[["Masraf Yeri Adı", "Fark"]]
            .groupby("Masraf Yeri Adı")
            .sum()
            .sort_values(by="Fark")
        )
        if not sapmalar.empty:
            en_cok_asan = sapmalar[sapmalar["Fark"] < 0]
            if not en_cok_asan.empty:
                en_cok_asan_row = en_cok_asan.iloc[0]
                insights.append(
                    f"⚠️ Bütçeyi en fazla aşan masraf yeri: **{en_cok_asan_row.name}** ({en_cok_asan_row['Fark']:,.0f} ₺ fark)"
                )

        en_az_kullanan = df[df["Kümüle Fiili"] == 0]
        if not en_az_kullanan.empty:
            yerler = en_az_kullanan["Masraf Yeri Adı"].dropna().unique().tolist()
            yerler_str = ", ".join(yerler[:5])
            insights.append(f"❗ Hiç harcama yapılmayan masraf yerleri: {yerler_str}")

        active = df[df["Kümüle Fiili"] > 0]
        if not active.empty:
            min_row = (
                active.groupby("Masraf Yeri Adı")["Kümüle Fiili"]
                .sum()
                .sort_values()
                .head(1)
            )
            insights.append(
                f"🔍 En az harcama yapan (aktif) masraf yeri: **{min_row.index[0]}** ({min_row.iloc[0]:,.0f} ₺)"
            )

        if "Masraf Yeri Adı" in df.columns:
            df["Kullanım Oranı"] = df["Kümüle Fiili"] / df["Kümüle Bütçe"].replace(
                0, pd.NA
            )
            az_kullananlar = (
                df[df["Kullanım Oranı"] < 0.5]["Masraf Yeri Adı"].dropna().unique()
            )
            if len(az_kullananlar) > 0:
                insights.append(
                    f"🧊 Bütçesinin yarısından azını kullanan masraf yerleri: {', '.join(az_kullananlar[:5])}"
                )

            kullanim_df = df[df["Kümüle Bütçe"] > 0].copy()
            kullanim_df["Kullanım Oranı"] = (
                kullanim_df["Kümüle Fiili"] / kullanim_df["Kümüle Bütçe"]
            )
            if not kullanim_df.empty:
                max_row = kullanim_df.sort_values(
                    "Kullanım Oranı", ascending=False
                ).head(1)
                oran = max_row["Kullanım Oranı"].values[0] * 100
                ad = max_row["Masraf Yeri Adı"].values[0]
                insights.append(
                    f"🔥 En yüksek bütçe kullanım oranı: **{ad}** (%{oran:.1f})"
                )

    if "Masraf Çeşidi Grubu 1" in df.columns and "Kümüle Fiili" in df.columns:
        top_grup = (
            df.groupby("Masraf Çeşidi Grubu 1")["Kümüle Fiili"]
            .sum()
            .sort_values(ascending=False)
            .head(1)
        )
        if not top_grup.empty:
            insights.append(
                f"🏷️ En çok harcama yapılan masraf grubu: **{top_grup.index[0]}** ({top_grup.iloc[0]:,.0f} ₺)"
            )

    return insights
