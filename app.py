from dash import Dash, dcc, html, callback
from dash.dependencies import Input, Output, State
import dash
from dash_iconify import DashIconify
import json
import requests

import helpers
import plotly.express as px
import plotly.graph_objects as go
import os
from whitenoise import WhiteNoise

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = ['https://fonts.googleapis.com/css2?family=Poppins:wght@300&display=swap']

app = Dash(__name__, title="TwitterHawk", external_stylesheets=external_stylesheets)
server = app.server
server.wsgi_app = WhiteNoise(server.wsgi_app, root='static/')
# app.css.config.serve_locally = True

json_file = open("comm_final.json")
json_data = json.load(json_file)


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div(
        id="home-page",
        children = [
            html.Header([
                html.H1(f'Welcome to TwitterHawk')]),
            html.Aside([
                html.Div(
                    className='home',
                    children=[
                        html.P('Enter your twitter handle'),
                        html.Div([
                            html.P('@'),
                            dcc.Input(id='handle', type='text', debounce=True)
                        ], style={'display': 'flex', 'text-align': 'justify'}),
                        dcc.Link(html.Button(id='submit-button', type='submit', children='Submit'), href='/page-2')
                    ])
            # debounce making sure enter is pressed

            ])
        ]
    ),
])

def create_word_web(json_data):
    topics = json_data["topic_engagement"]
    word_web_dict = {}
    for key in topics:
        topic_score = topics[key]
        if(topic_score > 0):
            word_web_dict[key] = topic_score

    word_scores = str(word_web_dict)

    engagementScores = list(word_web_dict.items())
    engagementScores.sort(key=lambda tup: tup[1], reverse = True)
    while(engagementScores[0][1] > 1000):
        for i in range(len(engagementScores)):
            engagementScores[i] = (engagementScores[i][0], int(engagementScores[i][1]/10))

    word_web_text = ""
    for word in engagementScores:
        for i in range(word[1]):
            word_web_text += word[0] + " "

    resp = requests.post('https://quickchart.io/wordcloud', json={
        'format': 'png',
        'width': 500,
        'height': 500,
        'fontScale': 15,
        'rotation': 0.01,
        'scale': 'linear',
        'colors': ['black'],
        'removeStopwords': 'true',
        'text': word_web_text
    })

    with open('newscloud.png', 'wb') as f:
        f.write(resp.content)

    del engagementScores[min(5, len(engagementScores)):]
    tooltipString = ""
    for i in range(len(engagementScores)):
        tooltipString += str(engagementScores[i][0]) + ": " + str(engagementScores[i][1]) + "\n"

    return tooltipString

@app.callback(
    # Output('out', 'children'),
    # Output('err', 'children'),
    Output('home-page','children'),
    Output('page-content', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('url', 'pathname')],
    [State('handle', 'value')]
)

def show_handle(clicks, pathname, handle):
    if handle is None:
        # PreventUpdate prevents ALL outputs updating
        raise dash.exceptions.PreventUpdate
    if clicks is not None and handle is not None:
        if pathname == "/page-2":
            # some call to access/analysis which creates "json data"
            os.system(f"python3 src/comm_api.py {handle}")
            user_file = open("comm_output.json")
            user_data = json.load(user_file)
            tooltipString = create_word_web(user_data)
            #tooltipString = ""
            return [[], user_info(user_data, handle, tooltipString)]

def user_info(json_data, username, tooltipString):
    #tooltipString = create_word_web(json_data)
    loyalFollowerData = json_data["longest_follower"]["created_at"].split("-")
    loyalFollowerStr = loyalFollowerData[1] + "/" + loyalFollowerData[2].split("T")[0] + "/" + loyalFollowerData[0]
    loyalFollowerHandle = str(json_data["longest_follower"]["username"])
    loyalFollowerLikes = 0

    interest_json = json_data["top_interests"]
    top_interests = list(interest_json.keys())
    int_list_data = []
    for i in range(len(top_interests)):
        int_list_data.append((top_interests[i],interest_json[top_interests[i]] ))

    lfStr = str("Your most loyal follower: " + loyalFollowerHandle)
    lfDateStr = str(loyalFollowerHandle + " has followed you since " + loyalFollowerStr + ".")
    lfLikeStr = "You two go way back."
    #lfLikeStr = str(loyalFollowerHandle + " has liked " + str(loyalFollowerLikes) + " of your tweets.")
    #https://twitter.com/barackobama/status/552767187694661632

    topTweetStr = '<blockquote class="twitter-tweet"><a href=https://twitter.com/user/status/' + json_data["most_popular_tweet"] + '></a></blockquote><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'
    posTweetStr = '<blockquote class="twitter-tweet"><a href=https://twitter.com/user/status/' + json_data["most_positive_tweet"]+ '></a></blockquote><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'
    negTweetStr = '<blockquote class="twitter-tweet"><a href=https://twitter.com/user/status/' + json_data["most_negative_tweet"]+ '></a></blockquote><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'

    sentiment = (json_data["overall_compound_score"] + 1) / 2
    sentiment_strings = helpers.sentiment_score(sentiment)
    sentiment_percent = helpers.sentiment_breakdown(sentiment)

    times = json_data["time_engagement"]

    page_2_layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Header([
            html.H1(['Welcome to TwitterHawk, ', html.A('@' + username, href=f'https://twitter.com/{username}')]),
            # html.H1(f'Welcome to TwitterHawk, @{username}'),
            DashIconify(icon="fa-solid:fa-bars")
        ]),
        html.Aside([
            html.Div(
                className="row",
                children = [
                html.Section([
                    # dcc.Link(html.Button(id='submit-button', type='submit', children='Submit'), href='/page-2')
                    html.H2(['Your most loyal follower: ', html.A('@' + loyalFollowerHandle, href=f'https://twitter.com/{loyalFollowerHandle}')]),
                    html.P(lfDateStr),
                    html.P(lfLikeStr),
                    ]),
                html.Section([
                    html.H2("Your most popular tweet:"),
                    html.Iframe(className = "tweet", srcDoc = topTweetStr, height = 300, width = 400)
                ]),
                html.Section([
                    html.H2("Your favorite topics to tweet about:"),
                    html.Ol(
                        [
                            html.Li(str(int_list_data[0][0] + ": " + str(int_list_data[0][1]))),
                            html.Li(str(int_list_data[1][0] + ": " + str(int_list_data[1][1]))),
                            html.Li(str(int_list_data[2][0] + ": " + str(int_list_data[2][1])))
                        ]
                    )
                ]),
            ]),
            html.Div(
                className="row2",
                children = [
                html.Section([
                        html.H2("Your most positive tweet:"),
                        html.Iframe(className = "tweet", srcDoc = posTweetStr, height = 300, width = 400)
                ]),
                html.Section([
                    html.H2("On twitter, you tend to be " + sentiment_strings[0]),
                    html.P(sentiment_strings[1]),
                    dcc.Graph(id="graph", figure=helpers.generate_chart(sentiment, username))
                    ]),
                html.Section([
                        html.H2("Your most negative tweet:"),
                        html.Iframe(className = "tweet", srcDoc = negTweetStr, height = 300, width = 400)
                ])
                ]),
            html.Div(
                className="row3",
                children = [
                html.Section([
                        html.H2("Your most engaging topics"),
                            html.Img(src = "newscloud.png",id="wordcloud"),
                            html.H4("Top engagement scores:"),
                            html.P(tooltipString, className = "engagementScores")
                ]),
                html.Section([
                    html.H2("You get the most engagement during these times..."),
                    dcc.Graph(
                        figure={
                            'data': [
                                {'x': list(times.keys()), 'y': list(times.values()), 'type': 'bar', 'name': 'Times',
                                'marker' : { "color" : '#1DA1F2'}}
                            ],
                            'layout': {
                                # 'title': 'Times you Tweet',
                                'figure.layout.autosize': True,
                                # 'config.responsive': True,
                                'figure.layout.height': '300px',
                                # 'xaxis':{
                                #     'title':'Time of Day'
                                # },
                                'yaxis':{
                                    'title':'Engagement'
                                }
                            },
                        }
                    )
                ]),
                html.Section([
                    html.H2("You can get a little emotional on Twitter..."),
                    dcc.Graph(id="graph2", figure=helpers.generate_sentiment_chart(json_data))
                    ]),
                ]),
            html.Div(
                className="bottom",
                children =
                [
                    html.H2("Share TwitterHawk with your Network!"),
                    html.Iframe(srcDoc = '<a href="https://twitter.com/share?ref_src=twsrc%5Etfw" class="twitter-share-button" data-size="large" data-text="Everyone go check out TwitterHawk, the newest Twitter analysis tool!" data-url="https://twitterhawk.com" data-show-count="false">Tweet</a><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>', width = 100, height = 100)
                ])
        ]),
        html.P(id='err', style={'color': 'red'}),
        html.P(id='out')
    ])
    return page_2_layout

if __name__ == '__main__':
    #app.run_server(debug=True, dev_tools_hot_reload = False)
    app.run_server(debug=False, host='0.0.0.0', port=8050)
