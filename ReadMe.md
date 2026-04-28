
# 🌤️ Multi-Source Weather MCP Agent
 
A conversational AI agent that fetches real-time weather data from two independent sources — the **USA National Weather Service** and an **Israeli weather site** — using the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) and [Groq](https://groq.com/) as the LLM backend.
 
---
 
## 📁 Project Structure
 
```
.
├── chat_host.py        # Main agent loop — orchestrates tools and Groq LLM
├── client.py           # Generic MCP client (connects to any MCP server via stdio)
├── weather_USA.py      # MCP server: US weather via NWS API
├── weather_israel.py   # MCP server: Israeli weather via browser scraping (Playwright)
├── .env                # Environment variables (GROQ_API_KEY)
└── README.md
```
 
---
 
## ⚙️ How It Works
 
```
User Query
    │
    ▼
ChatHost (chat_host.py)
    │   uses Groq LLM (llama-3.3-70b-versatile)
    │   discovers tools from all MCP servers
    │
    ├──► MCPClient → weather_USA.py      (NWS API — HTTP)
    └──► MCPClient → weather_israel.py   (Playwright browser scraping)
```
 
1. **`ChatHost`** starts two `MCPClient` instances, one per weather server.
2. Each `MCPClient` launches its server script as a subprocess and communicates via **stdio** (MCP standard transport).
3. Available tools are collected from all servers and exposed to the Groq LLM.
4. The LLM decides which tool(s) to call based on the user's query.
5. Tool results are fed back to the LLM, which produces the final answer.
---
 
## 🚀 Getting Started
 
### 1. Prerequisites
 
- Python 3.11+
- A [Groq API key](https://console.groq.com/)
### 2. Install dependencies
 
```bash
pip install groq mcp httpx python-dotenv playwright
playwright install chromium
```
 
### 3. Configure environment
 
Create a `.env` file in the project root:
 
```env
GROQ_API_KEY=your_groq_api_key_here
```
 
### 4. Run the agent
 
```bash
python chat_host.py
```
 
You'll see the connected tools printed, then an interactive prompt:
 
```
Connected to server with tools: ['get_alerts_in_USA', 'get_forecast_in_USA']
Connected to server with tools: ['open_weather_forecast_israel', 'enter_weather_forecast_city_israel', 'select_weather_forecast_city_israel', 'get_weather_forecast_israel']
 
MCP Client Started!
Type your queries or 'quit' to exit.
 
Query:
```
 
---
 
## 🛠️ Available Tools
 
### 🇺🇸 USA Weather (`weather_USA.py`)
Uses the free [National Weather Service API](https://api.weather.gov) — no API key needed.
 
| Tool | Description |
|------|-------------|
| `get_alerts_in_USA` | Active weather alerts for a US state (e.g. `CA`, `TX`) |
| `get_forecast_in_USA` | 5-period forecast for a given latitude/longitude |
 
### 🇮🇱 Israel Weather (`weather_israel.py`)
Uses **Playwright** to scrape [weather2day.co.il](https://www.weather2day.co.il/forecast). Must be run in sequence:
 
| Step | Tool | Description |
|------|------|-------------|
| 1 | `open_weather_forecast_israel` | Opens browser and loads the forecast page |
| 2 | `enter_weather_forecast_city_israel` | Types city name into the search field |
| 3 | `select_weather_forecast_city_israel` | Selects city from autocomplete dropdown |
| 4 | `get_weather_forecast_israel` | Scrapes and returns the forecast text |
 
> **Note:** The Israel server opens a visible Chromium browser window (`headless=False`). This is intentional for debugging; set `headless=True` in `weather_israel.py` to suppress it.
 
---
 
## 💬 Example Queries
 
### US weather
```
Query: Are there any active weather alerts in Florida?
 
Query: What is the weather forecast for New York City?
(Coordinates: 40.7128, -74.0060)
 
Query: What's the forecast for Los Angeles this week?
(Coordinates: 34.0522, -118.2437)
```
 
### Israeli weather
```
Query: What is the weather forecast in Tel Aviv?
 
Query: Is it going to rain in Haifa tomorrow?
```
 
### Combined / General
```
Query: Compare the weather in Miami and Tel Aviv today.
 
Query: Should I pack an umbrella for my trip to Be'er Sheva?
```
 
---
 
## 🔧 Extending the Agent
 
To add a new data source, create a new MCP server file and register it in `chat_host.py`:
 
```python
self.mcp_clients = [
    MCPClient("./weather_USA.py"),
    MCPClient("./weather_israel.py"),
    MCPClient("./your_new_server.py"),  # ← add here
]
```
 
Tool names are automatically namespaced as `<server_name>__<tool_name>` to avoid conflicts.
 
---
 
## 📝 Notes
 
- The Israeli weather scraper depends on the structure of `weather2day.co.il` and may break if the site changes.
- SSL verification is disabled in the USA weather client (`verify=False`) for compatibility with certain network environments (e.g. filtered networks). Re-enable it in production by removing the custom `transport`.
- The agent uses Groq's `llama-3.3-70b-versatile` model. You can swap this for any model supported by Groq in `chat_host.py`.