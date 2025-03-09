#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time
import re
import json
import pprint
import os
import argparse

def scroll_down(page):
    """Scroll down the page to load more videos."""
    page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
    time.sleep(3)  # Wait for new videos to load

def collect_music_links(playwright, n_results, n_attempts, processed_data=None):
    browser = playwright.chromium.launch(headless=False)  # Change to True to run in background
    context = browser.new_context()
    page = context.new_page()

    music_data = processed_data if processed_data else {}

    print("Opening YouTube...")
    page.goto("https://www.youtube.com/")
    time.sleep(3)

    try:
        reject_button = page.get_by_role("button", name=re.compile("Reject", re.IGNORECASE))
        if reject_button:
            print("Clicking 'Reject all'...")
            reject_button.click()
            time.sleep(3)
    except Exception as e:
        print(f"Cookie rejection button not found: {e}")

    search_query = "hip hop dance battle"
    print(f"Searching for: {search_query}")

    search_box = page.get_by_role("combobox", name="Search")
    search_box.fill(search_query)
    search_box.press("Enter")

    time.sleep(5)

    videos_processed = 0
    while videos_processed < n_attempts:
        # Scroll down to load more videos if needed
        if videos_processed > 0 and videos_processed % 20 == 0:  # Scroll every 20 videos
            print("Scrolling down to load more videos...")
            scroll_down(page)
            time.sleep(5)  # Wait for new videos to load

        # Get all video links on the page
        video_links = page.locator("a#video-title").all()
        if not video_links:
            print("No videos found! Exiting.")
            return music_data

        print(f"Found {len(video_links)} videos. Processed {videos_processed}/{n_attempts}")

        # Process only new videos
        for video in video_links[videos_processed:]:  # Only process new videos
            if videos_processed >= n_attempts:
                break

            videos_processed += 1
            video_url = video.get_attribute("href")
            if not video_url:
                continue
            full_video_url = f"https://www.youtube.com{video_url}"

            # Skip if the video has already been processed
            if full_video_url in music_data:
                print(f"Skipping already processed video: {full_video_url}")
                continue

            print(f"\nChecking video {videos_processed}/{n_attempts}: {full_video_url}")
            video.click()
            time.sleep(5)

            try:
                more_button = page.get_by_role("button", name="...more")
                if more_button:
                    print("Clicking 'More' in the description...")
                    more_button.click()
                    time.sleep(3)

                music_section = page.locator("#structured-description ytd-horizontal-card-list-renderer")
                if not music_section.count():
                    print("No music section found, skipping.")
                    page.go_back()
                    time.sleep(3)
                    continue

                print("Music section found! Extracting data...")

                music_items = music_section.locator("a").all()
                video_music_links = []

                print(f"Found {len(music_items)} items in the Music section.")

                for idx, item in enumerate(music_items):
                    try:
                        music_url = item.get_attribute("href")
                        music_text = item.inner_text()
                        print(f"[{idx+1}] {music_text}\n{music_url}\n")

                        if not music_url:
                            continue

                        if music_text == "Music" and "channel" in music_url:
                            continue

                        video_music_links.append(f"https://www.youtube.com{music_url}")

                    except Exception as e:
                        print(f"  Error extracting item {idx+1}: {e}")

                if video_music_links:
                    music_data[full_video_url] = video_music_links
                    print(f"Added {len(video_music_links)} music links for {full_video_url}")

                if len(music_data) >= n_results:
                    print(f"Target number of results ({n_results}) reached!")
                    context.close()
                    browser.close()
                    return music_data

            except Exception as e:
                print(f"Error processing video: {e}")

            # Go back to the search results page
            page.goto(f"https://www.youtube.com/results?search_query={search_query}")
            time.sleep(5)

    print(f"Processed {videos_processed} videos. Returning collected data.")
    context.close()
    browser.close()

    return music_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect music links from YouTube search results.")
    parser.add_argument("--n_results", type=int, default=10, help="Number of desired video results (default: 10)")
    parser.add_argument("--n_attempts", type=int, default=20, help="Maximum number of videos to look at (default: 20)")
    parser.add_argument("--read-processed-data-from", type=str, help="Path to a JSON file containing previously processed data")

    args = parser.parse_args()

    # Load processed data if provided
    processed_data = {}
    if args.read_processed_data_from:
        try:
            with open(args.read_processed_data_from, "r") as f:
                processed_data = json.load(f)
            print(f"Loaded {len(processed_data)} previously processed URLs from {args.read_processed_data_from}")
        except Exception as e:
            print(f"Error loading processed data: {e}")

    result = {}
    with sync_playwright() as playwright:
        result = collect_music_links(playwright, args.n_results, args.n_attempts, processed_data)
        print("\nCollected Music Data:")
        pprint.pp(result)

    data_item_num = 0
    fname = f"data/music_links_{data_item_num}.json"
    while os.path.isfile(fname):
        data_item_num += 1
        fname = f"data/music_links_{data_item_num}.json"

    if result:
        with open(fname, "w") as f:
            json.dump(result, f)
    else:
        print("Result is empty. Not writing.")
