# 3. Tunnel setup

Covers exposing Immich at a subdomain on your existing domain without opening any inbound port on your home network.

> **Why not port-forward instead?** Forwarding a port exposes your home router/IP directly to internet scanners and attack traffic, ties your home IP to a public-facing service, and needs dynamic DNS on top since residential IPs usually aren't static. A tunnel avoids all of that: no inbound port is ever opened, since the tunnel connector makes an outbound-only connection to Cloudflare, which relays traffic back to it.

## 1. Create the tunnel

In the [Cloudflare Zero Trust dashboard](https://one.dash.cloudflare.com/): **Networks → Tunnels → Create a tunnel** → choose **Cloudflared** → name it (e.g. `immichesque`).

## 2. Get the connector token

The tunnel creation flow shows an install command containing a long token after `--token`. Copy just the token value -- this project runs the connector as a Docker container instead of installing `cloudflared` directly on the host, so you won't run that install command as shown.

## 3. Add the public hostname

Still in the tunnel's settings, **Public Hostname** tab → **Add a public hostname**:

- **Subdomain**: whatever you want (e.g. `photos`)
- **Domain**: pick your existing domain from the dropdown (Cloudflare needs to manage its DNS for this dropdown to work -- see the two options below if it doesn't)
- **Service**: `HTTP` → `immich-server:2283`

> **Your domain is currently served through DigitalOcean, not Cloudflare DNS.** Two options:
>
> **Option A (recommended): move DNS to Cloudflare.** Change your domain's nameservers at your registrar to Cloudflare's, then the Public Hostname UI above manages the DNS record automatically. Your DigitalOcean droplet keeps serving the rest of the site unaffected -- only DNS management moves, not hosting.
>
> **Option B: keep DNS on DigitalOcean, add the CNAME manually.** Cloudflare's tunnel dashboard shows a target hostname (`<tunnel-id>.cfargotunnel.com`) -- add a CNAME record for your chosen subdomain pointing at that value in DigitalOcean's DNS panel instead of using the automatic Public Hostname UI.

## 4. Add the token to this project

```bash
cd immich
cp automation.env.example automation.env
```

Set `CLOUDFLARE_TUNNEL_TOKEN=<the token from step 2>` in `automation.env`.

## 5. Bring the tunnel up

```bash
docker compose up -d cloudflared
```

Check the tunnel shows **Healthy** in the Cloudflare dashboard, then visit `https://<your-subdomain>.<your-domain>` and confirm you land on Immich's login page.

## Next

Continue to [04-automation-setup.md](04-automation-setup.md) to wire up the review/backup automation.
