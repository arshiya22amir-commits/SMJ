SMJ NETWORK — PREMIUM WEBSITE
================================

Run locally:
1) Install Python 3.10+
2) Open a terminal in this folder
3) Run: pip install -r requirements.txt
4) Set a server address if available:
   Windows PowerShell: $env:SERVER_ADDRESS="play.example.com"
   macOS/Linux: export SERVER_ADDRESS="play.example.com"
5) Set a strong secret:
   Windows PowerShell: $env:SECRET_KEY="a-long-random-secret"
   macOS/Linux: export SECRET_KEY="a-long-random-secret"
6) Run: python app.py
7) Open http://127.0.0.1:5000

Design:
- Full premium dark gaming redesign, neon lime + violet
- Responsive navigation, cinematic CSS Minecraft-inspired hero
- BedWars / Practice PvP / Survival cards
- Server status API and copy-IP interaction
- News, community manifesto, rules, account/shop/support pages
- Salvador developer credit

Important:
- Replace SERVER_ADDRESS with your real server IP/domain.
- Set ADMIN_EMAIL before registering the administrator account.
- The rank shop is a visual catalogue only; no payment is processed.
- Instagram / Discord URLs are intentionally not invented.
- For public deployment use a production WSGI server, HTTPS, a strong
  SECRET_KEY, debug=False, and add CSRF protection / rate limiting.
- Public server status depends on the third-party mcsrvstat.us API.
