import re
import asyncio
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

mcp = FastMCP("weather-Israel")

FORECAST_URL = "https://www.weather2day.co.il/forecast"

_playwright = None
_browser = None
_page = None

async def close_browser():
    global _playwright, _browser, _page
    if _browser:
        await _browser.close()
    if _playwright:
        await _playwright.stop()
    _playwright = _browser = _page = None

async def ensure_browser():
    global _playwright, _browser, _page
    if _playwright is None:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=False)
        _page = await _browser.new_page()

@mcp.tool()
async def open_weather_forecast_israel() -> str:
    """Step 1: Opens browser and clears cookie overlays."""
    await close_browser() 
    await ensure_browser()

    print("Opening browser...")
    await _page.goto(FORECAST_URL, wait_until="networkidle")

    try:
        cookie_btn = _page.locator("button:has-text('מקובל'), .cc-acceptall")
        if await cookie_btn.is_visible():
            await cookie_btn.click()
            await asyncio.sleep(0.5)
    except:
        pass

    return "Browser opened fresh and ready."

@mcp.tool()
async def enter_weather_forecast_city_israel(city: str) -> str:
    """Step 2: Type city name into search box."""
    if _page is None:
        await open_weather_forecast_israel()

    await _page.wait_for_selector("#city_search_forecast")
    search_input = _page.locator("#city_search_forecast")
    
    await search_input.click(force=True)
    await search_input.fill("")
    await search_input.type(city, delay=120)
    await asyncio.sleep(2)

    return f"Typed city: {city}"

@mcp.tool()
async def select_weather_forecast_city_israel() -> str:
    """Step 3: Select first autocomplete city."""
    if _page is None:
        return "Error: Browser not initialized. Please start from Step 1."

    try:
        await _page.wait_for_selector(
            "#city_search_forecastautocomplete-list div",
            timeout=5000
        )
        items = _page.locator("#city_search_forecastautocomplete-list div")
        count = await items.count()

        if count == 0:
            return "No suggestions found."

        first_item = items.first
        text = await first_item.inner_text()
        await first_item.click(force=True)
        await asyncio.sleep(2)

        return f"Selected city: {text}"
    except Exception as e:
        return f"Selection failed: {str(e)}"

@mcp.tool()
async def get_weather_forecast_israel(limit: int = 2000) -> str:
    """Step 4: Scrapes the data and CLOSES browser."""
    global _page
    if not _page: 
        return "Error: No active page to scrape."
    
    try:
        await _page.wait_for_load_state("networkidle")
        
        content = await _page.evaluate("""() => {
            const container = document.querySelector('.forecast-container') || document.body;
            return container.innerText;
        }""")
        
        cleaned = " ".join(content.split())
        result = f"URL: {_page.url} | DATA: {cleaned[:limit]}"
        
        await close_browser()
        return result
        
    except Exception as e:
        await close_browser()
        return f"Scraping failed: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")