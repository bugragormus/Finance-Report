# plotly_config.py
import plotly.io as pio
import plotly.express as px

def apply_plotly_defaults():
    pio.kaleido.scope.default_format = "png"
    pio.kaleido.scope.default_width = 1000
    pio.kaleido.scope.default_height = 600
    pio.kaleido.scope.default_colorway = px.colors.qualitative.Plotly
    pio.kaleido.scope.default_paper_bgcolor = "white"
    pio.kaleido.scope.default_plot_bgcolor = "white"
