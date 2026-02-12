import dash
from dash import dcc, html
import plotly.express as px
from data_loader import load_all_data
import pandas as pd
import numpy as np

dash.register_page(__name__, path='/page3', suppress_callback_exceptions=True)

