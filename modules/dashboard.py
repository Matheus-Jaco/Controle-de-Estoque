from flask import Blueprint, render_template, session
from models import product_summary, report_summary, monthly_chart_data


dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@dashboard_bp.route('/inicial')
@dashboard_bp.route('/inicio')
@dashboard_bp.route('/deasheboard')
@dashboard_bp.route('/admin')
def view_dashboard():
    summary = product_summary()
    report = report_summary()
    chart_data = monthly_chart_data()
    return render_template('dashboard.html', summary=summary, report=report, chart_data=chart_data, title='Inicial')
