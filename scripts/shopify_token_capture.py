"""
One-time Shopify OAuth token capture script.
No dependencies — uses only Python 3 standard library.

SETUP (do these BEFORE running):
  1. Go to dev.shopify.com → TS AI Operations → Settings
     - Copy the "Client ID" and "Client secret" values
     - Paste them into this script below (lines 22-23)

  2. Go to dev.shopify.com → TS AI Operations → Versions → Create version
     - In the "Redirect URLs" field, enter: http://localhost:3456/callback
     - Make sure "Use legacy install flow" is checked
     - Click "Release"

  3. Uninstall the app from your store if currently installed:
     admin.shopify.com/store/tibetanspirits/settings/apps

  4. Run this script FIRST (so it's listening before the redirect):
     cd tibetan-spirit-ops
     python3 scripts/shopify_token_capture.py

  5. THEN install the app from your store admin:
     admin.shopify.com/store/tibetanspirits/settings/apps
     → Click on TS AI Operations → Install

  6. Your browser will redirect to localhost:3456/callback
     The script catches the code, exchanges it, and prints your access token.

  7. Copy the shpat_... token into your .env as SHOPIFY_ACCESS_TOKEN
  8. Delete this script — it's single-use.
"""

import http.server
import os
import urllib.parse
import urllib.request
import urllib.error
import json
import hashlib
import hmac

# ──────────────────────────────────────────────────────────────────────────────
# PASTE YOUR CREDENTIALS HERE (from Dev Dashboard → TS AI Operations → Settings)
# ──────────────────────────────────────────────────────────────────────────────
CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID", "PASTE_YOUR_CLIENT_ID_HERE")
CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET", "PASTE_YOUR_CLIENT_SECRET_HERE")
SHOP = "tibetanspirits.myshopify.com"  # Already set — don't change
# ──────────────────────────────────────────────────────────────────────────────

PORT = 3456


def verify_hmac(query_string: str, secret: str) -> bool:
    """Verify Shopify's HMAC signature on the callback URL."""
    params = urllib.parse.parse_qs(query_string, keep_blank_values=True)
    provided_hmac = params.pop("hmac", [None])[0]
    if not provided_hmac:
        return False
    # Rebuild query string without hmac, sorted
    sorted_params = "&".join(
        f"{k}={v[0]}" for k, v in sorted(params.items())
    )
    computed = hmac.new(
        secret.encode("utf-8"),
        sorted_params.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(computed, provided_hmac)


class TokenCaptureHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return

        # Log everything we received for debugging
        print(f"\n📨 Callback received!")
        print(f"   Full URL: localhost:{PORT}{self.path[:100]}...")
        print(f"   Parameters: {list(params.keys())}")

        if "code" not in params:
            print(f"\n⚠️  No 'code' parameter in the redirect.")
            print(f"   Got these params instead: {list(params.keys())}")
            print(f"\n   This usually means:")
            print(f"   - The Redirect URL wasn't set (check Dev Dashboard version config)")
            print(f"   - Or Shopify sent a session redirect, not an auth code grant")

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"""
                <html><body style="font-family: system-ui; padding: 40px; max-width: 600px; margin: auto;">
                <h1 style="color: #e74c3c;">No authorization code received</h1>
                <p>Parameters received: <code>{', '.join(params.keys())}</code></p>
                <h3>Checklist:</h3>
                <ol>
                <li>Dev Dashboard → TS AI Operations → Versions → latest version</li>
                <li>Redirect URLs field = <code>http://localhost:{PORT}/callback</code></li>
                <li>"Use legacy install flow" is checked</li>
                <li>Version is Released (active)</li>
                <li>App was uninstalled then reinstalled from store admin</li>
                </ol>
                <p>Fix the above, then re-run this script and reinstall.</p>
                </body></html>
            """.encode())
            return

        # We have a code!
        code = params["code"][0]
        shop = params.get("shop", [SHOP])[0]

        # Verify HMAC if client secret is set
        if CLIENT_SECRET:
            query_string = parsed.query
            if verify_hmac(query_string, CLIENT_SECRET):
                print(f"   ✅ HMAC signature verified")
            else:
                print(f"   ⚠️  HMAC verification failed (proceeding anyway)")

        print(f"\n✅ Authorization code received: {code[:12]}...")
        print(f"   Shop: {shop}")
        print(f"   Exchanging for access token...\n")

        # Exchange the code for an access token
        token_url = f"https://{shop}/admin/oauth/access_token"
        payload = json.dumps({
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
        }).encode("utf-8")

        req = urllib.request.Request(
            token_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                access_token = result.get("access_token", "NOT FOUND")
                scope = result.get("scope", "")

                print("=" * 60)
                print(f"  ACCESS TOKEN: {access_token}")
                print(f"  SCOPES:       {scope}")
                print("=" * 60)
                print()
                print(f"  Paste this into your .env file:")
                print(f"  SHOPIFY_ACCESS_TOKEN={access_token}")
                print()
                print(f"  Token starts with 'shpat_' = offline (permanent). Good.")
                print(f"  Token starts with 'shpua_' = online (expires). Re-do with offline mode.")
                print()

                # Also save to a temp file for easy copy
                with open("scripts/.shopify_token_temp", "w") as f:
                    f.write(f"SHOPIFY_ACCESS_TOKEN={access_token}\n")
                print(f"  Also saved to: scripts/.shopify_token_temp")

        except urllib.error.HTTPError as e:  # noqa
            error_body = e.read().decode("utf-8")
            print(f"❌ Token exchange failed: HTTP {e.code}")
            print(f"   Response: {error_body}")
            print(f"\n   Common causes:")
            print(f"   - Authorization code expired (they're single-use, valid ~30 seconds)")
            print(f"   - Client ID or Secret is wrong")
            print(f"   - App was already installed (uninstall first, then reinstall)")

        # Send success page to browser
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"""
            <html><body style="font-family: system-ui; text-align: center; padding: 60px;">
            <h1 style="color: #27ae60;">Token Captured!</h1>
            <p>Check your terminal for the access token.</p>
            <p style="color: #666;">You can close this tab.</p>
            </body></html>
        """)

    def log_message(self, format, *args):
        pass  # Suppress default HTTP logging


if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRET:
        print()
        print("=" * 60)
        print("  SETUP REQUIRED")
        print("=" * 60)
        print()
        print("  1. Go to: dev.shopify.com")
        print("  2. Click: TS AI Operations → Settings")
        print("  3. Copy the 'Client ID' and 'Client secret'")
        print("  4. Paste them into this script (lines 40-41)")
        print()
        print("  Then run this script again.")
        print()
        exit(1)

    print()
    print("=" * 60)
    print("  Shopify OAuth Token Capture")
    print("=" * 60)
    print()
    print(f"  Listening on: http://localhost:{PORT}/callback")
    print(f"  Store:        {SHOP}")
    print(f"  Client ID:    {CLIENT_ID[:8]}...")
    print()
    print("  NEXT STEP: Install (or reinstall) TS AI Operations")
    print(f"  from: admin.shopify.com/store/tibetanspirits/settings/apps")
    print()
    print("  Waiting for Shopify redirect...")
    print()

    server = http.server.HTTPServer(("localhost", PORT), TokenCaptureHandler)

    try:
        server.handle_request()  # Handle exactly one request, then exit
    except KeyboardInterrupt:
        print("\nCancelled.")
    finally:
        server.server_close()
        print("Server stopped.")
