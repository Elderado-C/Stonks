# backend.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from datetime import datetime, time
import pytz

app = FastAPI()

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_market_status():
    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)
    current_time = now.time()
    
    # 3-Hour window logic
    open_time = time(9, 30)
    window_end = time(12, 30)
    
    if time(4, 0) <= current_time < time(9, 30):
        session = "Pre-Market"
    elif time(9, 30) <= current_time < time(16, 0):
        session = "Regular Trading"
    elif time(16, 0) <= current_time < time(20, 0):
        session = "After-Hours"
    else:
        session = "Closed"

    time_remaining = "0 hrs"
    if session == "Regular Trading" and current_time < window_end:
        tdelta = datetime.combine(now.date(), window_end) - datetime.combine(now.date(), current_time)
        time_remaining = f"{tdelta.seconds // 3600}h {(tdelta.seconds // 60) % 60}m"

    return {"session": session, "time_in_3h_window": time_remaining}

@app.get("/api/dashboard")
def get_dashboard_data():
    market_status = get_market_status()
    # Plug in real API keys (Polygon, Alpaca) here for production
    try:
        spy = yf.Ticker("SPY").history(period="1d")
        vix = yf.Ticker("^VIX").history(period="1d")
        
        return {
            "market_session": market_status["session"],
            "window_remaining": market_status["time_in_3h_window"],
            "spy_price": round(spy['Close'].iloc[-1], 2) if not spy.empty else "N/A",
            "vix_price": round(vix['Close'].iloc[-1], 2) if not vix.empty else "N/A",
            "regime": "Mixed/Choppy", # Placeholder for complex logic
            "data_status": "Live"
        }
    except Exception as e:
        return {
            "data_status": "Stale/Delayed",
            "message": "Live confirmation unavailable. Please upload Webull screenshots (Daily, 1H, 5m, RSI, MACD, VWAP, Options Chain)."
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
