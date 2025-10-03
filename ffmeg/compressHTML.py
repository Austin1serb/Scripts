import re

def minify_html(html):
    """Minifies HTML by removing extra spaces, newlines, comments, and ensuring Base64 integrity."""
    # Remove comments
    html = re.sub(r"<!--(.*?)-->", "", html, flags=re.DOTALL)

    # Remove unnecessary whitespace between tags
    html = re.sub(r">\s+<", "><", html)

    # Remove multiple spaces (excluding spaces inside attributes)
    html = re.sub(r"\s{2,}", " ", html)

    # Ensure Base64 strings are continuous (removes newlines and spaces in Base64 data URLs)
    html = re.sub(r"(data:image\/[a-zA-Z]+;base64,)[\s\n]+", r"\1", html)

    # Trim whitespace from the beginning and end
    html = html.strip()

    return html
html_email="""
   <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>Recruiter Page Visit</title>
            <style>
              body {
                font-family: Helvetica, Arial, sans-serif;
                color: #333;
                background: #f4f4f4;
                padding: 20px;
              }
              .container {
                background: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                max-width: 600px;
                margin: auto;
              }
              .highlight {
                font-weight: bold;
                color: #0073e6;
              }
              .footer {
                text-align: center;
                font-size: 12px;
                color: #888;
                margin-top: 20px;
              }
              .logo {
                width: 120px;
                height: auto;
                margin: 10px auto;
                display: block;
              }
              .link {
                color: #0073e6;
                text-decoration: none;
              }
            </style>
          </head>
          <body>
            <div class="container">
              <h2>🚀 New Visit to Recruiter Page</h2>
              <p><strong>Referer:</strong><span class="highlight">${referrer}</span></p>
              <p><strong>From LinkedIn:</strong><span class="highlight">${isFromLinkedIn ? "Yes ✅" : "No ❌"}</span></p>
              <p><strong>Time:</strong> ${safeData?.timestamp}</p>
              <p><strong>Browser:</strong> ${safeData?.browser}</p>
              <p><strong>Platform:</strong> ${safeData?.platform}</p>
              <p><strong>Mobile:</strong> ${safeData?.mobile}</p>
              <p><strong>User Agent:</strong> ${safeData?.userAgent}</p>
              <p><strong>Language:</strong> ${safeData?.language}</p>
              <p><strong>Screen Size:</strong> ${safeData?.screenSize}</p>
              <p><strong>Timezone:</strong> ${safeData?.timezone}</p>
              <p><strong>IP Address:</strong> ${safeData?.ip}</p>
              <h3>🌍 Geolocation</h3>
              <p><strong>City:</strong> ${geoData?.city}</p>
              <p><strong>Region:</strong> ${geoData?.region}</p>
              <p><strong>Country:</strong> ${geoData?.country_name}</p>
              <p><strong>ISP:</strong> ${geoData?.org}</p>
              <p><strong>ASN:</strong> ${geoData?.asn}</p>
              <p><small>This email was automatically generated when someone visited your recruiter page.</small></p>
              <div class="footer">
                <a href="https://www.serbyte.net" target="_blank" rel="noopener noreferrer"><img src=${serbyteDataUrl} alt="Serbyte Logo" class="logo" /></a>
                <p>
                  <strong>Email:</strong><a href="mailto:info@serbyte.net" class="link">info@serbyte.net</a> | <strong>Phone:</strong
                  ><a href="tel:+12066596727" class="link">+1 (206) 659-6727</a>
                </p>
                <p>
                  <a href="https://www.serbyte.net/insights" class="link">Visit our Blog</a> |
                  <a href="https://www.serbyte.net/projects" class="link">View Our Projects</a>
                </p>
              </div>
            </div>
          </body>
        </html>
"""


minified_html = minify_html(html_email)
print(minified_html)