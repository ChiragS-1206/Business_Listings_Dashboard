import re
import time
from urllib.parse import quote_plus
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


CITIES = {
    "Delhi": "Delhi",
    "Chandigarh": "Chandigarh",
    "Mumbai": "Mumbai",
    "Rajasthan": "Jaipur, Rajasthan",
    "Tamil Nadu": "Chennai, Tamil Nadu",
    "Goa": "Goa",
}

CATEGORY_QUERIES = {
    "Restaurant": ["restaurants"],
    "Gym": ["gyms"],
    "Salon": ["beauty salons"],
    "Hotel": ["hotels"],
    "Grocery": ["grocery stores"],
}

SEARCH_URL = "https://www.google.com/maps/search/{q}"

TARGET_ROWS = 20       
MAX_SCROLLS = 15
WAIT_FOR_NEW_MS = 5000
OUTPUT = "gmaps_data.csv"


CARD_SELECTOR = "a.hfpxzc"
FEED_SELECTOR = "div[role='feed']"

PHONE_RE = re.compile(r"(?:\+91[\s-]?)?0?[6-9]\d{4}[\s-]?\d{5}")
COLUMNS = ["business_name", "category", "city", "address", "phone", "source"]

SCROLL_JS = """
async (feedSel) => {
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    const feed = document.querySelector(feedSel);
    if (!feed) return;

    // WIGGLE: thoda upar, phir neeche -> scroll event pakka fire hota hai
    feed.scrollTop = Math.max(0, feed.scrollTop - 600);
    feed.dispatchEvent(new Event('scroll'));
    await sleep(200);
    for (let i = 0; i < 5; i++) {
        feed.scrollTop += 500;
        feed.dispatchEvent(new Event('scroll'));
        await sleep(120);
    }
    feed.scrollTop = feed.scrollHeight;
    feed.dispatchEvent(new Event('scroll'));
}
"""


def count_cards(page):
    return page.locator(CARD_SELECTOR).count()


def end_of_list(page):
    try:
        return page.locator("text=/reached the end of the list/i").first.is_visible(timeout=200)
    except Exception:
        return False


def smart_scroll(page, tag, target):
    last_count = count_cards(page)
    stagnant = 0
    asked = False
    print(f"  start: {last_count} items")

    for i in range(MAX_SCROLLS):
        if last_count >= target:
            break

        page.evaluate(SCROLL_JS, FEED_SELECTOR)

        waited, count = 0, last_count
        while waited < WAIT_FOR_NEW_MS:
            page.wait_for_timeout(300)
            waited += 300
            count = count_cards(page)
            if count > last_count:
                break

        print(f"  scroll {i+1} -> {count} items")

        if end_of_list(page):
            print("  list khatam (end of list)")
            last_count = count
            break

        if count <= last_count:
            stagnant += 1
            if stagnant == 2 and not asked:
                asked = True
                page.screenshot(path=f"debug_stall_{tag}.png")
                print("\n  >>> ATAK GAYA. Firefox mein khud left list ko neeche scroll karke dekho:")
                print("  >>>  - Naye listings aate hain?   -> mujhe terminal ka output bhejo")
                print("  >>>  - Consent/captcha popup hai? -> usse solve kar do")
                print("  >>>  - Kuch load nahi hota?       -> Maps result limit pe hai")
                input("  >>> Ho jaye to ENTER dabao... ")
                stagnant = 0
                count = count_cards(page)
                print(f"  after manual step: {count} items")
            elif stagnant >= 4:
                print("  no more new data, stopping")
                break
        else:
            stagnant = 0
        last_count = count

    print(f"  final items loaded: {last_count}")


def parse(html, category, city):
    """List se name + link + (agar dikhe to) phone nikalta hai."""
    soup = BeautifulSoup(html, "lxml")
    links = soup.select(CARD_SELECTOR)
    print(f"  using selector: {CARD_SELECTOR} ({len(links)} matches)")

    rows = []
    for a in links:
        name = (a.get("aria-label") or "").strip()
        if not name:
            continue
        container = a.parent
        text = container.get_text(" ", strip=True) if container else ""
        phones = [re.sub(r"[\s-]", "", p) for p in PHONE_RE.findall(text)]
        rows.append({
            "business_name": name,
            "category": category,
            "city": city,
            "address": "",
            "phone": ", ".join(sorted(set(phones))),
            "source": "Google Maps",
            "_url": a.get("href", ""),
        })
    return rows


def get_label(page, selector):
    try:
        lab = page.locator(selector).first.get_attribute("aria-label", timeout=1500)
        if lab and ":" in lab:
            lab = lab.split(":", 1)[1]
        return (lab or "").replace("\u202f", " ").strip()
    except Exception:
        return ""


def fetch_details(detail_page, url):
    """Har listing ka page khol ke address + phone nikalta hai."""
    try:
        detail_page.goto(url, wait_until="domcontentloaded", timeout=60000)
        detail_page.wait_for_selector("h1", timeout=8000)
    except Exception:
        return "", ""
    address = get_label(detail_page, "button[data-item-id='address']")
    phone = get_label(detail_page, "button[data-item-id^='phone']")
    phone = re.sub(r"[\s-]", "", phone)
    return address, phone


def save(all_rows):
    df = pd.DataFrame(all_rows, columns=COLUMNS)
    if df.empty:
        return df
    df = df[df["business_name"] != ""]
    df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    return df


def scrape_category(page, detail_page, category, city, place, queries, first):
    tag = f"{city.replace(' ', '_')}_{category}"
    print(f"\n🔎 Scraping {category} in {city}...")
    seen, unique = set(), []

    for n, word in enumerate(queries):
        if len(unique) >= TARGET_ROWS:
            break
        url = SEARCH_URL.format(q=quote_plus(f"{word} in {place}"))
        print(f" URL {n+1}/{len(queries)}: {url}")

        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        if first and n == 0:
            input("Listings dikh rahi hain? Consent/captcha solve karke ENTER dabao... ")

        for text in ["Accept all", "Reject all", "Maybe Later", "Not Now", "Skip", "Close"]:
            try:
                page.get_by_text(text, exact=True).first.click(timeout=300)
            except Exception:
                pass

        smart_scroll(page, tag, TARGET_ROWS - len(unique))

        html = page.content()
        rows = parse(html, category, city)
        if not rows:
            with open(f"debug_{tag}.html", "w", encoding="utf-8") as f:
                f.write(html)
            page.screenshot(path=f"debug_{tag}.png")
            print(f"  ⚠ 0 rows. Saved debug_{tag}.html / .png")

        for r in rows:
            if len(unique) >= TARGET_ROWS:
                break
            if r["_url"] in seen:
                continue
            seen.add(r["_url"])

            # address + phone ke liye listing page kholo
            addr, phone = fetch_details(detail_page, r["_url"])
            if addr:
                r["address"] = addr
            if phone:
                r["phone"] = phone
            unique.append(r)
            print(f"   [{len(unique)}/{TARGET_ROWS}] {r['business_name']}")

    for r in unique:
        r.pop("_url", None)
    print(f"{category} / {city}: {len(unique)} rows")
    return unique


def main():
    all_rows = []
    p = sync_playwright().start()
    context = None
    stop_all = False
    first = True
    try:
        context = p.firefox.launch_persistent_context(
            user_data_dir="./firefox_profile",
            headless=False,
            viewport={"width": 1366, "height": 900},
            locale="en-IN",
            firefox_user_prefs={
                "dom.webdriver.enabled": False,
                "useAutomationExtension": False,
            },
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.set_default_timeout(20000)   
        detail_page = context.new_page() 
        detail_page.set_default_timeout(20000)

        for city, place in CITIES.items():
            if stop_all:
                break
            print(f"\n==================== CITY: {city} ====================")

            for category, queries in CATEGORY_QUERIES.items():
                try:
                    all_rows += scrape_category(page, detail_page, category, city, place,
                                                queries, first=first)
                    first = False
                    save(all_rows)       
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f"{category}/{city} failed: {type(e).__name__}: {e}")
                    if "closed" in str(e).lower():
                        print("Browser band ho gaya, ab tak ka data save karke ruk raha hoon.")
                        stop_all = True
                        break
                time.sleep(1)

    except KeyboardInterrupt:
        print("\nCtrl+C: ab tak ka data save kar raha hoon...")
    finally:
        df = save(all_rows)
        try:
            if context:
                context.close()
        except Exception:
            pass
        try:
            p.stop()
        except Exception:
            pass

    if df is None or df.empty:
        print("\n❌ No data scraped. debug files check karo.")
        return
    print("\n✅ Done:")
    print(df.groupby(["city", "category"]).size().to_string())
    print(f"Total {len(df)} rows saved to {OUTPUT}")


if __name__ == "__main__":
    main()