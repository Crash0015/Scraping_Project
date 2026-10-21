from core.client import TikTokClient
from core.parser import TikTokParser
from core.exporter import DataExporter

def main() -> None:
    target_username = "stailokmusic"
    target_url = f"https://www.tiktok.com/@{target_username}"

    client = TikTokClient(headless=True)

    try:
        print("[*] Iniciando motor Playwright...")
        client.start()

        print(f"[*] Navegando a: {target_url}")
        # Con 1 scroll nos basta para asegurar más de 10 publicaciones
        html_rendered = client.fetch_rendered_html(target_url, scroll_count=1)

        print("[*] Procesando DOM con BeautifulSoup...")
        parser = TikTokParser(html_rendered)
        profile_data = parser.extract_user_summary()
        video_list = parser.extract_rendered_videos(limit=10)

        print("\n--- RESUMEN DEL PERFIL ---")
        for k, v in profile_data.items():
            print(f"  • {k}: {v}")

        print(f"\n[+] Videos capturados (limitado a los 10 últimos): {len(video_list)}")

        # Exportación en formato JSON
        DataExporter.to_json(
            {"profile": profile_data, "videos": video_list},
            f"perfil_{target_username}.json",
        )

    except Exception as error:
        print(f"[-] Error en el proceso: {error}")
    finally:
        client.close()
        print("[*] Sesión del navegador finalizada.")

if __name__ == "__main__":
    main()