import json
from pathlib import Path

class DataExporter:
    """Gestor para exportar datos extraídos a formato JSON."""

    @staticmethod
    def to_json(data: list[dict] | dict, filename: str) -> None:
        """Guarda la información estructurada en un archivo JSON legible."""
        output_path = Path(filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[+] Archivo JSON guardado exitosamente: {output_path.resolve()}")