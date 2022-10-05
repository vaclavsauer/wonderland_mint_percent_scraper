import sqlite3
from datetime import datetime
from datetime import timedelta

import dash
import pandas as pd
import plotly.graph_objects as go
from dash import dcc
from dash import html
from plotly.subplots import make_subplots

database = "output.db"

con = sqlite3.connect(database)
df = pd.read_sql_query("SELECT * from time_mint", con)

min_limits = df[
    df["timestamp"]
    > (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S.%f")
].quantile(0.01)
max_limits = df[
    df["timestamp"]
    > (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S.%f")
].quantile(0.99)

fig = make_subplots(
    rows=3,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.02,
    horizontal_spacing=0.02,
)

now = datetime.utcnow()

fig.update_layout(
    yaxis=dict(
        range=[
            min(
                min_limits["time_price"],
                min_limits["mim_price"],
                min_limits["time_mim_price"],
                min_limits["weth_price"],
                min_limits["wmemo_mim_price"],
            )
            * 0.9,
            max(
                max_limits["time_price"],
                max_limits["mim_price"],
                max_limits["time_mim_price"],
                min_limits["weth_price"],
                min_limits["wmemo_mim_price"],
            )
            * 1.1,
        ]
    ),
    yaxis2=dict(
        range=[
            min(
                min_limits["mim_roi"],
                min_limits["time_mim_roi"],
                min_limits["weth_roi"],
                min_limits["wmemo_mim_roi"],
            )
            * 0.9,
            max(
                max_limits["mim_roi"],
                max_limits["time_mim_roi"],
                min_limits["weth_roi"],
                min_limits["wmemo_mim_roi"],
            )
            * 1.1,
        ]
    ),
    xaxis=dict(
        range=[
            datetime.utcnow() - timedelta(days=1),
            datetime.utcnow() + timedelta(minutes=10),
        ]
    ),
)

# PRICE

fig.add_trace(
    go.Scatter(x=df["timestamp"], y=df["time_price"], name="$TIME price"), row=1, col=1
)

fig.add_trace(
    go.Scatter(x=df["timestamp"], y=df["mim_price"], name="MIM price"), row=1, col=1
)

fig.add_trace(
    go.Scatter(x=df["timestamp"], y=df["time_mim_price"], name="TIME-MIM LP price"),
    row=1,
    col=1,
)

fig.add_trace(
    go.Scatter(x=df["timestamp"], y=df["weth_price"], name="wETH.e price"), row=1, col=1
)

fig.add_trace(
    go.Scatter(x=df["timestamp"], y=df["wmemo_mim_price"], name="wMEMO-MIM SLP price"), row=1, col=1
)

# ROI

fig.add_trace(
    go.Scatter(x=df["timestamp"], y=df["mim_roi"], name="MIM ROI"), row=2, col=1
)

fig.add_trace(
    go.Scatter(x=df["timestamp"], y=df["time_mim_roi"], name="TIME-MIM LP ROI"),
    row=2,
    col=1,
)

fig.add_trace(
    go.Scatter(x=df["timestamp"], y=df["weth_roi"], name="wETH.e ROI"), row=2, col=1
)

fig.add_trace(
    go.Scatter(x=df["timestamp"], y=df["wmemo_mim_roi"], name="wMEMO-MIM SLP ROI"), row=2, col=1
)

# balance

fig.add_trace(
    go.Scatter(x=df["timestamp"], y=df["treasury_balance"], name="Treasury Balance"),
    row=3,
    col=1,
)

fig.add_trace(
    go.Scatter(x=df["timestamp"], y=df["mim_purchased"], name="MIM Purchased"),
    row=3,
    col=1,
)

fig.add_trace(
    go.Scatter(
        x=df["timestamp"], y=df["time_mim_purchased"], name="TIME-MIM Purchased"
    ),
    row=3,
    col=1,
)

fig.add_trace(
    go.Scatter(x=df["timestamp"], y=df["weth_purchased"], name="wETH.e Purchased"),
    row=3,
    col=1,
)

fig.add_trace(
    go.Scatter(x=df["timestamp"], y=df["wmemo_mim_purchased"], name="wMEMO-MIM SLP Purchased"),
    row=3,
    col=1,
)

app = dash.Dash(__name__)
app.layout = html.Div(
    [
        dcc.Graph(
            figure=fig,
            style={"width": "80vw", "height": "100vh", "margin": "auto"},
        )
    ]
)

app.run_server(debug=False)
# fig.show()
