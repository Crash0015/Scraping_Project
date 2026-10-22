import json
import math
import os
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv()


class FinancialScamAuditor:
    """Motor de detección de riesgo mediante Embeddings Densos remotos (Google gemini-embedding-001).

    Evalúa biografía y publicaciones en un espacio semántico continuo.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No se encontró GEMINI_API_KEY en el entorno ni en el archivo"
                " .env"
            )

        self.api_url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-embedding-001:batchEmbedContents?key={self.api_key}"
        )

        # Vectores canónicos de captación y fraude en redes
        self.scam_patterns = {
            "RENTABILIDAD_FACIL": (
                "ganar dinero facil rapido en dolares desde casa con celular"
                " sin experiencia inversion"
            ),
            "BOTS_Y_SENALES": (
                "sistema automatico que multiplica dinero senales de trading"
                " garantizadas bot cripto"
            ),
            "DESVIO_CANAL_PRIVADO": (
                "escribeme al whatsapp o telegram cupos limitados ingresa al"
                " link de mi perfil linkbio hotmart"
            ),
            "URGENCIA_PIRAMIDAL": (
                "oportunidad de negocio cambia tu vida financiera ultimos cupos"
                " escribe ya deja tu trabajo"
            ),
        }
        self.pattern_labels = list(self.scam_patterns.keys())
        self.pattern_texts = list(self.scam_patterns.values())

        print(
            "[*] Obteniendo embeddings densos para vectores canónicos de"
            " referencia..."
        )
        self.pattern_embeddings = self._get_embeddings(self.pattern_texts)

    def _get_embeddings(self, texts: list[str]) -> list[list[float]]:
        payload = {
            "requests": [
                {
                    "model": "models/gemini-embedding-001",
                    "content": {"parts": [{"text": t}]},
                }
                for t in texts
            ]
        }

        response = requests.post(
            self.api_url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Error en API Gemini ({response.status_code}): {response.text}"
            )

        data = response.json()
        return [item["values"] for item in data.get("embeddings", [])]

    @staticmethod
    def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def audit_profile_risk(self, json_path: str) -> dict:
        path = Path(json_path)
        if not path.exists():
            return {"error": f"Archivo no encontrado: {json_path}"}

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        profile = data.get("profile", {})
        videos = data.get("videos", [])
        username = profile.get("username", "desconocido")

        # 1. Recolección de textos y metadatos (Biografía + Videos)
        texts_to_analyze = []
        text_metadata = []

        # Evaluar biografía si existe
        bio = profile.get("bio", "").strip()
        if bio:
            texts_to_analyze.append(bio)
            text_metadata.append({
                "origin": "BIOGRAFÍA",
                "url": f"https://www.tiktok.com/@{username}",
                "raw_text": bio,
            })

        # Evaluar publicaciones limpiando plantillas
        for v in videos:
            desc = v.get("description", "").strip()
            if not desc:
                continue

            clean_text = desc
            if clean_text.lower().startswith("creado por"):
                parts = clean_text.split("con la música")
                clean_text = (
                    parts[0]
                    .replace(f"creado por {profile.get('nickname', '')}", "")
                    .replace("creado por", "")
                    .strip()
                )

            final_text = clean_text if len(clean_text) > 3 else desc
            if len(final_text) > 3:
                texts_to_analyze.append(final_text)
                text_metadata.append({
                    "origin": "PUBLICACIÓN",
                    "url": v.get("url", ""),
                    "raw_text": final_text,
                })

        if not texts_to_analyze:
            return {
                "audited_profile": f"@{username}",
                "elements_analyzed": 0,
                "flagged_events_count": 0,
                "global_risk_index": "0.0 / 100",
                "verdict": (
                    "PERFIL CONFORME (Sin texto descriptivo ni biografía"
                    " analizable)"
                ),
                "flagged_cases": [],
            }

        print(
            f"[*] Generando embeddings para {len(texts_to_analyze)} elementos"
            f" (1 biografía + {len(texts_to_analyze) - (1 if bio else 0)} videos)..."
        )
        content_embeddings = self._get_embeddings(texts_to_analyze)

        flagged_events = []
        max_scores_per_element = []

        for i, post_vec in enumerate(content_embeddings):
            post_scores = [
                self._cosine_similarity(post_vec, pat_vec)
                for pat_vec in self.pattern_embeddings
            ]
            max_sim_idx = int(
                max(range(len(post_scores)), key=lambda k: post_scores[k])
            )
            max_score = post_scores[max_sim_idx]
            max_scores_per_element.append(max_score)

            # Umbral de similitud semántica calibrada
            if max_score >= 0.70:
                meta = text_metadata[i]
                flagged_events.append({
                    "origin": meta["origin"],
                    "url": meta["url"],
                    "matched_pattern": self.pattern_labels[max_sim_idx],
                    "confidence": f"{round(max_score * 100, 2)}%",
                    "excerpt": meta["raw_text"],
                })

        risk_score = round(
            (sum(max_scores_per_element) / len(max_scores_per_element)) * 100, 2
        )

        # Criterio de veredicto:
        # Se declara alto riesgo si hay al menos 2 eventos marcados,
        # O si la biografía directamente es clasificada como patrón de captación.
        bio_flagged = any(e["origin"] == "BIOGRAFÍA" for e in flagged_events)
        is_high_risk = len(flagged_events) >= 2 or bio_flagged

        return {
            "audited_profile": f"@{username}",
            "elements_analyzed": len(texts_to_analyze),
            "flagged_events_count": len(flagged_events),
            "global_risk_index": f"{risk_score} / 100",
            "verdict": (
                "PERFIL DE ALTO RIESGO (Patrón de Captación Detectado)"
                if is_high_risk
                else "PERFIL CONFORME (Bajo Riesgo)"
            ),
            "flagged_cases": flagged_events,
        }