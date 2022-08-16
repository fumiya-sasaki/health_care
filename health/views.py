from django.views import generic
from health import forms

from health.forms import HealthSerchForm, WeightCreateForm
from django.contrib import messages  # 追加
from django.shortcuts import redirect  # 追加
from health.models import Detail, Weight
from django.urls import reverse_lazy
import numpy as np
import pandas as pd
import datetime
from django_pandas.io import read_frame
from .plugin_plotly import GraphGenerator
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin


class LoginView(LoginView):
    """ログインページ"""
    form_class = forms.LoginForm
    template_name = "health/login.html"


class LogoutView(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = "health/login.html"


class WeightList(LoginRequiredMixin, generic.ListView):
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


class WeightCreate(LoginRequiredMixin, generic.CreateView):
    template_name = 'health/register.html'
    model = Weight
    form_class = WeightCreateForm
    success_url = reverse_lazy('health:weight_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '体重登録'
        return context

    def form_valid(self, form):
        detail = Detail.objects.get(id=1)
        weight = form.cleaned_data['weight']
        bmi = weight / ((detail.height / 100) ** 2)
        season_number = 0
        date = form.cleaned_data['date']
        year = int(date.strftime("%Y"))
        first = datetime.datetime(year, 4, 1).date()
        latter = datetime.datetime(year, 10, 1).date()
        if first <= date and latter > date:
            season_number = 1
        # 体脂肪率＝(3.02 + 0.461×体重(kg) - 6.85×(男性１,女性0) - 0.089×身長(cm) + 0.038×年齢(歳) - 0.238×(冬0、夏1))÷体重×100
        body_fat = (3.02 + 0.461 * weight - (6.85 * detail.gender) - 0.089 *
                    detail.height + 0.038 * detail.age - (0.238 * season_number)) / weight * 100
        form.instance.body_fat = round(body_fat, 1)
        form.instance.bmi = round(bmi, 1)

        return super(WeightCreate, self).form_valid(form)


class WeightUpdate(LoginRequiredMixin, generic.UpdateView):
    template_name = 'health/register.html'
    model = Weight
    form_class = WeightCreateForm
    success_url = reverse_lazy('health:weight_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '体重更新'
        return context

    def form_valid(self, form):
        detail = Detail.objects.get(id=1)
        weight = form.cleaned_data['weight']
        bmi = weight / ((detail.height / 100) ** 2)
        season_number = 0
        year = int(form.cleaned_data['date'].strftime("%Y"))
        first = datetime.datetime(year, 4, 1).date()
        latter = datetime.datetime(year, 10, 1).date()
        if first <= form.cleaned_data['date'] and latter > form.cleaned_data['date']:
            season_number = 1
        # 体脂肪率＝(3.02 + 0.461×体重(kg) - 6.85×(男性１,女性0) - 0.089×身長(cm) + 0.038×年齢(歳) - 0.238×(冬0、夏1))÷体重×100
        body_fat = (3.02 + 0.461 * weight - (6.85 * detail.gender) - 0.089 *
                    detail.height + 0.038 * detail.age - (0.238 * season_number)) / weight * 100
        form.instance.body_fat = round(body_fat, 1)
        form.instance.bmi = round(bmi, 1)

        self.object = weight = form.save()
        messages.info(self.request,
                      f'体重を更新しました\n'
                      f'日付:{weight.date}\n')
        return redirect(self.get_success_url())


class WeightDelete(LoginRequiredMixin, generic.DeleteView):
    """支出削除"""
    template_name = 'health/delete.html'
    model = Weight

    def get_success_url(self):
        return reverse_lazy('health:weight_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '体重削除確認'

        return context

    def delete(self, request, *args, **kwargs):
        self.object = weight = self.get_object()
        weight.delete()
        return redirect(self.get_success_url())


class MonthDashboard(LoginRequiredMixin, generic.TemplateView):
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

        detail = Detail.objects.get(id=1)
        df = read_frame(queryset,
                        fieldnames=['date', 'weight', 'body_fat', 'bmi'])

        # グラフ作成クラスをインスタンス化
        gen = GraphGenerator()

        season_number = 0
        date = df['date'][len(df['date']) - 1]
        first = datetime.datetime(year, 4, 1).date()
        latter = datetime.datetime(year, 10, 1).date()
        if first <= date and latter > date:
            season_number = 1

        # # totalの数字を計算して渡す
        context['average'] = round(
            df['weight'].sum() / len(df['weight']), 1)

        context['ave_fat'] = round(
            df['body_fat'].sum() / len(df['body_fat']), 1)

        context['ave_bmi'] = round(
            df['bmi'].sum() / len(df['bmi']), 1)

        context['appropriate'] = round((detail.height / 100) ** 2 * 22, 1)
        context['height'] = detail.height
        context['gender'] = '男性' if detail.gender == 1 else '女性'
        context['age'] = detail.age
        context['leaving_work'] = round(97.8 + 13.9 * df['weight'][len(
            df['weight']) - 1] + 176.8 * detail.gender + 2.29 * detail.height - 0.97 * detail.age + 6.13 * season_number, 1)

        # 日別の棒グラフの素材を渡す
        df_weight = pd.pivot_table(
            df, index='date', values='weight')
        df_body_fat = pd.pivot_table(
            df, index='date', values='body_fat')
        df_bmi = pd.pivot_table(
            df, index='date', values='bmi')
        dates = list(df_weight.index.values)
        weight_heights = [val[0] for val in df_weight.values]
        body_fat_heights = [val[0] for val in df_body_fat.values]
        bmi_heights = [val[0] for val in df_bmi.values]

        plot_bar = gen.month_daily_bar(
            x_weight=dates,
            y_weight=weight_heights,
        )

        plot_line = gen.month_daily_line(
            x_body_fat=dates,
            y_body_fat=body_fat_heights,
            x_bmi=dates,
            y_bmi=bmi_heights
        )
        context['plot_bar'] = plot_bar
        context['plot_line'] = plot_line

        return context
