import os
import requests

from scraper import PDF_URLS

folder_name = "Catechism_PDFs"
os.makedirs(folder_name, exist_ok=True)

for number, url in PDF_URLS:
    filename = url.split("/")[-1]
    prefix = str(number).zfill(2)
    filepath = os.path.join(folder_name, f"{prefix}_{filename}")

    print(f"Downloading #{number}: {filename}...")

    try:
        req = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        req.raise_for_status()

        with open(filepath, 'wb') as f:
            f.write(req.content)

    except requests.exceptions.RequestException as e:
        print(f"Failed to download #{number}: {e}")

print("All downloads finished!")
