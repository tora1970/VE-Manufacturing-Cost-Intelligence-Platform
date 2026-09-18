from utils.loader import MasterDataLoader

loader = MasterDataLoader()

masterdata = loader.load_all()

print("\nMASTERDATA LOADED")

for name, df in masterdata.items():

    print("-" * 50)
    print(name)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
