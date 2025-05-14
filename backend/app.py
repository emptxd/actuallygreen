import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.abspath(os.path.join(BASE_DIR, "../templates"))
STATIC_DIR   = os.path.abspath(os.path.join(BASE_DIR, "../static"))

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)

# --- SQLAlchemy setup ---
db_path = os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ─── Summary model ───
class SummaryEmission(db.Model):
    __tablename__ = 'summary_emission'
    id               = db.Column(db.Integer, primary_key=True)
    country          = db.Column(db.String(80), nullable=False)
    year             = db.Column(db.Integer,  nullable=False)
    agriculture      = db.Column(db.Float,    nullable=False)
    energy_supply    = db.Column(db.Float,    nullable=False)
    industry         = db.Column(db.Float,    nullable=False)
    lulu_cf          = db.Column(db.Float,    nullable=False)
    other            = db.Column(db.Float,    nullable=False)
    waste_management = db.Column(db.Float,    nullable=False)
    total_emissions  = db.Column(db.Float,    nullable=False)

    def to_dict(self):
        return {
            'country':          self.country,
            'year':             self.year,
            'Agriculture':      self.agriculture,
            'Energy (supply)':  self.energy_supply,
            'Industry':         self.industry,
            'LULUCF':           self.lulu_cf,
            'Other':            self.other,
            'Waste management': self.waste_management,
            'Total':            self.total_emissions,
        }
# Create DB + tables if they don't exist
with app.app_context():
    db.create_all()

# --- Existing routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/emissions')
def emissions():
    return render_template('emissions.html')



@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/targets')
def targets():
    return render_template('targets.html')


# ——— Query route ———
@app.route('/query')
def query():
    # filter parameters
    country   = request.args.get('country',   '',      type=str)
    year_from = request.args.get('year_from', 1990,    type=int)
    year_to   = request.args.get('year_to',   2023,    type=int)

    # dropdown options
    countries = [c[0] for c in db.session.query(SummaryEmission.country)
                             .distinct().order_by(SummaryEmission.country)]
    years     = [y[0] for y in db.session.query(SummaryEmission.year)
                             .distinct().order_by(SummaryEmission.year)]

    # base query
    q = SummaryEmission.query.filter(SummaryEmission.year.between(year_from, year_to))
    if country:
        q = q.filter_by(country=country)
    rows = q.order_by(SummaryEmission.country, SummaryEmission.year).all()

    # prepare data for template
    summary = [r.to_dict() for r in rows]
    # fixed sector order:
    sectors = ["Agriculture","Energy (supply)","Industry","LULUCF","Other","Waste management"]

    return render_template(
        'query.html',
        summary=summary,
        countries=countries,
        years=years,
        selected_country=country,
        year_from=year_from,
        year_to=year_to,
        sectors=sectors
    )

if __name__ == '__main__':
    app.run(debug=True)