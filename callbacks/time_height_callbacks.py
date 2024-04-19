import xarray as xr
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from datetime import datetime

from .style_functions import style_figure

def get_callbacks_timeheight(app):

    @app.callback(Output(component_id='intermediate-ds-timeheight', component_property='data'),
                Input(component_id='datepicker', component_property='date'),
                Input(component_id='path', component_property='value'),
                Input(component_id='height_slider', component_property='value'))
    def get_timeheight_data(seldate, path, level_range):
        # convert date to YYYYMMDD format
        seldate = datetime.strptime(seldate, '%Y-%m-%d').strftime('%Y%m%d')

        ds = xr.open_dataset(
            path+'/METEOGRAM_patch001_' + seldate + '_koeln.nc')
        # only get up to around 12 km height and every 6th time step to reduce data size for speedup
        ds_sub = ds[['CLC', 'T']].isel(height_2=slice(level_range[0], level_range[1]), time=slice(0, len(ds.time), 6))
        df = ds_sub.to_dataframe()
        df = df.reset_index()
        # timeheighte data set must be converted to json so timeheightat it is stored as binary to be used in otimeheighter functions
        return df.to_json(date_format='iso', orient='split')


    @app.callback(Output(component_id='timeheight_plot', component_property='figure'),
                Input('dropdown_timeheight', 'value'),
                Input('intermediate-ds-timeheight', 'data'))
    def timeheight_graph_update(dropdown_value, df_json):
        df = pd.read_json(df_json, orient='split')
        fig = go.Figure(data=
                        go.Contour(z=df['{}'.format(dropdown_value)], x=df['time'], y=df['height_2'],
                                colorscale='thermal'))
        
        # apply styling to the figure
        fig = style_figure(fig)

        if dropdown_value == 'CLC':
            fig.update_layout(title='',
                            xaxis_title='Time',
                            yaxis_title=''
                            )
        return fig

