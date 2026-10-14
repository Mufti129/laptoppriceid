import plotly.graph_objects as go

def apply_dark_plotly_layout(fig, height=420):
    """Standarisasi layout dark theme untuk seluruh grafik Plotly di LaptopPrice ID."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1e293b",
        plot_bgcolor="#1e293b",
        font=dict(color="#f8fafc", family="Plus Jakarta Sans"),
        height=height,
        margin=dict(t=40, b=30, l=30, r=30),
        legend=dict(
            bgcolor="rgba(15, 23, 42, 0.6)",
            bordercolor="rgba(255, 255, 255, 0.1)",
            font=dict(color="#f8fafc")
        )
    )
    fig.update_xaxes(gridcolor="#334155", linecolor="#475569")
    fig.update_yaxes(gridcolor="#334155", linecolor="#475569")
