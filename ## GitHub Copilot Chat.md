## GitHub Copilot Chat

- Extension: 0.53.1 (prod)
- VS Code: 1.125.1 (fcf604774b9f2674b473065736ee75077e256353)
- OS: win32 10.0.26200 x64
- GitHub Account: marysavenkova16-commits

## Network

User Settings:
```json
  "http.systemCertificatesNode": true,
  "github.copilot.advanced.debug.useElectronFetcher": true,
  "github.copilot.advanced.debug.useNodeFetcher": false,
  "github.copilot.advanced.debug.useNodeFetchFetcher": true
```

Connecting to https://api.github.com:
- DNS ipv4 Lookup: 140.82.121.5 (6 ms)
- DNS ipv6 Lookup: Error (6 ms): getaddrinfo ENOTFOUND api.github.com
- Proxy URL: None (4 ms)
- Electron fetch (configured): HTTP 200 (179 ms)
- Node.js https: HTTP 200 (332 ms)
- Node.js fetch: HTTP 200 (225 ms)

Connecting to https://api.githubcopilot.com/_ping:
- DNS ipv4 Lookup: 140.82.113.21 (54 ms)
- DNS ipv6 Lookup: Error (2 ms): getaddrinfo ENOTFOUND api.githubcopilot.com
- Proxy URL: None (2 ms)
- Electron fetch (configured): HTTP 200 (158 ms)
- Node.js https: HTTP 200 (481 ms)
- Node.js fetch: HTTP 200 (473 ms)

Connecting to https://copilot-proxy.githubusercontent.com/_ping:
- DNS ipv4 Lookup: 4.225.11.192 (25 ms)
- DNS ipv6 Lookup: Error (22 ms): getaddrinfo ENOTFOUND copilot-proxy.githubusercontent.com
- Proxy URL: None (4 ms)
- Electron fetch (configured): HTTP 200 (283 ms)
- Node.js https: HTTP 200 (271 ms)
- Node.js fetch: HTTP 200 (286 ms)

Connecting to https://mobile.events.data.microsoft.com: HTTP 404 (60 ms)
Connecting to https://dc.services.visualstudio.com: HTTP 404 (380 ms)
Connecting to https://copilot-telemetry.githubusercontent.com/_ping: HTTP 200 (481 ms)
Connecting to https://copilot-telemetry.githubusercontent.com/_ping: HTTP 200 (477 ms)
Connecting to https://default.exp-tas.com: HTTP 400 (311 ms)

Number of system certificates: 95

## Documentation

In corporate networks: [Troubleshooting firewall settings for GitHub Copilot](https://docs.github.com/en/copilot/troubleshooting-github-copilot/troubleshooting-firewall-settings-for-github-copilot).