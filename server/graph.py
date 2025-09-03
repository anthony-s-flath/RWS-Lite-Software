import pandas as pd
import plotly.express as px
import plotly.io as pio


class Graph:
    def __init__(self, query):
        print(query)
        if len(dict(query)) == 0:
            self.data = pd.read_csv("data.csv")
            self.fig = px.scatter(x=self.data['time'], y=self.data['in_temp'])

    # returns this fig in an html page as an encoded string
    def as_html(self):
        return pio.to_html(self.fig, include_plotlyjs='cdn').encode()
