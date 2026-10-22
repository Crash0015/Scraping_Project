import json
from analytics.scam_detector import FinancialScamAuditor
from core.client import TikTokClient
from core.exporter import DataExporter
from core.parser import TikTokParser


def main() -> None:
    target_username = "stailokmusic"
    target_url = f"https://www.tiktok.com/@{target_username}"
    output_filename = f"perfil_{target_username}.json"

    client = TikTokClient(headless=True)

    try:
        print("[*] Iniciando motor Playwright...")
        client.start()

        print(f"[*] Navegando a: {target_url}")
        html_rendered = client.fetch_rendered_html(target_url, scroll_count=1)

        print("[*] Procesando DOM con BeautifulSoup...")
        parser = TikTokParser(html_rendered)
        profile_data = parser.extract_user_summary()
        video_list = parser.extract_rendered_videos(limit=10)

        print("\n--- RESUMEN DEL PERFIL ---")
        for k, v in profile_data.items():
            print(f"  • {k}: {v}")

        print(f"\n[+] Videos capturados (limitado a los 10 últimos): {len(video_list)}")

        # 1. Exportación a JSON con el método de tu clase
        DataExporter.to_json(
            {"profile": profile_data, "videos": video_list},
            output_filename,
        )

        # 2. Pipeline de Auditoría Semántica Vectorial
        print("\n" + "=" * 60)
        print(" AUDITORÍA SEMÁNTICA VECTORIAL (NLP DENSE EMBEDDINGS)")
        print("=" * 60)
        auditor = FinancialScamAuditor()
        audit_result = auditor.audit_profile_risk(output_filename)

        print("\n[+] Reporte de Auditoría:")
        print(json.dumps(audit_result, indent=2, ensure_ascii=False))

    except Exception as error:
        print(f"[-] Error en el proceso: {error}")
    finally:
        client.close()
        print("[*] Sesión del navegador finalizada.")


if __name__ == "__main__":
    main()