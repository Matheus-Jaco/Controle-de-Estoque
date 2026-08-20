from flask import Blueprint, render_template
from models import report_summary

from datetime import datetime

reports_bp = Blueprint('reports', __name__, url_prefix='/reports', template_folder='../templates')


@reports_bp.route('')
def reports_view():
    summary = report_summary()
    months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    now = datetime.now()
    current_period = f"{months[now.month - 1]} de {now.year}"
    current_time = now.strftime('%d/%m/%Y às %H:%M')
    return render_template('reports.html', summary=summary, title='Relatórios', current_period=current_period, current_time=current_time)
