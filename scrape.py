#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time
import re
import json
import pprint
import os
import argparse

def save_data_file( fname, data_dict ):
    """
    FIXME
    """
    data_item_num = 0
    numbered_fname = f"{fname}_{data_item_num}"
    while os.path.isfile(numbered_fname + ".json"):
        data_item_num += 1
        numbered_fname = f"{fname}_{data_item_num}"
        
    with open(numbered_fname + ".json", "w") as f:
        json.dump(data_dict, f)

    return f"{fname}_{data_item_num}.json"

def youtube_id( url ):
    """
    Helper that reduces a YouTube video link to the unique video identifier
    """
    if "watch?v=" not in url:
        # already reduced to id
        return url

    # identifier starts after this specific url sequence and takes 11 characters
    return url[ url.find( "watch?v=" ) + 8 : url.find( "watch?v=" ) + 19 ]

def scroll_down(page):
    """Scroll down the page to load more videos."""
    page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
    time.sleep(3)  # Wait for new videos to load

def collect_music_links(playwright, n_results, n_attempts, processed_data=None,
                        intermediate_saving=True):
    browser = playwright.chromium.launch(headless=False)  # Change to True to run in background
    context = browser.new_context()
    page = context.new_page()

    processed_data = processed_data if processed_data else {}
    if processed_data is None:
        processed_data = {}

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
    new_video_urls = 0
    while videos_processed < n_attempts:
        # Scroll down to load more videos if needed
        if videos_processed > 0 and videos_processed % 5 == 0:
            print("Scrolling down to load more videos...")
            scroll_down(page)
            time.sleep(5)  # Wait for new videos to load

            if intermediate_saving:
                save_data_file( "data/music_links", processed_data )

        # Get all video links on the page
        video_links = page.locator("a#video-title").all()
        if not video_links:
            print("No videos found! Exiting.")
            return processed_data

        print(f"Found {len(video_links)} videos. Processed {videos_processed}/{n_attempts}")

        # Process only new videos
        for video in video_links[videos_processed:]:  # Only process new videos
            videos_processed += 1

            if videos_processed >= n_attempts:
                break

            video_url = video.get_attribute("href")
            if not video_url:
                continue
            video_id = youtube_id( video_url )

            # Skip if the video has already been processed
            if video_id in processed_data:
                print(f"Skipping already processed video: {video_id}")
                continue

            print(f"\nChecking video {videos_processed}/{n_attempts}: {video_id}")
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

                        music_id = youtube_id( music_url )
                        if video_id == music_id:
                            with open( "problem-video-report.txt", "a" ) as f:
                                f.writelines( [ page.content() ] )
                            page.screenshot(path="screenshot.png")
                            break
                        video_music_links.append( music_id )

                    except Exception as e:
                        print(f"  Error extracting item {idx+1}: {e}")

                if video_music_links:
                    processed_data[video_id] = video_music_links
                    new_video_urls += 1
                    print(f"Added {len(video_music_links)} music links for {video_id}")

                if new_video_urls >= n_results:
                    print(f"Target number of results ({n_results}) reached!")
                    context.close()
                    browser.close()
                    return processed_data

            except Exception as e:
                print(f"Error processing video: {e}")

            if video_id == "RQurJCHgD1w":
                with open( "problem_video_found", "a" ) as f:
                    f.writelines( video_music_links )

            # Go back to the search results page
            page.goto(f"https://www.youtube.com/results?search_query={search_query}")
            time.sleep(5)

    print(f"Processed {videos_processed} videos. Returning collected data.")
    context.close()
    browser.close()

    return processed_data

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

    with sync_playwright() as playwright:
        processed_data = collect_music_links(playwright, args.n_results, args.n_attempts, processed_data)
        print("\nCollected Music Data:")
        pprint.pp(processed_data)

    if processed_data:
        save_data_file( "data/music_links", processed_data )
    else:
        print("Result is empty. Not writing.")
