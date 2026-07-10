# Compatibility

A community-maintained record of devices people have run the Roborock Local Server against.
This is for confirmed, working (or not-working) results. If you just want to ask a question or
share a report to discuss, use the
[Compatibility Discussions category](https://github.com/DonSidro/local_roborock_server/discussions/categories/compatibility)
instead.

For the certificate-chain compatibility matrix, see [Tested vacuums](docs/tested_vacuums.md).

Legend for **Works?**: ✅ working · ❌ not working · ❓ partial / unconfirmed

| Device | OS / Version | Project version | Works? | Notes |
|---|---|---|:---:|---|
| Roborock S8 MaxV Ultra | Firmware `02.52.32` | v1.0.2 | ✅ | ZeroSSL chain, Docker Compose install |
| Roborock S5 Max | Firmware not reported | v1.0.2 | ❌ | Rejects ZeroSSL; onboards fine with the Actalis chain |

## Adding your device

Got a confirmed result? Open a pull request adding a row to the table above. Keep the columns in
order and use the legend symbols for the **Works?** column. If you are not sure yet, start a thread
in the [Compatibility Discussions category](https://github.com/DonSidro/local_roborock_server/discussions/categories/compatibility)
first and we can promote confirmed results here.
