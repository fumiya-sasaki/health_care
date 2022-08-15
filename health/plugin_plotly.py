import plotly.graph_objects as go


class GraphGenerator:
    """ビューから呼び出されて、グラフをhtmlにして返す"""

    def month_pie(self, labels, values):
        """月間支出のパイチャート"""
        fig = go.Figure()
        fig.add_trace(go.Pie(labels=labels,
                             values=values))

        return fig.to_html(include_plotlyjs=False)

    def month_daily_bar(self,
                        x_weight,
                        y_weight):
        """月間支出の日別バーチャート"""
        fig = go.Figure()
        fig.update_xaxes(tickformat="%Y-%m-%d")
        fig.update_layout(title=dict(text='<b>月間体重推移',
                                     font=dict(size=22,
                                               color='grey'),
                                     y=0.88),
                          xaxis=dict(title='日付（日）'),
                          yaxis=dict(title='体重（Kg）'),)
        fig.add_trace(go.Scatter(
            x=x_weight,
            y=y_weight,
            mode='lines+markers',
            name='体重',
            line=dict(width=5),
            marker=dict(size=10, symbol='circle'),
        ))

        return fig.to_html(include_plotlyjs=False)

    def month_daily_line(self,
                         x_body_fat,
                         y_body_fat,
                         x_bmi,
                         y_bmi):
        """月間支出の日別バーチャート"""
        fig = go.Figure()
        fig.update_xaxes(tickformat="%Y-%m-%d")
        fig.update_layout(title=dict(text='<b>月間体脂肪/BMI推移',
                                     font=dict(size=22,
                                               color='grey'),
                                     y=0.88),
                          xaxis=dict(title='日付（日）'),
                          yaxis=dict(title='体脂肪/BMI（%）')
                          )
        fig.add_trace(go.Scatter(
            x=x_body_fat,
            y=y_body_fat,
            mode='lines+markers',
            name='体脂肪率',
            line=dict(width=4),
            marker=dict(size=7, symbol='circle'),
        ))

        fig.add_trace(go.Scatter(
            x=x_bmi,
            y=y_bmi,
            mode='lines+markers',
            name='BMI',
            line=dict(width=4),
            marker=dict(size=7, symbol='circle'),
        ))
        return fig.to_html(include_plotlyjs=False)
