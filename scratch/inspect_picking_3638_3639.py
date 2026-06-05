import pickle

with open('app/cache/picking_cache.pkl', 'rb') as f:
    data = pickle.load(f)

for k, v in data['data'].items():
    if '100003638' in k or '100003639' in k:
        print(f"WO {k}: {v}")
