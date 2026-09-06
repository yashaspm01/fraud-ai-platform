import shutil
from pathlib import Path
import kagglehub

DEST_PATH = Path("pipelines/data/raw/paysim.csv")


def main():
    print("Downloading PaySim dataset via kagglehub...")
    path = kagglehub.dataset_download("mtalaltariq/paysim-data")
    print(f"Downloaded to cache: {path}")

    downloaded_dir = Path(path)
    csv_files = list(downloaded_dir.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"No CSV found in downloaded dataset at {path}")

    source_csv = csv_files[0]
    DEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(source_csv, DEST_PATH)

    print(f"✅ Copied to: {DEST_PATH}")


if __name__ == "__main__":
    main()
