import asyncio
from playwright.async_api import async_playwright

async def close_cookies_popup(page):
    try:
        print("Checking for cookies popup")
        await page.click("text=AGREE", timeout=10000)
        await page.wait_for_selector("text=AGREE", state="detached", timeout=10000)
        print("Cookies popup closed")
    except Exception as e:
        print("No cookies popup found or failed to close:", e)

async def get_designer_links(page):
    url = "https://www.fragrantica.com/designers/"
    print(f"Navigating to {url}")
    await page.goto(url)
    await close_cookies_popup(page)
    print("Waiting for selector a[href^='/designers/']")
    await page.wait_for_selector("a[href^='/designers/']", timeout=60000)
    designer_elements = await page.query_selector_all("a[href^='/designers/']")
    designer_links = ["https://www.fragrantica.com" + await element.get_attribute('href') for element in designer_elements]
    print(f"Found {len(designer_links)} designer links")
    return designer_links

async def get_perfume_links(page, designer_url):
    print(f"Navigating to {designer_url}")
    await page.goto(designer_url)
    await close_cookies_popup(page)
    print("Waiting for selector a[href^='/perfume/']")
    await page.wait_for_selector("a[href^='/perfume/']", timeout=60000)
    perfume_elements = await page.query_selector_all("a[href^='/perfume/']")
    perfume_links = ["https://www.fragrantica.com" + await element.get_attribute('href') for element in perfume_elements]
    print(f"Found {len(perfume_links)} perfume links for {designer_url}")
    return perfume_links

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Cambiar a headless=False para ver el navegador en acción
        page = await browser.new_page()

        try:
            designer_links = await get_designer_links(page)

            all_perfume_links = {}
            for designer_url in designer_links:
                designer_name = designer_url.split("/")[-2]
                perfume_links = await get_perfume_links(page, designer_url)
                all_perfume_links[designer_name] = perfume_links

            for designer, links in all_perfume_links.items():
                print(f"Designer: {designer}")
                for link in links:
                    print(link)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())










