"""
Dashboard routes for analytics and overview.
"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from Personal_Expense_Tracker import db
from Personal_Expense_Tracker.models import Expense
from sqlalchemy import func
from datetime import datetime, timedelta

# Create blueprint
dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/')
@login_required
def index():
    """
    Main dashboard route.
    
    Returns:
        rendered template: Dashboard with analytics
    """
    user_id = current_user.id
    
    # Get date range for current month
    today = datetime.now()
    first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Total expenses
    total_expenses = db.session.query(func.sum(Expense.amount))\
        .filter_by(user_id=user_id).scalar() or 0.0
    
    # Current month expenses
    monthly_expenses = db.session.query(func.sum(Expense.amount))\
        .filter(Expense.user_id == user_id)\
        .filter(Expense.date >= first_day)\
        .scalar() or 0.0
    
    # Get category breakdown
    category_data = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter_by(user_id=user_id).group_by(Expense.category).all()
    
    # Get monthly trend (last 6 months)
    six_months_ago = today - timedelta(days=180)
    monthly_trend = db.session.query(
        func.strftime('%Y-%m', Expense.date).label('month'),
        func.sum(Expense.amount).label('total')
    ).filter(Expense.user_id == user_id)\
     .filter(Expense.date >= six_months_ago)\
     .group_by('month')\
     .order_by('month').all()
    
    # Get recent expenses
    recent_expenses = Expense.query.filter_by(user_id=user_id)\
        .order_by(Expense.date.desc()).limit(5).all()
    
    # Get yearly summary
    current_year = today.year
    yearly_expenses = db.session.query(
        func.strftime('%m', Expense.date).label('month'),
        func.sum(Expense.amount).label('total')
    ).filter(Expense.user_id == user_id)\
     .filter(func.strftime('%Y', Expense.date) == str(current_year))\
     .group_by('month').all()
    
    # Prepare chart data
    categories = [item.category for item in category_data]
    category_totals = [float(item.total) for item in category_data]
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    yearly_data = [0] * 12
    for item in yearly_expenses:
        month_idx = int(item.month) - 1
        if 0 <= month_idx < 12:
            yearly_data[month_idx] = float(item.total)
    
    trend_months = [item.month for item in monthly_trend]
    trend_totals = [float(item.total) for item in monthly_trend]
    
    return render_template(
        'dashboard/index.html',
        title='Dashboard',
        total_expenses=total_expenses,
        monthly_expenses=monthly_expenses,
        categories=zip(categories, category_totals),
        recent_expenses=recent_expenses,
        chart_data={
            'categories': categories,
            'category_totals': category_totals,
            'yearly_data': yearly_data,
            'months': months,
            'trend_months': trend_months,
            'trend_totals': trend_totals
        }
    )


@dashboard.route('/api/stats')
@login_required
def api_stats():
    """
    API endpoint for dashboard statistics.
    
    Returns:
        json: Dashboard statistics
    """
    user_id = current_user.id
    
    # Get statistics
    total_expenses = db.session.query(func.sum(Expense.amount))\
        .filter_by(user_id=user_id).scalar