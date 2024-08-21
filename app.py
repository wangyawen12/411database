from databases.mongodb_utils import MongoDB
from databases.mysql_utils import MySQL
from databases.neo4j_utils import Neo4j
from dash import Dash, html, dcc, Output, Input, callback, dash_table, State
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import mysql.connector
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os

load_dotenv()

mysqlHost = os.getenv('MYSQL_HOST')
mysqlUser = os.getenv('MYSQL_USER')
mysqlPassword = os.getenv('MYSQL_PASSWORD')
mysqlDatabase = os.getenv('MYSQL_DATABASE')

mongodb = MongoDB()
mysqldb = MySQL()
neo4j = Neo4j()

# Get data from databases
keywords = mysqldb.get_keywords()
df = mongodb.krc_by_entity()
faculty = mongodb.get_all_faculty()

#top keywords
first_widget = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4(children='''
                    Keyword overview:
                '''),
                dcc.Input(id="val-selector", type="number", min=5, max=20, step=5, value=10),
                html.Div(id='keyword_summary', children='''
                '''),

                dcc.Graph(
                    id='example-graph',
                    figure={}
                ),
            ]
        )
    ],
    className='card'
)
#top publications based on keywords
second_widget = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4(children='''Publications based on keyword'''),
                dcc.Input(id="pub_keyword", type="text", value="graph"),
                dcc.Graph(
                    id='pub_keyword_graph',
                    figure={}
                ),
            ]
        )
    ],
    className='card',
    style={'flex': '1 1 calc(50% - 5px)'}
)

#update faculty
third_widget = dbc.Card(
    [
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.H4(children='''
                                Faculty Page
                            '''),
                        dcc.Markdown("This form has string editing enabled on columns"),
                        dcc.Input(id='search_faculty_input', type='text', value= 'david forsyth',placeholder='Enter faculty name'),
                        html.Button('Search', id='search-button', n_clicks=0),

                        dag.AgGrid(
                            id="update_faculty_output",
                            columnDefs=[{"field": "id", "hide": True},{"field": "name"}, {"field": "research_interest"}, {"field": "position"},{"field": "email"},{"field": "phone"},{"field": "university"}],
                            columnSize="sizeToFit",
                            defaultColDef={"editable": True, "cellDataType": False},
                            dashGridOptions={"animateRows": False},
                            style={"height": 100, "width": '100%'}
                        ),
                    ]
                ),
                html.Img(id='img_url', width = '300', height = '350'),
                html.Br(),
                html.Button('Save Changes', id='save-button', n_clicks=0),
                html.Div(children='''
                    Attention: First hit enter on updated data filed then click Save Changes button.
                '''),
                html.Div(id='edit-output')
            ]
        )
    ],
    # style={'textAlign': 'center'}
    className='card',
    style={'flex': '1 1 calc(50% - 5px)'}
)
#KRC
fourth_widget = dbc.Card(
    [
        dbc.CardBody([
            html.H4('Total KRC by Affiliation/Faculty'),
            html.Div([
                dcc.Dropdown(['Affiliation', 'Faculty'], 'Affiliation', id = 'entity-option'),
                dcc.Dropdown(keywords, '', id = 'keyword-option'),
            ], style = {'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '10px'}),
            dcc.Graph(id = 'krc-graph'),
            dcc.RadioItems(
                options = [5, 10, 15],
                value = 15,
                id = 'number-affiliation',
                inline = True,
                style = {'margin': '10px'},
                inputStyle = {'margin': '5px'},
            ),
        ]),
    ],
    className='card'
)
#top faculty by keywords
fifth_widget = dbc.Card(
    [
        dbc.CardBody([
            html.H4('Top Faculty Ranking By Keywords'),
            html.Div(
                [
                    dcc.Dropdown(keywords, '', id = 'keyword', multi=True),
                ],
            ),
            dcc.Graph(id = 'faculty-keyword-graph'),
        ]),
    ],
    className='card'
)

#update publications
sixth_widget = dbc.Card(
    [
        dbc.CardBody([
            html.H4('Update Publications'),
            html.Div(
                [
                    html.Span('Faculty:'),
                    dcc.Dropdown(faculty, '', id='faculty-update'),
                ]
            ),
            html.Div(
                [
                    html.Span('Publication ID:'),
                    dcc.Dropdown(id='publication_id', placeholder='Pick a publication id'),
                ]
            ),
            html.Div(
                [
                    html.Span('New Title:', style={'marginRight': '10px'}),
                    dcc.Input(id='new-title', type='text', placeholder='New Title'),
                ],
                style={'display': 'flex', 'alignItems': 'center', 'marginTop': '10px'}
            ),
            html.Div(
                [
                    html.Span('New Venue:', style={'marginRight': '10px'}),
                    dcc.Input(id='new-venue', type='text', placeholder='New Venue'),
                ],
                style={'display': 'flex', 'alignItems': 'center', 'marginTop': '10px'}
            ),
            html.Div(
                [
                    html.Span('New Year:', style={'marginRight': '10px'}),
                    dcc.Input(id='new-year', type='number', placeholder='New Year'),
                ],
                style={'display': 'flex', 'alignItems': 'center', 'marginTop': '10px'}
            ),
            html.Div(
                [
                    html.Span('Number Citations:', style={'marginRight': '10px'}),
                    dcc.Input(id='new-num-citations', type='number', placeholder='Number of Citations'),
                ],
                style={'display': 'flex', 'alignItems': 'center', 'marginTop': '10px'}
            ),
            html.Button('Submit', id='submit-val', n_clicks=0),
            html.H6(id='update-message', style={'color': 'red', 'font': 'bold'}),
            html.Div(
                children=[
                    dbc.Card(
                        dbc.CardBody([
                            html.H6('Publication Detail'),
                            html.Hr(),
                            html.Div(id='old-publication'),
                        ]),
                        # className='w-50',
                    ),
                    dbc.Card(
                        dbc.CardBody([
                            html.H6('New Publication Detail'),
                            html.Hr(),
                            html.Div(id='new-publication')
                        ]),
                        # className='w-50',
                    ),
                ],
                style={'display': 'flex', 'justifyContent': 'center', 'gap': '5px'}
            ),
        ]),
    ],
    className='card'
)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "CS 411:Final Project"
server = app.server

body = html.Div([
    html.H1('Explore the Academic World', style={'display': 'flex', 'justifyContent': 'center'}),
    html.H5('Help Students Pick their Graduate School', style={'display': 'flex', 'justifyContent': 'center'}),
    html.Div(
        id='card-container',
        children=[
            first_widget,
            second_widget,
            fourth_widget,
            fifth_widget,
            third_widget,
            sixth_widget
        ]
    )
])

app.layout = body

@callback(
    Output('old-publication', 'children'),
    Input('publication_id', 'value'),
    prevent_initial_call = True
)
def get_old_publication(publication_id):
    old_publication = mongodb.get_publication_by_id(int(publication_id))
    old_data = html.Ul(
                        [html.Li(f"{key}: {value}") for key, value in old_publication.items()],
                        style={'listStyleType': 'none', 'padding': 0, 'margin': 0}
                    )
    return old_data

@callback(
    Output('update-message', 'children'),
    Output('new-publication', 'children'),
    Input('submit-val', 'n_clicks'),
    State('new-title', 'value'),
    State('new-venue', 'value'),
    State('new-year', 'value'),
    State('new-num-citations', 'value'),
    State('publication_id', 'value'),
    prevent_initial_call = True
)
def update_publication(n_clicks, title, venue, year, numCitations, publication_id):
    if n_clicks > 0:
        # print('clicked')
        content = {}
        if title:
            content['title'] = title
        if venue:
            content['venue'] = venue
        if year:
            content['year'] = year
        if numCitations:
            content['numCitations'] = numCitations
        
        updated_publication = mongodb.update_publication(int(publication_id), content)
        if updated_publication is False:
            return 'Error: Year must be between 1500 and 2024', html.Div()
        # print(updated_publication)
        res = 'Update successfully!'
        new_data = html.Ul(
                        [html.Li(f"{key}: {value}") for key, value in updated_publication.items()],
                        style={'listStyleType': 'none', 'padding': 0, 'margin': 0}
                    )
        
        return res, new_data
        # return res

@callback(
    Output('publication_id', 'options'),
    Input('faculty-update', 'value'),
    prevent_initial_call = True
)
def get_faculty_publications(faculty):
    publication_ids = mongodb.get_publication_id(faculty)
    # print(type(publication_ids[0]))
    return publication_ids

@callback(
    Output('faculty-keyword-graph', 'figure'),
    Input('keyword', 'value'),
)
def update_faculty_keyword_graph(keywords):
    keywords_list = [keyword for keyword in keywords]
    df = neo4j.find_faculty_by_keywords(keywords=keywords_list)
    # end = time.time()
    # time_spend = (end - start) * 1000
    # print(f"Query time with indexing: {time_spend: .2f} ms")
    fig = px.bar(df, x=df.columns[0], y=df.columns[1])
    return fig

@callback(
    Output('krc-graph', 'figure'),
    Input('number-affiliation', 'value'),
    State('entity-option', 'value'),
)
def resize_krc_graph(size, entity_option):
    global df
    # print('in resize_krc_graph')
    df_graph = df.iloc[:size].reset_index(drop=True)
    fig = px.bar(df_graph, x=entity_option, y='total_KRC')
    return fig

@callback(
    Output('krc-graph', 'figure', allow_duplicate=True),
    Input('entity-option', 'value'),
    Input('keyword-option', 'value'),
    State('number-affiliation', 'value'),
    prevent_initial_call = True
)
def change_krc_graph(entity_option, keyword_option, size):
    global df
    # print('in change_krc_graph')
    # start = time.time()
    df = mongodb.krc_by_entity(entity=entity_option, keyword=keyword_option)
    # end = time.time()
    # time_spend = (end - start) * 1000
    # print(f"Query time with indexing: {time_spend: .2f} ms")
    df_graph = df.iloc[:size].reset_index(drop=True)
    fig = px.bar(df_graph, x=entity_option, y='total_KRC')
    return fig

@callback(
    Output("example-graph", "figure"),
    Output("keyword_summary", 'children'),
    Input("val-selector", "value"))
def create_chart(selected_val):
    conn = mysql.connector.connect(
        host=mysqlHost,
        user=mysqlUser,
        password=mysqlPassword,
        database=mysqlDatabase,
    )
    cursor = conn.cursor()
    
    # params = (selected_val, )

    cursor.execute(
        "SELECT k.name AS name, COUNT(pk.publication_id) as count "
        "FROM publication_keyword pk "
        "JOIN publication p ON pk.publication_id = p.id "
        "JOIN keyword k ON pk.keyword_id = k.id "
        "WHERE p.year >= 2012 "
        "GROUP BY k.name ORDER BY count(pk.publication_id) DESC "
        f"LIMIT {selected_val};"
    )

    results = cursor.fetchall()

    df = pd.DataFrame(results, columns=['name', 'count'])
    fig = px.bar(df, x="name", y="count")


    cursor.execute(
        f"SELECT COUNT(*) FROM keyword;"
    )
    totalKeywords = cursor.fetchall()
    keywordRs = 'Total Keywords: {}, top {} popular keywords.'.format(totalKeywords[0][0],selected_val)
    cursor.close()
    conn.close()
    return fig,keywordRs


@callback(
    Output("pub_keyword_graph", "figure"),
    Input("pub_keyword", "value"))
def create_pub_keyword_chart(selected_val):
    conn = mysql.connector.connect(
        host=mysqlHost,
        user=mysqlUser,
        password=mysqlPassword,
        database=mysqlDatabase,
    )
    cursor = conn.cursor()

    params = (selected_val,)
    cursor.execute(
        f"SELECT p.title, p.num_citations, pk.score as score "
        f"FROM keyword k "
        f"JOIN publication_keyword pk ON pk.keyword_id = k.id "
        f"JOIN publication p ON p.id = pk.publication_id "
        f"WHERE k.name = %s "
        f"ORDER BY p.num_citations DESC "
        f"Limit 10;", params=params
    )
    

    results = cursor.fetchall()

    df2 = pd.DataFrame(results, columns=['title', 'num_citations', 'score'])

    fig2 = px.scatter(df2, x="num_citations", y="score", size="num_citations", color="title")

    cursor.close()
    conn.close()
    return fig2

#update faculty  https://dash.plotly.com/dash-ag-grid/cell-editors
@callback(
    Output('img_url','src'),
    Output(component_id='update_faculty_output', component_property='rowData'),
    # Input(component_id='update_faculty_input', component_property='value'),# change to use state
    Input('search-button', 'n_clicks'),
    State('search_faculty_input', 'value')
)
def search_faculty(n_clicks,selected_val):
    conn = mysql.connector.connect(
        host=mysqlHost,
        user=mysqlUser,
        password=mysqlPassword,
        database=mysqlDatabase,
    )
    cursor = conn.cursor()

    params = (selected_val,)
    cursor.execute(
        f"SELECT f.id as id, f.name as name, f.research_interest as research_interest, f.position as position, f.email as email, f.phone as phone, f.photo_url as photo, university.name as university from faculty f "
        f"join university on f.university_id=university.id "
        f"where f.name = %s;", params=params
    )

    results = cursor.fetchall()
    # print(results)
    column_names = [i[0] for i in cursor.description]
    df2 = pd.DataFrame(results, columns=column_names)
    imgUrl=""
    if len(results)>0 :
        imgUrl = results[0][6]
    cursor.close()
    conn.close()
    return imgUrl,df2.to_dict('records')

#Callback to update MySQL database with edited data
@app.callback(
    Output('edit-output', 'children'),
    Input('save-button', 'n_clicks'),
    State('update_faculty_output', 'rowData')
)
def update_faculty(n_clicks, new_data):#new_data is from State
    if n_clicks is None or new_data is None:
        return "No changes to update."

    conn = mysql.connector.connect(
        host=mysqlHost,
        user=mysqlUser,
        password=mysqlPassword,
        database=mysqlDatabase,
    )
    cursor = conn.cursor()
    # print("xxxxx",new_data)

    for row in new_data:
        cursor.execute(
            """
            UPDATE faculty
            SET name = %s, position = %s, research_interest =%s, email =%s, phone = %s
            WHERE id = %s
            """, (row['name'], row['position'], row['research_interest'], row['email'],  row['phone'], row['id'])
        )

    conn.commit()
    cursor.close()
    conn.close()

    return f"Updated {len(new_data)} rows."




if __name__ == '__main__':
    app.run(debug=True)
