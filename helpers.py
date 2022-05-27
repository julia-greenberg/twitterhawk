import plotly.graph_objects as go

def sentiment_score(sentiment):
    if 0 <= sentiment < .05:
        return ["extremely negative.", "Jeez, lighten up!"]
    if .05 <= sentiment < .2:
        return ["very negative.", "You must be pleasant to be around..."]
    if .2 <= sentiment < .4:
        return ["fairly negative.", "Turn that frown upside down."]
    if .4 <= sentiment < .45:
        return ["slightly negative.", "It's ok to have a bad day sometimes."]
    if .45 <= sentiment < .55:
        return ["neutral.", "Just like Switzerland."]
    if .55 <= sentiment < .6:
        return ["slightly positive.", "Like a close-mouthed smile."]
    if .6 <= sentiment < .8:
        return ["fairly positive.", "Glass half full, eh?"]
    if .8 <= sentiment < .95:
        return ["very positive.", "You have a lot in common with protons!"]
    if .95 <= sentiment <= 1:
        return ["extremely positive.", "A ray of sunshine."]

def sentiment_breakdown(sentiment):
    positive = sentiment 
    negative = 1 - sentiment
    return f"{positive * 100}% \U0001f600 {negative * 100}% \U0001F621"

def generate_chart(sentiment, user):
    labels = ['Positive \U0001f600','Negative \U0001F620']
    values = [sentiment, 1 - sentiment]
    colors = ["green", "red"]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent', title=f"Sentiment Breakdown for @{user}")])
    fig.update_traces(textposition='inside', textinfo='percent+label', hoverinfo='label+percent')
    return fig

    # "sentiments": {
    #     "joy": 15,
    #     "anger": 4,
    #     "surprise": 1
    # },
    #  {'x': list(times.keys()), 'y': list(times.values()), 'type': 'bar', 'name': 'Times',
    #                             'marker' : { "color" : '#1DA1F2'}}
def generate_sentiment_chart(json_data):
    sentiments = json_data["sentiments"]
    labels =  list(sentiments.keys())
    values = list(sentiments.values())
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent')])
    fig.update_traces(textposition='inside', textinfo='percent+label', hoverinfo='label+percent')
    return fig
