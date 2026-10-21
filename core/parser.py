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
        """Extraemos las publicaciones visibles en la cuadricla limitadas a 10 elementos."""
        videos = []
        post_items = self.soup.find_all("div", attrs={"data-e2e": "user-post-item"})

        for item in post_items:
            link_tag = item.find("a")
            video_url = link_tag.get("href", "") if link_tag else ""

            desc_tag = item.find("img") or item.find("a")
            description = desc_tag.get("alt", "") if desc_tag and desc_tag.has_attr("alt") else ""

            views_tag = item.find("strong", attrs={"data-e2e": "video-views"})
            views = views_tag.get_text(strip=True) if views_tag else "N/D"

            if video_url:
                videos.append({
                    "url": video_url,
                    "description": description.strip(),
                    "views": views,
                })

        # Retornamos unicamente los primeros N elementos especificados, en este caso 10.
        return videos[:limit]