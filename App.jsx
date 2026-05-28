async function fetchLiveMarketData() {
  try {
    // Point this to your local Python backend
    const res = await fetch("http://localhost:8000/api/market/snapshot");
    
    if (!res.ok) {
      throw new Error(`Market data request failed with status: ${res.status}`);
    }
    
    return await res.json();
  } catch (error) {
    console.error("Backend connection error:", error);
    return {
      status: DATA_STATES.UNAVAILABLE,
      timestamp: new Date().toISOString(),
      source: "Connection Failed",
      stocks: [],
      options: []
    };
  }
}
