import json
from bs4 import BeautifulSoup

class TikTokParser:
    """Procesador DOM configurado para extraer metadatos de perfil y publicaciones."""

    def __init__(self, markup: str) -> None:
        self.soup = BeautifulSoup(markup, "html.parser")

    def extract_user_summary(self) -> dict:
        """Extraemos las métricas generales del perfil objetivo."""
        script_tag = self.soup.find("script", id="__UNIVERSAL_DATA_FOR_REHYDRATION__")
        if script_tag and script_tag.string:
            try:
                data = json.loads(script_tag.string)
                user_detail = (
                    data.get("__DEFAULT_SCOPE__", {})
                    .get("webapp.user-detail", {})
                    .get("userInfo", {})
                )
                if user_detail:
                    user = user_detail.get("user", {})
                    stats = user_detail.get("stats", {})
                    return {
                        "username": user.get("uniqueId"),
                        "nickname": user.get("nickname"),
                        "bio": user.get("signature"),
                        "followers": stats.get("followerCount"),
                        "following": stats.get("followingCount"),
                        "likes": stats.get("heartCount"),
                        "video_count": stats.get("videoCount"),
                    }
            except json.JSONDecodeError:
                pass

        h1_tag = self.soup.find("h1", {"data-e2e": "user-title"}) or self.soup.find("h1")
        return {
            "username": "Desconocido",
            "nickname": h1_tag.get_text(strip=True) if h1_tag else "No detectado",
        }

    def extract_rendered_videos(self, limit: int = 10) -> list[dict]:
        """Extrae publicaciones visibles buscando texto real en enlaces e imágenes."""
        videos = []
        post_items = self.soup.find_all(
            "div", attrs={"data-e2e": "user-post-item"}
        )

        for item in post_items:
            link_tag = item.find("a")
            video_url = link_tag.get("href", "") if link_tag else ""

            # Intentar capturar texto descriptivo real
            description = ""

            # Prioridad 1: Atributo title en el enlace
            if link_tag and link_tag.get("title"):
                description = link_tag.get("title").strip()

            # Prioridad 2: Atributo alt en la imagen de portada
            if not description:
                img_tag = item.find("img")
                if img_tag and img_tag.get("alt"):
                    description = img_tag.get("alt").strip()

            # Prioridad 3: Texto plano dentro de spans o divs descriptivos
            if not description:
                desc_container = item.find(
                    ["div", "span"],
                    class_=lambda c: c and "desc" in c.lower(),
                )
                if desc_container:
                    description = desc_container.get_text(strip=True)

            views_tag = item.find("strong", attrs={"data-e2e": "video-views"})
            views = views_tag.get_text(strip=True) if views_tag else "N/D"

            if video_url:
                videos.append({
                    "url": video_url,
                    "description": description,
                    "views": views,
                })

        return videos[:limit]