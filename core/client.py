from playwright.sync_api import sync_playwright, Browser, Page

class TikTokClient:
    """Cliente modular para renderizar el JavaScript de TikTok."""

    def __init__(self, headless: bool = True) -> None:
        self.headless = headless
        self._playwright = None
        self.browser: Browser | None = None

    def start(self) -> None:
        """Inicia el proceso de Chromium."""
        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )

    def fetch_rendered_html(self, url: str, scroll_count: int = 1) -> str:
        """Navega a la URL, espera la carga del DOM y retorna el HTML renderizado."""
        if not self.browser:
            raise RuntimeError("Cliente no inicializado. Llama a .start() primero.")

        context = self.browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="es-EC",
        )
        page: Page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(4000)

            for _ in range(scroll_count):
                page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)

            return page.content()
        finally:
            context.close()

    def close(self) -> None:
        """Cierra el navegador y libera recursos."""
        if self.browser:
            self.browser.close()
        if self._playwright:
            self._playwright.stop()