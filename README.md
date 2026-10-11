# eShopCo latency analytics endpoint

Deploy this project to Vercel. The POST endpoint is the root path `/` of your assigned deployment URL.

Request example:
```json
{"regions":["emea","apac"],"threshold_ms":176}
```

Response shape:
```json
{"results":[{"region":"emea","avg_latency":155.27916666666668,"p95_latency":214.888,"avg_uptime":98.24275,"breaches":4},{"region":"apac","avg_latency":170.185,"p95_latency":219.123,"avg_uptime":97.82675,"breaches":6}]}
```

`p95_latency` uses linear interpolation (the default percentile method in NumPy). `breaches` counts records where `latency_ms > threshold_ms`. CORS permits any origin, method, and request header; OPTIONS preflight is handled automatically. CORS headers are applied to both successful and error responses.

Deploy: import this repository into Vercel or run `npx vercel --prod` from the project directory. Your final POST endpoint URL will be the deployment's public URL (for example, `https://YOUR-PROJECT.vercel.app/`).
