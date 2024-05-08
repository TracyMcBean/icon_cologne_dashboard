import xarray as xr
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from datetime import datetime

from .style_functions import style_figure, style_error
from utils.error_utils import var_exists

def get_callbacks_timeheight(app, config):

    @app.callback(Output(component_id='intermediate-ds-timeheight', component_property='data'),
                Input(component_id='datepicker', component_property='date'),
                Input(component_id='path', component_property='value'),
                Input(component_id='height_slider', component_property='value'))
    def get_timeheight_data(seldate, path, level_range):
        # convert date to YYYYMMDD format
        seldate = datetime.strptime(seldate, '%Y-%m-%d').strftime('%Y%m%d')

        ds = xr.open_dataset(
            path+'/'+ config['paths']['prefix_meteogram'] + seldate + config['paths']['postfix_meteogram']+'.nc')
        # only get up to around 12 km height and every 6th time step to reduce data size for speedup

        var_list = ['CLC', 'T', 'RHO', 'P', 'REL_HUM','U', 'V']
        var_list = var_exists(var_list, ds)

        ds_sub = ds[var_list].isel(height_2=slice(level_range[0], level_range[1]), time=slice(0, len(ds.time), 6))
        df = ds_sub.to_dataframe()
        df = df.reset_index()
        # timeheighte data set must be converted to json so timeheightat it is stored as binary to be used in otimeheighter functions
        return df.to_json(date_format='iso', orient='split')


    @app.callback(Output(component_id='timeheight_plot', component_property='figure'),
                Input('dropdown_timeheight', 'value'),
                Input('intermediate-ds-timeheight', 'data'))
    def timeheight_graph_update(dropdown_value, df_json):
        df = pd.read_json(df_json, orient='split')

        # check if the variable is in the dataframe, if not use default error plot
        if dropdown_value not in df.columns:
            fig = go.Figure()
            fig = style_error(fig)
            return fig
        
        fig = go.Figure(data=
                        go.Contour(z=df['{}'.format(dropdown_value)], x=df['time'], y=df['height_2'],
                                colorscale='viridis_r', colorbar=dict(title='')))
        
        # apply styling to the figure
        fig = style_figure(fig)

        fig.update_layout(title='',
                        xaxis_title='Time [UTC]',
                        yaxis_title='Height [m]')
        # loop over all possible variables and set the colorbar title accordingly
        dropdown_values = ['CLC', 'T', 'RHO', 'P', 'REL_HUM',
                           'U', 'V']
        cbar_titles = ['0 or 1', 'T [K]', 'Rho [kg/m^3]', 'P [Pa]',
                       ' Rel. hum. [%]', 'U [m/s]', 'V [m/s]']
        for dv, ct in zip(dropdown_values, cbar_titles):
            if dropdown_value == dv:
                fig.update_traces(
                    colorbar=dict(
                        title=ct,
                        ),
                )
        if dropdown_value == 'T':
            #update colorscale for temperature
            fig.update_traces(colorscale="Turbo", selector=dict(type='contour'))
        if dropdown_value in ['U', 'V']:
            #update colorscale for wind, center around 0
            fig.update_traces(colorscale="PRGn", selector=dict(type='contour'),
                              zmid=0)
        
        return fig

