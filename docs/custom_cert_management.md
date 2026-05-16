# Custom certificate management

Use this if you do not want Cloudflare DNS-01 automation and instead want to provide the TLS certificate files yourself during [Installation](installation.md).

Check [Tested Vacuums](tested_vacuums.md) first. This is the right path when your vacuum works better with a certificate chain other than the built-in `zerossl` or `actalis` options, or when you already have certs you want to reuse. Older vacuums are less likely to support certs from places like LetsEncrypt. Newer vacuums may work, but this is not tested. Please report back any findings you have via a PR to the tested_vacuums page.

## Required Config

Set the TLS section in `config.toml` to the provided-certificate mode:

```toml
[tls]
mode = "provided"
cert_file = "/data/certs/fullchain.pem"
key_file = "/data/certs/privkey.pem"
```

If you use the setup wizard and answer no to Cloudflare, it will write these values for you. You then need to place your certificate files at `data/certs/fullchain.pem` and `data/certs/privkey.pem` before starting the stack.

## Related Docs

- [Installation](installation.md)
- [Cloudflare setup](cloudflare_setup.md)
- [Onboarding](onboarding.md)
