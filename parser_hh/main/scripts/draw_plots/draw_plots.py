def draw_bar_chart(df, col1, col2):
    bar_chart = {
        'data': {},
        'layout': {}
    }
    if df is not None:
        data = {
            'x': df[col1].to_list(),
            'y': df[col2].to_list(),
            'type': 'bar',
            'orientation': 'v'
        }
        layout = {
            'title': 'ТОП-20 НАВЫКОВ',
            'title_x': 0.5,
            'title_font_family': "Arial Black",
            'xaxis': {
                'title': 'Навыки/Требования',
                'offset': 5,
                'title_font_size': 20
            },
            'yaxis': {
                'title': 'Кол-во появлений',
                'title_font_size': 20
            },
            'dy': 1,
            'margin': {
                'b': 200
            }
        }
        bar_chart = {
            'data': [data],
            'layout': layout
        }
    return bar_chart


def draw_table(df, titles):
    data = {}
    if 'url_hh' in df.columns:
        df['url_hh'] = df['url_hh'].map(lambda url : f'<a href="{url}">{url}</a>')
    if df is not None:
        values = [df[col].to_list() for col in df.columns]

        data = [{
            'type': 'table',
            'header': {
                'values': [[col.upper()] for col in titles],
                'align': ['center'],
                'line': {'width': 2, 'color': 'white'},
                'fill': {'color': "#1f77b4"},
                'font': {'size': 20, 'color': 'white', 'family': 'Arial'}
            },
            'cells': {
                'values': values,
                'align': ['left', 'center'],
                'line': {'width': 2, 'color': 'white'},
                'fill': {'color': 'rgb(231 231 231)'},
                'font': {'size': 17, 'color': ["black"], 'family': 'Arial'}
            }
        }]
    return data
