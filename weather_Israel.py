import re
import asyncio
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

mcp = FastMCP("weather-Israel")

FORECAST_URL = "https://www.weather2day.co.il/forecast"

_playwright = None
_browser = None
_page = None

async def ensure_browser():
    global _playwright, _browser, _page
    if _playwright is None:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=False)
        _page = await _browser.new_page()

@mcp.tool()
async def open_weather_forecast_israel(action: str = "open") -> str:
    """Step 1: Opens browser and clears cookie overlays."""
    await ensure_browser()
    await _page.goto(FORECAST_URL, wait_until="networkidle")
    
    try:
        cookie_btn = _page.locator("button:has-text('מקובל'), .cc-acceptall")
        if await cookie_btn.is_visible():
            await cookie_btn.click()
            await asyncio.sleep(0.5)
    except:
        pass
    return "Browser ready and page is clear."

@mcp.tool()
async def enter_weather_forecast_city_israel(city: str) -> str:
    """Step 2: Finds the search input and types city name."""
    if not _page: return "Error: Open browser first."
    
    search_input = _page.locator("input[name='search'], #search_field").first
    await search_input.wait_for(state="visible")
    await search_input.click()
    await search_input.fill("")
    
    await search_input.type(city, delay=150)
    await asyncio.sleep(1.5) 
    return f"Typed city: {city}"

@mcp.tool()
async def select_weather_forecast_city_israel(mode: str = "first") -> str:
    """Step 3: Selects the city from the autocomplete list."""
    if not _page: return "Error: Open browser first."
    
    try:
        item = _page.locator(".ui-menu-item, .autocomplete-suggestion").first
        await item.wait_for(state="visible", timeout=5000)
        await item.click()
        return "City selected from dropdown."
    except:
        await _page.keyboard.press("Enter")
        return "Dropdown failed, pressed Enter as fallback."

@mcp.tool()
async def get_weather_forecast_israel(limit: int = 2000) -> str:
    """Step 4: Scrapes the forecast data."""
    if not _page: return "Error: Open browser first."
    
    await _page.wait_for_load_state("networkidle")
    
    content = await _page.evaluate("""() => {
        const container = document.querySelector('.forecast-container') || document.body;
        return container.innerText;
    }""")
    
    cleaned = " ".join(content.split())
    return f"URL: {_page.url} | DATA: {cleaned[:limit]}"

if __name__ == "__main__":
    mcp.run(transport="stdio")