import sys
import os

# Ensure the root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
app = create_app('production')

with app.app_context():
    from app.models.order import get_picking_data, PICKING_CACHE
    get_picking_data()
    raw_df = PICKING_CACHE.get('raw_df')
    
    if raw_df is not None:
        print("Columns in raw_df:")
        print(raw_df.columns.tolist())
        print(f"\nTotal rows in raw_df: {len(raw_df)}")
        if len(raw_df) > 0:
            print("\nFirst 5 rows in raw_df:")
            for idx, row in raw_df.head(5).iterrows():
                print(f"Row {idx}:")
                for col in raw_df.columns:
                    print(f"  {col}: {row[col]}")
        else:
            print("raw_df is empty!")
    else:
        print("raw_df is None!")
