from argparse import ArgumentParser
from xgboost import XGBRegressor

import pandas as pd

# parse args
parser = ArgumentParser(description='Convert between different phosphorus metrics.')
parser.add_argument('src_metric', type=str, help='Name of the source metric. '
                                                 'Must be one of ["Olsen", "tot", "M3", "ox", "BD"]')
parser.add_argument('tgt_metric', type=str, help='Name of the target metric. '
                                                 'Must be one of ["Olsen", "tot", "M3", "ox", "BD"]')
parser.add_argument('-i', '--input', type=str, help='Path to the input .csv file.')
parser.add_argument('-o', '--output', type=str, help='Path to the output .csv file.',
                    required=False, default=None)

args = parser.parse_args()

if args.output is None:
    args.output = f'./{args.tgt_metric}_pred.csv'

# validate args
valid_metrics = ['Olsen', 'tot', 'M3', 'ox', 'BD']
assert args.src_metric in valid_metrics, 'Invalid source metric name'
assert args.tgt_metric in valid_metrics, 'Invalid target metric name'
assert args.src_metric != args.tgt_metric, 'Source and target metrics must be different'

# validate data
df = pd.read_csv(args.input)
features = [f'{args.src_metric}_P_mg_kg', 'pH', 'TOC_g_kg', '% Clay', '% Silt', '% Sand']
for f in features:
    assert f in df.columns, f'Missing feature: {f}'

# run model
model = XGBRegressor()
model.load_model(f'model/xgb_{args.src_metric}_{args.tgt_metric}.json')

pred = model.predict(df[features])
df.insert(len(df.columns), f'{args.tgt_metric}_P_mg_kg_pred', pred)
df.to_csv(args.output, index=False)
