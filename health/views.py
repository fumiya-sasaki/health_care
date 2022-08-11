from django.views import generic

from health.forms import HealthSerchForm, WeightCreateForm
from django.contrib import messages  # 追加
from django.shortcuts import redirect  # 追加
from health.models import Weight
from django.urls import reverse_lazy
import numpy as np
import pandas as pd
import datetime
from django_pandas.io import read_frame
from .plugin_plotly import GraphGenerator
# Create your views here.


class WeightList(generic.ListView):
    template_name = 'health/weight_list.html'
    model = Weight
    ordering = '-date'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = form = HealthSerchForm(self.request.GET or None)
        if form.is_valid():
            year = form.cleaned_data.get('year')
            # 何も選択されていないときは0の文字列が入るため、除外
            if year and year != '0':
                queryset = queryset.filter(date__year=year)

                # 何も選択されていないときは0の文字列が入るため、除外
            month = form.cleaned_data.get('month')
            if month and month != '0':
                queryset = queryset.filter(date__month=month)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # search formを渡す
        context['search_form'] = self.form
        return context


class WeightCreate(generic.CreateView):
    template_name = 'health/register.html'
    model = Weight
    form_class = WeightCreateForm
    success_url = reverse_lazy('health:weight_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '体重登録'
        return context

    def form_valid(self, form):
        weight = form.cleaned_data['weight']
        season_number = 0
        currentDateTime = datetime.datetime.now()
        date = currentDateTime.date()
        year = int(date.strftime("%Y"))
        print(datetime.datetime(year, 4, 1))
        if datetime.datetime(year, 4, 1).date() <= form.cleaned_data['date'] and datetime.datetime(year,10, 1).date() > form.cleaned_data['date']:
            season_number = 1
        body_fat = (3.02 + 0.461 * weight - 6.85 * season_number - 0.089 *
            171 + 0.038 * 28 - 0.238) / weight * 100
        Weight.objects.create(
        date=form.cleaned_data['date'],
        weight=weight,
        body_fat=round(body_fat, 1)
        )
        return super(WeightCreate, self).form_valid(form)


class WeightUpdate(generic.UpdateView):
    template_name = 'health/register.html'
    model = Weight
    form_class = WeightCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '体重更新'
        print('************', kwargs)
        return context

    def get_success_url(self):
        return reverse_lazy('health:weight_list')

    def form_valid(self, form):
        self.object = weight = form.save()
        # messages.info(self.request,
        #               f'支出を更新しました\n'
        #               f'日付:{weight.date}\n'
        #               f'カテゴリ:{weight.category}\n'
        #               f'金額:{weight.price}円')
        return redirect(self.get_success_url())


class WeightDelete(generic.DeleteView):
    """支出削除"""
    template_name = 'health/delete.html'
    model = Weight

    def get_success_url(self):
        return reverse_lazy('health:weight_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print('*******************', kwargs)
        context['page_title'] = '体重削除確認'

        return context

    def delete(self, request, *args, **kwargs):
        self.object = weght = self.get_object()

        weght.delete()
        # messages.info(self.request,
        #               f'支出を削除しました\n'
        #               f'日付:{weght.date}\n'
        #               f'カテゴリ:{weght.category}\n'
        #               f'金額:{weght.price}円')
        return redirect(self.get_success_url())


class MonthDashboard(generic.TemplateView):
    """月間支出ダッシュボード"""
    template_name = 'health/month_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # これから表示する年月
        year = int(self.kwargs.get('year'))
        month = int(self.kwargs.get('month'))
        context['year_month'] = f'{year}年{month}月'

        # 前月と次月をコンテキストに入れて渡す
        if month == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month - 1

        if month == 12:
            next_year = year + 1
            next_month = 1
        else:
            next_year = year
            next_month = month + 1
        context['prev_year'] = prev_year
        context['prev_month'] = prev_month
        context['next_year'] = next_year
        context['next_month'] = next_month

        # paymentモデルをdfにする
        queryset = Weight.objects.filter(date__year=year)
        queryset = queryset.filter(date__month=month)
        # クエリセットが何もない時はcontextを返す
        # 後の工程でエラーになるため
        if not queryset:
            return context

        df = read_frame(queryset,
                        fieldnames=['date', 'weight', 'body_fat'])

        # グラフ作成クラスをインスタンス化
        gen = GraphGenerator()

        # # pieチャートの素材を作成
        # df_pie = pd.pivot_table(df, index='category', values='price', aggfunc=np.sum)
        # pie_labels = list(df_pie.index.values)
        # pie_values = [val[0] for val in df_pie.values]
        # plot_pie = gen.month_pie(labels=pie_labels, values=pie_values)
        # context['plot_pie'] = plot_pie

        # # テーブルでのカテゴリと金額の表示用。
        # # {カテゴリ:金額,カテゴリ:金額…}の辞書を作る
        # context['table_set'] = df_pie.to_dict()['price']

        # # totalの数字を計算して渡す
        context['total_payment'] = df['weight'].sum() / len(df['weight'])

        # 日別の棒グラフの素材を渡す
        df_bar = pd.pivot_table(
            df, index='date', values='weight', aggfunc=np.sum)
        dates = list(df_bar.index.values)
        heights = [val[0] for val in df_bar.values]
        plot_bar = gen.month_daily_bar(x_list=dates, y_list=heights)
        context['plot_bar'] = plot_bar

        return context
