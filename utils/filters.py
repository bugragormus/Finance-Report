import streamlit as st

def apply_filters(df, columns, key_prefix):
    selected_filters = {}
    for col in columns:
        if col not in df.columns:
            continue
        temp_df = df.copy()
        for other_col in columns:
            if other_col == col:
                continue
            if f"{key_prefix}_{other_col}" in st.session_state:
                selected = st.session_state[f"{key_prefix}_{other_col}"]
                if selected:
                    temp_df = temp_df[temp_df[other_col].isin(selected)]
        options = sorted(temp_df[col].dropna().unique().tolist(), key=lambda x: str(x))

        selected = st.multiselect(
            f"🔍 {col}",
            options,
            key=f"{key_prefix}_{col}",
            default=st.session_state.get(f"{key_prefix}_{col}", []),
            help=f"{col} için filtre seçin",
        )
        selected_filters[col] = selected


# Filtre uygulama
    filtered_df = df.copy()
    for col, selected in selected_filters.items():
        if selected:
            filtered_df = filtered_df[filtered_df[col].isin(selected)]
    return filtered_df
