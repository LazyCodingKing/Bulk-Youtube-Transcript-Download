#!/usr/bin/env python3
"""
YouTube Transcript Extractor
A Linux application to download transcripts from YouTube channels or playlists using Playwright
"""

import asyncio
import json
import os
import re
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading

# --- SET CONCURRENCY LIMIT ---
# Number of videos to download at the same time.
# 5 is a safe default. Increase (e.g., 10) for more speed, but risk errors.
CONCURRENT_DOWNLOADS = 5

class YouTubeTranscriptExtractor:
    def __init__(self):
        self.output_dir = Path.home() / "youtube_transcripts"
        self.output_dir.mkdir(exist_ok=True)
        self.debug_mode = True
        
    async def extract_video_urls(self, url, browser, progress_callback):
        """Extract all video URLs from a channel or playlist"""
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        try:
            # --- URL CHECK ---
            if '/c/' in url or '/user/' in url or '/@' in url:
                if not url.endswith(('/videos', '/videos/')):
                    url = url.rstrip('/') + '/videos'
                    progress_callback(f"Channel URL detected. Forcing '/videos' tab: {url}")
            
            progress_callback(f"Loading URL: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)
            
            # Accept cookies if popup appears
            try:
                accept_button = page.get_by_role("button", name="Accept all")
                if not await accept_button.count():
                     accept_button = page.locator(
                        'button:has-text("Accept"), button:has-text("Reject")'
                     ).first
                
                if await accept_button.is_visible(timeout=5000):
                    progress_callback("Cookie popup found. Clicking 'Accept'...")
                    await accept_button.click()
                    await asyncio.sleep(2)
            except:
                pass 
            
            progress_callback("Scrolling to load all videos (this may take a while)...")
            
            # --- START: IMPROVED SCROLLING LOGIC ---
            previous_height = -1
            patience = 0
            max_patience = 5 # Stop after 5 consecutive scrolls with no new content
            scroll_attempts = 0
            
            while patience < max_patience:
                await page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
                await asyncio.sleep(2.5) # Give time for content to load
                
                current_height = await page.evaluate("document.documentElement.scrollHeight")
                
                if current_height == previous_height:
                    patience += 1
                    progress_callback(f"Scroll {scroll_attempts}: No new content... (Patience {patience}/{max_patience})")
                else:
                    patience = 0 # Reset patience
                    previous_height = current_height
                    progress_callback(f"Scroll {scroll_attempts}: Loaded new videos. (Height: {current_height})")
                
                scroll_attempts += 1
                
                if scroll_attempts > 200: # Safety break for massive channels
                    progress_callback("Reached 200 scroll attempts, stopping.")
                    break
            
            progress_callback(f"Scrolling complete after {scroll_attempts} attempts.")
            # --- END: IMPROVED SCROLLING LOGIC ---
            
            await asyncio.sleep(3)
            
            progress_callback("Extracting video links...")
            
            video_links = await page.evaluate("""
                () => {
                    const links = [];
                    const selectors = [
                        'a#video-title', 'a#video-title-link',
                        'a.yt-simple-endpoint.style-scope.ytd-video-renderer',
                        'ytd-video-renderer a#video-title',
                        'ytd-grid-video-renderer a#video-title',
                        'ytd-playlist-video-renderer a#video-title'
                    ];
                    
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {
                            if (el.href && el.href.includes('watch?v=')) {
                                links.push({
                                    url: el.href.split('&')[0],
                                    title: el.title || el.textContent.trim()
                                });
                            }
                        }
                        if (links.length > 0) break;
                    }
                    return links;
                }
            """)
            
            # Remove duplicates
            seen = set()
            unique_videos = []
            for video in video_links:
                if video['url'] not in seen and video['title']:
                    seen.add(video['url'])
                    unique_videos.append(video)
            
            progress_callback(f"Found {len(unique_videos)} unique videos")
            
            return unique_videos
            
        except Exception as e:
            progress_callback(f"Error extracting videos: {str(e)}")
            return []
        finally:
            await context.close()
    
    async def get_transcript(self, video_url, video_title, browser, progress_callback):
        """Get transcript for a single video"""
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        try:
            # Shorten video title for logging
            log_title = (video_title[:50] + '...') if len(video_title) > 50 else video_title
            
            progress_callback(f"  [STARTING] {log_title}")
            await page.goto(video_url, wait_until="domcontentloaded", timeout=60000)
            
            # Get actual video title if not provided
            if not video_title or video_title == 'Video (title will be extracted)':
                try:
                    video_title_element = page.locator('h1.ytd-watch-metadata yt-formatted-string')
                    if await video_title_element.count() > 0:
                         video_title = await video_title_element.inner_text()
                    else:
                         video_title = "Unknown Video"
                except:
                    video_title = "Unknown Video"
            
            await page.wait_for_selector('video', timeout=20000)
            
            transcript_opened = False
            
            try:
                await page.get_by_role("button", name="...more").click(timeout=10000)
                await asyncio.sleep(0.5) # Faster wait
                await page.get_by_role("button", name="Show transcript").click(timeout=5000)
                await page.get_by_role("heading", name="Transcript").wait_for(
                    state="visible", timeout=10000
                )
                transcript_opened = True

            except Exception as e:
                # One last attempt: Sometimes the panel is *already* open
                try:
                    if await page.get_by_role("heading", name="Transcript").is_visible(timeout=1000):
                        progress_callback(f"  [INFO] Transcript panel was already open for {log_title}")
                        transcript_opened = True
                    else:
                        raise e
                except Exception:
                    progress_callback(f"  [NO TRANSCRIPT] {log_title}")
                    return None 
            
            if not transcript_opened:
                return None
            
            await asyncio.sleep(1) # Wait for segments to load
            
            transcript_segments = await page.evaluate("""
                () => {
                    let segments = [];
                    const renderers = document.querySelectorAll('ytd-transcript-segment-renderer');
                    if (renderers.length > 0) {
                        for (const seg of renderers) {
                            const timestamp = seg.querySelector('.segment-timestamp, [class*="timestamp"]')?.textContent?.trim();
                            const text = seg.querySelector('.segment-text, [class*="segment-text"]')?.textContent?.trim();
                            if (text) segments.push({ timestamp: timestamp || '', text });
                        }
                        return segments;
                    }
                    return segments;
                }
            """)
            
            if transcript_segments and len(transcript_segments) > 0:
                progress_callback(f"  [EXTRACTED] {log_title} ({len(transcript_segments)} segments)")
                # Return the *actual* title we found
                return transcript_segments, video_title
            else:
                progress_callback(f"  [NO SEGMENTS] {log_title}")
                return None
                
        except Exception as e:
            progress_callback(f"  [ERROR] {log_title}: {str(e)}")
            return None
        finally:
            await context.close()
    
    def format_transcript(self, segments):
        """Format transcript segments into readable paragraphs"""
        if not segments:
            return ""
        
        text = " ".join(seg['text'] for seg in segments if seg['text'])
        text = text.replace('  ', ' ').strip()
        
        sentences = []
        current = ""
        
        for char in text:
            current += char
            if char in '.!?' and len(current) > 20:
                sentences.append(current.strip())
                current = ""
        if current:
            sentences.append(current.strip())
        
        paragraphs = []
        current_para = []
        for i, sentence in enumerate(sentences):
            current_para.append(sentence)
            if len(current_para) >= 4 or i == len(sentences) - 1:
                paragraphs.append(" ".join(current_para))
                current_para = []
        
        return "\n\n".join(paragraphs)

    async def worker(self, video, browser, semaphore, progress_callback):
        """
        A worker that acquires a semaphore, gets a transcript,
        and saves the files.
        """
        async with semaphore:
            # Call get_transcript
            result = await self.get_transcript(video['url'], video['title'], browser, progress_callback)
            
            # get_transcript now returns (transcript_segments, actual_title) or None
            if result:
                transcript, actual_title = result
                
                # Use the *actual* title from the page if we found it
                video['title'] = actual_title 
                
                # --- Save file logic (moved from process_url) ---
                safe_title = re.sub(r'[^\w\s-]', '', video['title'])[:100].strip()
                if not safe_title or safe_title == "Unknown Video":
                    safe_title = video['url'].split('watch?v=')[-1]

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{safe_title}_{timestamp}.txt"
                filepath = self.output_dir / filename
                
                formatted_text = self.format_transcript(transcript)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Video: {video['title']}\n")
                    f.write(f"URL: {video['url']}\n")
                    f.write(f"Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*80 + "\n\n")
                    f.write(formatted_text)
                
                # Save raw version
                raw_filename = f"{safe_title}_{timestamp}_raw.txt"
                raw_filepath = self.output_dir / raw_filename
                
                with open(raw_filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Video: {video['title']}\n")
                    f.write(f"URL: {video['url']}\n")
                    f.write(f"Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*80 + "\n\n")
                    
                    for segment in transcript:
                        if segment['text']:
                            timestamp_str = f"[{segment['timestamp']}] " if segment['timestamp'] else ""
                            f.write(f"{timestamp_str}{segment['text']}\n")
                
                progress_callback(f"  [SAVED] {filename}")
                return {'video': video['title'], 'status': 'Success', 'file': filename}
            else:
                # get_transcript already logged the failure
                return {'video': video['title'], 'status': 'No transcript available'}

    async def process_url(self, url, progress_callback):
        """Main processing function"""
        async with async_playwright() as p:
            progress_callback("Launching browser...")
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            try:
                if 'watch?v=' in url:
                    progress_callback("Detected single video URL")
                    video_id = url.split('watch?v=')[1].split('&')[0]
                    videos = [{
                        'url': f'https://www.youtube.com/watch?v={video_id}',
                        'title': 'Video (title will be extracted)'
                    }]
                else:
                    videos = await self.extract_video_urls(url, browser, progress_callback)
                
                if not videos:
                    progress_callback("No videos found! Please check the URL.")
                    return
                
                progress_callback(f"\n{'='*60}")
                progress_callback(f"Found {len(videos)} videos. Starting concurrent extraction...")
                progress_callback(f"Processing {CONCURRENT_DOWNLOADS} videos at a time.")
                progress_callback(f"{'='*60}\n")
                
                # --- Concurrency Logic ---
                semaphore = asyncio.Semaphore(CONCURRENT_DOWNLOADS)
                tasks = []
                
                for video in videos:
                    # Create a task for each worker
                    tasks.append(self.worker(video, browser, semaphore, progress_callback))
                
                # Run all tasks concurrently and wait for them to finish
                all_results = await asyncio.gather(*tasks)
                # --- End Concurrency Logic ---
                
                # Process results
                successful = 0
                for result in all_results:
                    if result and result['status'] == 'Success':
                        successful += 1
                
                # Save summary
                summary_file = self.output_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(all_results, f, indent=2, ensure_ascii=False)
                
                progress_callback(f"\n{'='*60}")
                progress_callback(f"Extraction complete!")
                progress_callback(f"Successful: {successful}/{len(videos)}")
                progress_callback(f"Output directory: {self.output_dir}")
                progress_callback(f"{'='*60}")
                
            finally:
                await browser.close()


class TranscriptExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Transcript Extractor (Playwright)")
        self.root.geometry("900x700")
        
        self.extractor = YouTubeTranscriptExtractor()
        self.is_running = False
        
        self.setup_ui()
    
    def setup_ui(self):
        # URL input
        url_frame = ttk.Frame(self.root, padding="10")
        url_frame.pack(fill=tk.X)
        
        ttk.Label(url_frame, text="YouTube Channel/Playlist URL:").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Example text
        example_frame = ttk.Frame(self.root, padding="5")
        example_frame.pack(fill=tk.X)
        ttk.Label(example_frame, text="Examples: Single video, channel (e.g., .../c/ChannelName/videos), or playlist URL", 
                 foreground="gray").pack(side=tk.LEFT, padx=15)

        # Output Folder Frame
        output_frame = ttk.Frame(self.root, padding="5 0 10 10")
        output_frame.pack(fill=tk.X)

        ttk.Button(output_frame, text="Change Output Folder", command=self.change_output_folder).pack(side=tk.LEFT, padx=(0, 10))

        self.output_dir_var = tk.StringVar()
        self.output_dir_var.set(f"Saving to: {self.extractor.output_dir}")
        
        ttk.Label(output_frame, textvariable=self.output_dir_var, foreground="gray").pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(button_frame, text="Start Extraction", command=self.start_extraction)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Open Output Folder", command=self.open_output_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        # --- MODIFIED: Added Merge All button ---
        self.merge_select_button = ttk.Button(button_frame, text="Merge Selected Files", command=self.merge_selected_files)
        self.merge_select_button.pack(side=tk.LEFT, padx=5)
        
        self.merge_all_button = ttk.Button(button_frame, text="Merge All Files", command=self.merge_all_files)
        self.merge_all_button.pack(side=tk.LEFT, padx=5)
        # --- END MODIFICATION ---
        
        # Progress display
        progress_frame = ttk.Frame(self.root, padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(progress_frame, text="Progress Log:").pack(anchor=tk.W)
        
        self.progress_text = scrolledtext.ScrolledText(progress_frame, height=30, state='disabled', 
                                                       font=('Courier', 9))
        self.progress_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_label = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def change_output_folder(self):
        new_dir = filedialog.askdirectory(
            initialdir=self.extractor.output_dir,
            title="Select Output Folder"
        )
        
        if new_dir: 
            self.extractor.output_dir = Path(new_dir)
            self.extractor.output_dir.mkdir(exist_ok=True) 
            self.output_dir_var.set(f"Saving to: {self.extractor.output_dir}")
            self.log_progress(f"Output folder changed to: {new_dir}")

    def merge_selected_files(self):
        output_dir = self.extractor.output_dir

        # 1. Ask user to select multiple .txt files
        file_paths = filedialog.askopenfilenames(
            initialdir=output_dir,
            title="Select Transcript Files to Merge",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not file_paths:
            self.log_progress("Merge (Selected) cancelled by user.")
            return

        # 2. Ask user where to save the merged file
        save_path = filedialog.asksaveasfilename(
            initialdir=output_dir,
            title="Save Merged Transcript As",
            defaultextension=".txt",
            initialfile="merged_transcripts.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not save_path:
            self.log_progress("Merge (Selected) save cancelled by user.")
            return

        # 3. Read and merge files
        try:
            with open(save_path, 'w', encoding='utf-8') as merged_file:
                merged_file.write(f"MERGED TRANSCRIPTS (Selected Files)\n")
                merged_file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                merged_file.write(f"Total files: {len(file_paths)}\n")
                merged_file.write("="*80 + "\n\n")

                for idx, file_path_str in enumerate(file_paths):
                    file_path = Path(file_path_str)
                    
                    if file_path.exists():
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            merged_file.write(content)
                            
                            if idx < len(file_paths) - 1:
                                merged_file.write("\n\n" + "="*80 + "\n\n")
                    else:
                        self.log_progress(f"  [WARNING] File not found, skipping: {file_path.name}")
            
            self.log_progress(f"Successfully merged {len(file_paths)} transcripts to {save_path}")
            messagebox.showinfo("Success", f"Merged {len(file_paths)} transcripts to {save_path}")

        except Exception as e:
            self.log_progress(f"  [ERROR] Failed to merge: {e}")
            messagebox.showerror("Error", f"An error occurred during merging: {e}")

    # --- NEW: Merge All Files Method ---
    def merge_all_files(self):
        output_dir = self.extractor.output_dir
        self.log_progress("Starting 'Merge All'...")

        # 1. Find all .txt files, excluding raw files
        try:
            # We sort them by name
            transcript_files = sorted([
                f for f in output_dir.glob("*.txt") if not f.name.endswith("_raw.txt")
            ])
            
            if not transcript_files:
                messagebox.showinfo("Info", "No transcript files found in the output folder to merge.")
                self.log_progress("No non-raw .txt files found.")
                return
            
            self.log_progress(f"Found {len(transcript_files)} files to merge.")

        except Exception as e:
            messagebox.showerror("Error", f"Error scanning directory: {e}")
            self.log_progress(f"  [ERROR] Error scanning directory: {e}")
            return

        # 2. Ask user where to save the merged file
        save_path = filedialog.asksaveasfilename(
            initialdir=output_dir,
            title="Save Merged Transcript As",
            defaultextension=".txt",
            initialfile="merged_ALL_transcripts.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not save_path:
            self.log_progress("Merge (All) save cancelled by user.")
            return

        # 3. Read and merge files
        try:
            with open(save_path, 'w', encoding='utf-8') as merged_file:
                merged_file.write(f"MERGED TRANSCRIPTS (All Files)\n")
                merged_file.write(f"Source Folder: {output_dir}\n")
                merged_file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                merged_file.write(f"Total files: {len(transcript_files)}\n")
                merged_file.write("="*80 + "\n\n")

                for idx, file_path in enumerate(transcript_files):
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        merged_file.write(content)
                        
                        if idx < len(transcript_files) - 1:
                            merged_file.write("\n\n" + "="*80 + "\n\n")
            
            self.log_progress(f"Successfully merged {len(transcript_files)} transcripts to {save_path}")
            messagebox.showinfo("Success", f"Merged {len(transcript_files)} transcripts to {save_path}")

        except Exception as e:
            self.log_progress(f"  [ERROR] Failed to merge: {e}")
            messagebox.showerror("Error", f"An error occurred during merging: {e}")
    # --- END NEW ---

    def log_progress(self, message):
        """Log messages in a thread-safe way"""
        try:
            if not self.root.winfo_exists():
                 return
            
            # Use after() to schedule the update on the main thread
            self.root.after(0, self._update_log_text, message)
        except tk.TclError:
            pass # Ignore errors if window is closing

    def _update_log_text(self, message):
        """Internal method to update the GUI, runs on main thread"""
        try:
            self.progress_text.config(state='normal')
            self.progress_text.insert(tk.END, message + "\n")
            self.progress_text.see(tk.END)
            self.progress_text.config(state='disabled')
            # No root.update() needed here, after() handles it
        except tk.TclError:
            pass # Ignore if widget is destroyed

    def clear_log(self):
        self.progress_text.config(state='normal')
        self.progress_text.delete(1.0, tk.END)
        self.progress_text.config(state='disabled')
    
    def start_extraction(self):
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        if not ('youtube.com' in url or 'youtu.be' in url):
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return
        
        if self.is_running:
            messagebox.showwarning("Warning", "Extraction already in progress")
            return
        
        self.is_running = True
        self.start_button.config(state='disabled')
        self.status_label.config(text="Extracting...")
        self.clear_log()
        
        # Run in separate thread
        thread = threading.Thread(target=self.run_extraction, args=(url,))
        thread.daemon = True
        thread.start()
    
    def run_extraction(self, url):
        """
        This runs in a separate thread, so it's safe
        to create and run a new asyncio event loop.
        """
        try:
            asyncio.run(self.extractor.process_url(url, self.log_progress))
            self.root.after(0, self.status_label.config, {'text': 'Extraction complete!'})
        except Exception as e:
            self.log_progress(f"\n❌ Error: {str(e)}")
            self.root.after(0, self.status_label.config, {'text': 'Error occurred'})
        finally:
            self.is_running = False
            self.root.after(0, self.start_button.config, {'state': 'normal'})
    
    def open_output_folder(self):
        os.system(f'xdg-open "{self.extractor.output_dir}"')


def main():
    root = tk.Tk()
    app = TranscriptExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()