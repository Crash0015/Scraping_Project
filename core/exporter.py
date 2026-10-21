import csv
import json
from pathlib import Path

class DataExporter:
    """Gestor para exportar datos extraídos a JSON y CSV."""

    @staticmethod
    def to_json(data: list[dict] | dict, filename: str) -> None:
        """Guarda la información en formato JSON."""
        output_path = Path(filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[+] Archivo JSON guardado: {output_path.resolve()}")

    @staticmethod
    def to_csv(data: list[dict], filename: str) -> None:
        """Guarda la lista de diccionarios en un archivo CSV."""
        if not data:
            print("[-] Sin datos para CSV.")
            return

        output_path = Path(filename)
        fieldnames = list(data[0].keys())

        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"[+] Archivo CSV guardado: {output_path.resolve()}")