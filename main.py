from core.client import TikTokClient
from core.parser import TikTokParser
from core.exporter import DataExporter

def main() -> None:
    # Perfil público a consultar
    target_username = "tiktok"
    target_url = f"https://www.tiktok.com/@{target_username}"

    # headless=False si deseas ver la ventana del navegador; True para segundo plano
    client = TikTokClient(headless=True)

    try:
        print("[*] Iniciando motor Playwright...")
        client.start()

        # scroll_count=3 para forzar la carga de más filas de videos
        print(f"[*] Obteniendo perfil con scroll dinámico: {target_url}")
        html_rendered = client.fetch_rendered_html(target_url, scroll_count=3)

        print("[*] Procesando árbol DOM con BeautifulSoup...")
        parser = TikTokParser(html_rendered)
        profile_data = parser.extract_user_summary()
        video_list = parser.extract_rendered_videos()

        print("\n--- RESUMEN DEL PERFIL ---")
        for k, v in profile_data.items():
            print(f"  • {k}: {v}")

        print(f"\n[+] Total de videos capturados en la cuadrícula: {len(video_list)}")

        # Exportar datos
        DataExporter.to_json(
            {"profile": profile_data, "videos": video_list},
            f"perfil_{target_username}.json",
        )
        if video_list:
            DataExporter.to_csv(video_list, f"videos_{target_username}.csv")

    except Exception as error:
        print(f"[-] Error en el proceso: {error}")
    finally:
        client.close()
        print("[*] Sesión del navegador finalizada.")

if __name__ == "__main__":
    main()