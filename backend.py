# backend.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from datetime import datetime, timezone
import random

app = FastAPI()

# Allow the React frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/market/snapshot")
def get_market_snapshot():
    """
    Returns the exact JSON payload expected by the React UI's fetchLiveMarketData()
    """
    # The default universe of stocks in your React UI
    stock_symbols = [
        "VOO", "ASTS", "SPY", "QQQ", "NVDA", "TSLA", 
        "IREN", "VRT", "APLD", "RKLB", "HUT"
    ]
    
    # NBIS is not a standard Yahoo Finance ticker, so we handle it separately
    stocks_data = []
    
    # Fetch live data in bulk using yfinance
    try:
        tickers = yf.Tickers(" ".join(stock_symbols))
        
        for sym in stock_symbols:
            try:
                # fast_info is the quickest way to get the current price in yfinance
                current_price = tickers.tickers[sym].fast_info['lastPrice']
                stocks_data.append({
                    "symbol": sym,
                    "current": round(current_price, 2),
                    "dataStatus": "live",
                    "source": "yfinance API"
                })
            except Exception:
                # Fallback if a specific ticker fails to load
                stocks_data.append({
                    "symbol": sym,
                    "current": 0.0,
                    "dataStatus": "unavailable",
                    "source": "yfinance error"
                })
                
    except Exception as e:
        return {"status": "unavailable", "source": f"Backend Error: {str(e)}"}

    # Add NBIS mock data since it's a core holding in the UI but lacks a public yf ticker
    stocks_data.append({
        "symbol": "NBIS",
        "current": round(76.20 + random.uniform(-1.5, 1.5), 2),
        "dataStatus": "simulated",
        "source": "Mock Backend Data"
    })

    # Options data is mocked here. Free live options APIs are virtually non-existent.
    # Replace this block with a Polygon.io or Tradier API call in production.
    options_data = [
        {
            "symbol": "DRAM",
            "strike": 70,
            "expiry": "2026-06-26",
            "currentPremium": round(2.65 + random.uniform(-0.2, 0.4), 2),
            "dataStatus": "simulated",
            "source": "Mock Options Feed"
        },
        {
            "symbol": "IREN",
            "strike": 90,
            "expiry": "2026-07-17",
            "currentPremium": round(2.10 + random.uniform(-0.15, 0.3), 2),
            "dataStatus": "simulated",
            "source": "Mock Options Feed"
        }
    ]

    return {
        "status": "live",
        # ISO format timestamp required by the React frontend (secondsSince function)
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "Python FastAPI + yfinance",
        "stocks": stocks_data,
        "options": options_data
    }

if __name__ == "__main__":
    import uvicorn
    # Runs the server on http://localhost:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
