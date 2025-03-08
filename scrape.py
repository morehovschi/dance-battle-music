#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time
import sys
import re
import json
import pprint
import os

def collect_music_links(playwright):
    browser = playwright.chromium.launch(headless=False)  # Change to True to run in background
    context = browser.new_context()
    page = context.new_page()
    
    music_data = {}
    
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
    
    video_links = page.locator("a#video-title").all()
    if not video_links:
        print("No videos found! Exiting.")
        return {}
    
    print(f"Found {len(video_links)} videos. Starting iteration...")

    for video in video_links[:3]:  # Limit to 3 videos for testing
        video_url = video.get_attribute("href")
        if not video_url:
            continue
        full_video_url = f"https://www.youtube.com{video_url}"
        
        print(f"\nChecking video: {full_video_url}")
        video.click()
        
        time.sleep(5)

        try:
            more_button = page.get_by_role("button", name="...more")
            if more_button:
                print("Clicking 'More' in the description...")
                more_button.click()
                time.sleep(3)

            # Locate the "Music" section using its actual container
            music_section = page.locator("#structured-description ytd-horizontal-card-list-renderer")
            if not music_section.count():
                print("No music section found, skipping.")
                page.go_back()
                time.sleep(3)
                continue
            
            print("Music section found! Extracting data...")

            # Extract all links inside the Music section
            music_items = music_section.locator("a").all()
            # per video music links
            video_music_links = []

            print(f"Found {len(music_items)} items in the Music section.")
            
            # Debug: Print all raw attributes of elements
            for idx, item in enumerate(music_items):
                try:
                    music_url = item.get_attribute("href")
                    music_text = item.inner_text()
                    print(f"[{idx+1}] {music_text}\n{music_url}\n")

                    if not music_url:
                        continue

                    # usually there is an extra item here with the text "Music" and
                    # a link that is irrelevant for our purposes; skip it
                    if music_text == "Music" and "channel" in music_url:
                        continue
                    
                    video_music_links.append( f"https://www.youtube.com{music_url}" )

                except Exception as e:
                    print(f"  Error extracting item {idx+1}: {e}")

            if video_music_links:
                music_data[full_video_url] = video_music_links
                print(f"Added {len(video_music_links)} music links for {full_video_url}")

        except Exception as e:
            print(f"Error processing video: {e}")
        
        page.goto(f"https://www.youtube.com/results?search_query={search_query}")
        time.sleep(5)

    context.close()
    browser.close()
    
    return music_data

if __name__ == "__main__":
    result = {}
    with sync_playwright() as playwright:
        result = collect_music_links(playwright)
        print("\nCollected Music Data:")
        pprint.pp( result )

    # if data file already exists, increment iteration number so as to not overwrite
    data_item_num = 0
    fname = f"data/music_links_{data_item_num}.json"
    while os.path.isfile( fname ):
        data_item_num += 1
        fname = f"data/music_links_{data_item_num}.json"    

    if result:
        with open( fname, "w" ) as f:
            json.dump( result, f )
    else:
        print( "Result is empty. Not writing." )
