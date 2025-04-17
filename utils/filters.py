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

        # Get the current session state value
        current_selection = st.session_state.get(f"{key_prefix}_{col}", [])
        
        # Filter out any default values that are not in the current options
        valid_defaults = [val for val in current_selection if val in options]
        
        try:
            selected = st.multiselect(
                f"🔍 {col}",
                options,
                key=f"{key_prefix}_{col}",
                default=valid_defaults,
                help=f"{col} için filtre seçin",
            )
        except st.errors.StreamlitAPIException as e:
            st.warning(f"Filtre değerleri güncellendi. Lütfen tekrar seçim yapın.")
            # Reset the session state for this filter
            st.session_state[f"{key_prefix}_{col}"] = []
            selected = st.multiselect(
                f"🔍 {col}",
                options,
                key=f"{key_prefix}_{col}",
                default=[],
                help=f"{col} için filtre seçin",
            )
        
        selected_filters[col] = selected

    # Filtre uygulama
    filtered_df = df.copy()
    for col, selected in selected_filters.items():
        if selected:
            filtered_df = filtered_df[filtered_df[col].isin(selected)]
    return filtered_df
