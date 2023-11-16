from flask import Blueprint, render_template
from flask import abort
from flask_login import login_required, current_user
import sqlite3
import pandas as pd
import json
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models import HoverTool
from bokeh.io import curdoc
curdoc().theme = 'dark_minimal'
import warnings

dashcharts=Blueprint('dancing',__name__, template_folder='templates')

@dashcharts.route('/analytics')
@login_required
def analytics():
    if current_user.userlevel not in ["4","5"]:
        abort(403)

    sqliteConnection=sqlite3.connect('instance/site.db')
    cursor=sqliteConnection.cursor()
    query='select * from appdata;'

    result = cursor.fetchall()
    df=pd.read_sql(query, sqliteConnection)
    cursor.close()
    warnings.filterwarnings(action='ignore', category=Warning)
    df2=df[['entry_date', 'bank_name', 'bank_status']]
    df2['entry_date']=pd.to_datetime(df2['entry_date'])
    df2['month']=df2['entry_date'].dt.month
    df2['day']=df2['entry_date'].dt.day
    df_crnt_mnth = df2[df2['month'] == 6]
    df_crnt_mnth.drop(['entry_date', 'month'], axis=1, inplace=True)
    group = df_crnt_mnth.groupby(['day', 'bank_name']).agg({"bank_name": len})
    dhli = group.unstack()
    dhli.fillna(0, inplace=True)
    curdoc().theme='dark_minimal'
    p23 = figure(title="Cards application count", max_width=500, height=350, x_axis_label="Month",
                 y_axis_label="Number of applications",
                 toolbar_location=None,
                 tools=[HoverTool()],
                 tooltips="On day @x there are @y applications")
    p23.line(dhli['bank_name', 'CBD'].index, dhli['bank_name', 'CBD'].values, legend_label='CBD', color="blue",
             line_width=2)
    p23.line(dhli['bank_name', 'ADCB'].index, dhli['bank_name', 'ADCB'].values, legend_label='ADCB', color="red",
             line_width=2)
    p23.line(dhli['bank_name', 'SCB'].index, dhli['bank_name', 'SCB'].values, legend_label='SCB', color="green",
             line_width=2)
    p23.line(dhli['bank_name', 'ENBD'].index, dhli['bank_name', 'ENBD'].values, legend_label='ENBD', color="gray",
             line_width=2)
    p23.line(dhli['bank_name', 'RAK'].index, dhli['bank_name', 'RAK'].values, legend_label='RAK', color="purple",
             line_width=2)

    # p23.circle(dhli['bank_name', 'ADCB'].index, dhli['bank_name', 'CBD'].values, size=8, color="#b86f23")
    p23.legend.location = 'top_left'
    p23.legend.label_text_font = "times"
    p23.legend.label_text_font_style = "italic"
    p23.legend.border_line_width = 3
    p23.legend.border_line_color = "navy"
    p23.legend.border_line_alpha = 0.8
    p23.legend.background_fill_color = "navy"
    p23.legend.background_fill_alpha = 0.2
    p23.xaxis.axis_line_width = 3
    p23.axis.minor_tick_in = -3
    p23.axis.minor_tick_out = 6

    script, div = components(p23)

    return render_template('dashboard.html', script=script, div=div)