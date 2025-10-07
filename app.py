import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

# Initialize the Dash app - NO CHANGES HERE
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Supermarket Insights Story"

try:
    df = pd.read_csv("Sample - Superstore.csv", encoding="latin1")
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    df['Order Month'] = df['Order Date'].dt.to_period('M').dt.to_timestamp()
except FileNotFoundError:
    print("Error: 'superstore.csv' not found.")
    df = pd.DataFrame()

def create_kpi_card(title, value, color):
    return dbc.Card(
        dbc.CardBody([
            html.H4(title, className="card-title text-muted"),
            html.H2(value, className="card-text", style={"color": color}),
        ], className="text-center"),
        className="kpi-card",
    )

def create_scene_1(df):
    if df.empty: return html.Div("Data not loaded.")
    total_sales = f"${df['Sales'].sum():,.0f}"
    avg_discount = f"{df['Discount'].mean():.2%}"
    total_profit = f"${df['Profit'].sum():,.0f}"
    sales_by_region = df.groupby('Region')['Sales'].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(sales_by_region, x='Region', y='Sales', title="Total Sales by Region", template='plotly_dark', color_discrete_sequence=['#4c78a8'])
    fig.update_layout(title_x=0.5, xaxis_title=None, yaxis_title="Total Sales ($)", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return html.Div([
        html.H1("Supermarket Performance Overview", className="scene-title"),
        html.P("A high-level look at key performance indicators across all regions.", className="scene-subtitle"),
        dbc.Row([dbc.Col(create_kpi_card("Total Sales", total_sales, "#1f77b4"), md=4), dbc.Col(create_kpi_card("Average Discount", avg_discount, "#ff7f0e"), md=4), dbc.Col(create_kpi_card("Total Profit", total_profit, "#2ca02c"), md=4)], className="mb-4"),
        dcc.Graph(figure=fig, className="story-chart"),
    ])

def create_scene_2(df):
    if df.empty: return html.Div("Data not loaded.")
    top_cat = df.groupby('Category')['Sales'].sum().idxmax()
    top_sub_cat = df.groupby('Sub-Category')['Sales'].sum().idxmax()
    sales_profit_by_cat = df.groupby('Category')[['Sales', 'Profit']].sum().reset_index()
    fig = go.Figure(data=[go.Bar(name='Sales', x=sales_profit_by_cat['Category'], y=sales_profit_by_cat['Sales'], marker_color='#1f77b4'), go.Bar(name='Profit', x=sales_profit_by_cat['Category'], y=sales_profit_by_cat['Profit'], marker_color='#2ca02c')])
    fig.update_layout(barmode='group', title="Sales vs. Profit by Category", template='plotly_dark', title_x=0.5, legend_title_text='Metric', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return html.Div([
        html.H1("Category & Product Analysis", className="scene-title"),
        html.P("Which product categories drive the most sales and profit?", className="scene-subtitle"),
        dbc.Row([dbc.Col(md=3), dbc.Col(create_kpi_card("Top Category by Sales", top_cat, "#1f77b4"), md=3), dbc.Col(create_kpi_card("Top Sub-Category by Sales", top_sub_cat, "#ff7f0e"), md=3), dbc.Col(md=3)], className="mb-4"),
        dcc.Graph(figure=fig, className="story-chart"),
    ])

def create_scene_3(df):
    if df.empty: return html.Div("Data not loaded.")
    total_customers = f"{df['Customer ID'].nunique():,}"
    avg_order_value = f"${df['Sales'].sum() / df['Order ID'].nunique():,.2f}"
    top_segment = df.groupby('Segment')['Sales'].sum().idxmax()
    fig = px.scatter(df, x='Discount', y='Profit', color='Segment', title="Profit vs. Discount by Customer Segment", template='plotly_dark', hover_data=['Category', 'Sales'])
    fig.update_layout(title_x=0.5, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return html.Div([
        html.H1("Customer Insights", className="scene-title"),
        html.P("Exploring the relationship between customer segments, discounts, and profitability.", className="scene-subtitle"),
        dbc.Row([dbc.Col(create_kpi_card("Total Unique Customers", total_customers, "#1f77b4"), md=4), dbc.Col(create_kpi_card("Average Order Value", avg_order_value, "#ff7f0e"), md=4), dbc.Col(create_kpi_card("Top Segment by Sales", top_segment, "#2ca02c"), md=4)], className="mb-4"),
        dcc.Graph(figure=fig, className="story-chart"),
    ])

def create_scene_4(df):
    if df.empty: return html.Div("Data not loaded.")
    monthly_sales = df.groupby('Order Month')['Sales'].sum()
    best_month = monthly_sales.idxmax().strftime('%B %Y')
    orders_per_year = df.groupby(df['Order Date'].dt.year)['Order ID'].nunique().mean()
    avg_orders_per_year = f"{orders_per_year:,.0f}"
    fig = px.line(monthly_sales.reset_index(), x='Order Month', y='Sales', title="Monthly Sales Trend", template='plotly_dark', markers=True)
    fig.update_layout(title_x=0.5, xaxis_title="Month", yaxis_title="Total Sales ($)", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return html.Div([
        html.H1("Sales Over Time", className="scene-title"),
        html.P("Analyzing sales patterns and seasonality over the years.", className="scene-subtitle"),
        dbc.Row([dbc.Col(md=3), dbc.Col(create_kpi_card("Best Month for Sales", best_month, "#1f77b4"), md=3), dbc.Col(create_kpi_card("Avg. Orders Per Year", avg_orders_per_year, "#ff7f0e"), md=3), dbc.Col(md=3)], className="mb-4"),
        dcc.Graph(figure=fig, className="story-chart"),
    ])



app.layout = html.Div(
    id='app-root',
    children=[
        
        html.Section(id='scene-0', className='scene', children=[create_scene_1(df)]),
        html.Section(id='scene-1', className='scene', children=[create_scene_2(df)]),
        html.Section(id='scene-2', className='scene', children=[create_scene_3(df)]),
        html.Section(id='scene-3', className='scene', children=[create_scene_4(df)]),
    ]
)

if __name__ == '__main__':
    if not df.empty:
        app.run(debug=True)
        
