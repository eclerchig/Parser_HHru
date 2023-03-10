from django.http import JsonResponse
from django.shortcuts import render
from .scripts.parsing.to_parse import start
from .scripts.reporting.reporter import create_tokens
from .scripts.draw_plots.draw_plots import draw_bar_chart, draw_table

report = create_tokens()


def index(request):
    range_slider = 0
    display = {
        'tokens': False,
        'spinner': False
    }
    data = {'display': display}
    if request.method == 'POST' and 'to_parse' in request.POST:
        start()
        report.generate_tokens()
        display['tokens'] = True
        display['spinner'] = False
        range_slider = report.get_count_tokens()
    if report.get_skills() is not None:
        data = {
            'tokens_df': report.get_tokens_sliced(0, range_slider),
            'display': display,
            'range_slider': range_slider,
            'clouds_code': report.generate_cloud_code(0, range_slider)
        }
    return render(request, 'main/index.html', context=data)


def update_clouds_tokens(request):
    ranges = request.GET.getlist('ranges[]')
    response = {
        'clouds_code': report.generate_cloud_code(int(ranges[0]), int(ranges[1]))
    }
    return JsonResponse(response)


def update_charts(request):
    token = request.GET.get('token')
    pivot = report.get_pivot()
    vacs = pivot[pivot[token] > 0].sort_index().index.unique()
    print('token\n', token)
    print('skills before\n', report.get_skills())
    skills = report.get_skills().query('name_vac in @vacs') \
        .groupby(by='name_skill', as_index=False) \
        .agg({'name_vac': 'count'}) \
        .sort_values(by='name_vac', ascending=False).head(20)
    print('skills after\n', skills)
    df_vacs = report.get_vacs_by_token(token)
    bar_chart = draw_bar_chart(skills, 'name_skill', 'name_vac')
    response = {
        'bar_data': bar_chart['data'],
        'bar_layout': bar_chart['layout'],
        'table_data': draw_table(df_vacs, titles=['Вакансии', 'Адрес'])
    }
    return JsonResponse(response)
