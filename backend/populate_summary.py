# backend/populate_summary.py

import pandas as pd
import os
from app import app, db, SummaryEmission

CSV_PATH = os.path.join(app.root_path, 'C:/Users/emptb/Documents/actuallygreen/backend/data/CO2_by_country_year.csv')

def main():
    # 1) Read the CSV
    df = pd.read_csv(CSV_PATH)

    # 2) Rename columns to match the SQLAlchemy model
    df = df.rename(columns={
        'Country':            'country',
        'Year':               'year',
        'Agriculture':        'agriculture',
        'Energy (supply)':    'energy_supply',
        'Industry':           'industry',
        'LULUCF':             'lulu_cf',
        'Other':              'other',
        'Waste management':   'waste_management',
        'Total Emissions':    'total_emissions'
    })

    # 3) Ensure correct dtypes and fill NaNs in the six sector columns + total
    df['year']    = df['year'].astype(int)
    df['country'] = df['country'].astype(str)

    numeric_cols = [
        'agriculture',
        'energy_supply',
        'industry',
        'lulu_cf',
        'other',
        'waste_management',
        'total_emissions'
    ]
    # Fill any missing sector / total values with 0, then cast
    df[numeric_cols] = df[numeric_cols].fillna(0).astype(float)

    # 4) Populate the database
    with app.app_context():
        # Drop & recreate only the summary_emission table
        SummaryEmission.__table__.drop(db.engine, checkfirst=True)
        db.create_all()

        objs = [
            SummaryEmission(
                country          = row.country,
                year             = row.year,
                agriculture      = row.agriculture,
                energy_supply    = row.energy_supply,
                industry         = row.industry,
                lulu_cf          = row.lulu_cf,
                other            = row.other,
                waste_management = row.waste_management,
                total_emissions  = row.total_emissions
            )
            for row in df.itertuples()
        ]
        print(f"Inserting {len(objs)} records…")
        db.session.bulk_save_objects(objs)
        db.session.commit()
        print("Done.")

if __name__ == '__main__':
    main()
