import json
import math
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="eShopCo Regional Latency Analytics")

# Allow cross-origin dashboard requests, including POST and preflight OPTIONS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# Telemetry bundle supplied with the assignment (36 records).
TELEMETRY = json.loads(r'''[{"region":"apac","service":"recommendations","latency_ms":133.01,"uptime_pct":98.85,"timestamp":20250301},{"region":"apac","service":"catalog","latency_ms":216.9,"uptime_pct":97.634,"timestamp":20250302},{"region":"apac","service":"recommendations","latency_ms":109.82,"uptime_pct":97.137,"timestamp":20250303},{"region":"apac","service":"payments","latency_ms":179.41,"uptime_pct":97.139,"timestamp":20250304},{"region":"apac","service":"support","latency_ms":220.3,"uptime_pct":97.323,"timestamp":20250305},{"region":"apac","service":"support","latency_ms":218.16,"uptime_pct":98.358,"timestamp":20250306},{"region":"apac","service":"checkout","latency_ms":151.22,"uptime_pct":97.697,"timestamp":20250307},{"region":"apac","service":"support","latency_ms":115.52,"uptime_pct":99.178,"timestamp":20250308},{"region":"apac","service":"analytics","latency_ms":133.7,"uptime_pct":98.591,"timestamp":20250309},{"region":"apac","service":"catalog","latency_ms":150.82,"uptime_pct":97.111,"timestamp":20250310},{"region":"apac","service":"analytics","latency_ms":208.95,"uptime_pct":97.209,"timestamp":20250311},{"region":"apac","service":"recommendations","latency_ms":204.41,"uptime_pct":97.694,"timestamp":20250312},{"region":"emea","service":"analytics","latency_ms":124.62,"uptime_pct":97.437,"timestamp":20250301},{"region":"emea","service":"catalog","latency_ms":151.41,"uptime_pct":99.481,"timestamp":20250302},{"region":"emea","service":"catalog","latency_ms":217.66,"uptime_pct":97.935,"timestamp":20250303},{"region":"emea","service":"support","latency_ms":184.53,"uptime_pct":97.252,"timestamp":20250304},{"region":"emea","service":"checkout","latency_ms":212.62,"uptime_pct":99.03,"timestamp":20250305},{"region":"emea","service":"recommendations","latency_ms":168.14,"uptime_pct":99.152,"timestamp":20250306},{"region":"emea","service":"analytics","latency_ms":107.84,"uptime_pct":98.925,"timestamp":20250307},{"region":"emea","service":"analytics","latency_ms":122.96,"uptime_pct":99.384,"timestamp":20250308},{"region":"emea","service":"checkout","latency_ms":144.8,"uptime_pct":97.752,"timestamp":20250309},{"region":"emea","service":"payments","latency_ms":192.89,"uptime_pct":97.795,"timestamp":20250310},{"region":"emea","service":"support","latency_ms":112.27,"uptime_pct":97.555,"timestamp":20250311},{"region":"emea","service":"catalog","latency_ms":123.61,"uptime_pct":97.215,"timestamp":20250312},{"region":"amer","service":"checkout","latency_ms":133.82,"uptime_pct":98.958,"timestamp":20250301},{"region":"amer","service":"checkout","latency_ms":171.44,"uptime_pct":99.256,"timestamp":20250302},{"region":"amer","service":"analytics","latency_ms":228.93,"uptime_pct":98.587,"timestamp":20250303},{"region":"amer","service":"analytics","latency_ms":216.97,"uptime_pct":99.498,"timestamp":20250304},{"region":"amer","service":"recommendations","latency_ms":138.38,"uptime_pct":97.552,"timestamp":20250305},{"region":"amer","service":"analytics","latency_ms":200.57,"uptime_pct":97.202,"timestamp":20250306},{"region":"amer","service":"recommendations","latency_ms":176.69,"uptime_pct":97.656,"timestamp":20250307},{"region":"amer","service":"catalog","latency_ms":184.27,"uptime_pct":98.748,"timestamp":20250308},{"region":"amer","service":"catalog","latency_ms":230.43,"uptime_pct":98.124,"timestamp":20250309},{"region":"amer","service":"analytics","latency_ms":225.25,"uptime_pct":98.083,"timestamp":20250310},{"region":"amer","service":"recommendations","latency_ms":152.76,"uptime_pct":98.628,"timestamp":20250311},{"region":"amer","service":"catalog","latency_ms":156.15,"uptime_pct":97.976,"timestamp":20250312}]''')

class AnalyticsRequest(BaseModel):
    regions: list[str] = Field(..., min_length=1)
    threshold_ms: float


def percentile_linear(values: list[float], percentile: float) -> float:
    """Calculate a percentile using linear interpolation (NumPy default method)."""
    ordered = sorted(values)
    if not ordered:
        raise ValueError("Cannot calculate percentile for empty data")
    position = (len(ordered) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


@app.post("/")
def regional_analytics(request: AnalyticsRequest):
    results = []
    for region in request.regions:
        rows = [row for row in TELEMETRY if row.get("region") == region]
        if not rows:
            raise HTTPException(status_code=404, detail=f"No telemetry records for region: {region}")

        latencies = [float(row["latency_ms"]) for row in rows]
        uptimes = [float(row["uptime_pct"]) for row in rows]
        results.append({
            "region": region,
            "avg_latency": sum(latencies) / len(latencies),
            "p95_latency": percentile_linear(latencies, 0.95),
            "avg_uptime": sum(uptimes) / len(uptimes),
            "breaches": sum(value > request.threshold_ms for value in latencies),
        })

    return {"results": results}
