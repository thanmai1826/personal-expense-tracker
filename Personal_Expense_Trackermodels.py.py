"""
Database models for the Personal Expense Tracker.
"""
from datetime import datetime
from Personal_Expense_Tracker import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    """
    Load user from database by ID.
    
    Args:
        user_id (int): User ID
    
    Returns:
        User: User object or None
    """
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """
    User model for authentication and authorization.
    
    Attributes:
        id (int): Primary key
        username (str): Unique username
        email (str): User email address
        password_hash (str): Hashed password
        role (str): User role (admin/user)
        created_at (datetime): Account creation timestamp
        expenses (relationship): Related expense records
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to expenses
    expenses = db.relationship('Expense', backref='user', lazy=True,
                               cascade='all, delete-orphan')
    
    def __repr__(self):
        """String representation of User."""
        return f'<User {self.username}>'
    
    @property
    def password(self):
        """
        Prevent password from being accessed.
        
        Raises:
            AttributeError: Password is not readable
        """
        raise AttributeError('Password is not readable')
    
    @password.setter
    def password(self, password):
        """
        Set password hash.
        
        Args:
            password (str): Plain text password
        """
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """
        Verify password against hash.
        
        Args:
            password (str): Plain text password
        
        Returns:
            bool: True if password matches
        """
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        """Check if user is admin."""
        return self.role == 'admin'
    
    def get_total_expenses(self):
        """Calculate total expenses for user."""
        return sum(expense.amount for expense in self.expenses)
    
    def get_expenses_by_category(self):
        """Get expenses grouped by category."""
        from sqlalchemy import func
        return db.session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter_by(user_id=self.id).group_by(Expense.category).all()
    
    def get_monthly_expenses(self, year=None, month=None):
        """Get expenses for specific month."""
        from sqlalchemy import func
        query = db.session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter_by(user_id=self.id)
        
        if year:
            query = query.filter(func.strftime('%Y', Expense.date) == str(year))
        if month:
            query = query.filter(func.strftime('%m', Expense.date) == str(month).zfill(2))
        
        return query.group_by(Expense.category).all()


class Expense(db.Model):
    """
    Expense model for tracking user expenses.
    
    Attributes:
        id (int): Primary key
        user_id (int): Foreign key to User
        amount (float): Expense amount
        category (str): Expense category
        date (date): Expense date
        description (str): Optional description
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Last update timestamp
    """
    
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                           onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        """String representation of Expense."""
        return f'<Expense ${self.amount} - {self.category}>'
    
    def to_dict(self):
        """Convert expense to dictionary."""
        return {
            'id': self.id,
            'amount': self.amount,
            'category': self.category,
            'date': self.date.strftime('%Y-%m-%d'),
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }