## GitHub Copilot Chat

- Extension: 0.52.0 (prod)
- VS Code: 1.124.2 (6928394f91b684055b873eecb8bc281365131f1c)
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
- DNS ipv4 Lookup: 140.82.121.5 (4 ms)
- DNS ipv6 Lookup: Error (24 ms): getaddrinfo ENOTFOUND api.github.com
- Proxy URL: None (4 ms)
- Electron fetch (configured): HTTP 200 (70 ms)
- Node.js https: HTTP 200 (365 ms)
- Node.js fetch: HTTP 200 (73 ms)

Connecting to https://api.githubcopilot.com/_ping:
- DNS ipv4 Lookup: 140.82.114.21 (2 ms)
- DNS ipv6 Lookup: Error (2 ms): getaddrinfo ENOTFOUND api.githubcopilot.com
- Proxy URL: None (4 ms)
- Electron fetch (configured): HTTP 200 (161 ms)
- Node.js https: HTTP 200 (481 ms)
- Node.js fetch: HTTP 200 (503 ms)

Connecting to https://copilot-proxy.githubusercontent.com/_ping:
- DNS ipv4 Lookup: 4.225.11.192 (24 ms)
- DNS ipv6 Lookup: Error (25 ms): getaddrinfo ENOTFOUND copilot-proxy.githubusercontent.com
- Proxy URL: None (3 ms)
- Electron fetch (configured): HTTP 200 (400 ms)
- Node.js https: HTTP 200 (294 ms)
- Node.js fetch: HTTP 200 (300 ms)

Connecting to https://mobile.events.data.microsoft.com: HTTP 404 (170 ms)
Connecting to https://dc.services.visualstudio.com: HTTP 404 (413 ms)
Connecting to https://copilot-telemetry.githubusercontent.com/_ping: HTTP 200 (486 ms)
Connecting to https://copilot-telemetry.githubusercontent.com/_ping: HTTP 200 (530 ms)
Connecting to https://default.exp-tas.com: HTTP 400 (313 ms)

Number of system certificates: 93

## Documentation

In corporate networks: [Troubleshooting firewall settings for GitHub Copilot](https://docs.github.com/en/copilot/troubleshooting-github-copilot/troubleshooting-firewall-settings-for-github-copilot).