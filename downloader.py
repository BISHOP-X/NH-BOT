import os
import re
import requests
from PIL import Image
from bs4 import BeautifulSoup
import img2pdf
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession
import dns.resolver
import logging

logger = logging.getLogger(__name__)


class NHentaiDownloader:
    """NHentai downloader with PDF conversion"""
    
    def __init__(self, dns_server="8.8.8.8", max_workers=6):
        self.max_workers = max_workers
        self._setup_dns(dns_server)
    
    def _setup_dns(self, dns_server):
        """Configure DNS resolver"""
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            dns.resolver.override_system_resolver(resolver)
            logger.info(f"DNS configured: {dns_server}")
        except Exception as e:
            logger.warning(f"Failed to set DNS: {e}")
    
    def _clean_filename(self, text):
        """Remove invalid filename characters"""
        return "".join(c for c in text if c.isalnum() or c in (' ', '-', '_'))
    
    def get_manga_info(self, code):
        """Fetch manga information from nhentai"""
        try:
            url = f"https://nhentai.net/g/{code}/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title_tag = soup.find(itemprop="image")
            if not title_tag:
                return None
            
            title_parts = str(title_tag).split("/")
            server = title_parts[2][1]  # Extract server number
            path = title_parts[4]
            
            # Extract title from page
            page_text = soup.get_text()
            title = page_text.split('»')[0].strip()
            
            # Extract page count
            text_parts = page_text.split(':')
            page_count = 0
            for i in range(len(text_parts)):
                if 'Pages' in text_parts[i]:
                    page_count = text_parts[i+1].replace('\t', '').split('\n')[1].strip()
                    break
            
            logger.info(f"Manga info - Title: {title}, Pages: {page_count}, Server: {server}, Path: {path}")
            return (title, int(page_count), server, path)
            
        except Exception as e:
            logger.error(f"Error fetching manga info for {code}: {e}")
            return None
    
    def download_and_convert(self, code, title, page_count):
        """Download all pages and convert to PDF"""
        try:
            # Get full manga info
            manga_info = self.get_manga_info(code)
            if not manga_info:
                return None
            
            title, page_count, server, path = manga_info
            
            # Create temporary directory
            temp_dir = f"temp_{code}"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Build base URL
            base_url = f"https://i{server}.nhentai.net/galleries/{path}/"
            
            # Download all pages
            logger.info(f"Downloading {page_count} pages...")
            downloaded_files = self._download_pages(base_url, page_count, temp_dir, code)
            
            if len(downloaded_files) != page_count:
                logger.warning(f"Only downloaded {len(downloaded_files)}/{page_count} pages")
            
            # Convert to PDF
            clean_title = self._clean_filename(title)
            pdf_filename = f"{code}_{clean_title[:50]}.pdf"
            pdf_path = os.path.join(temp_dir, pdf_filename)
            
            logger.info(f"Converting {len(downloaded_files)} images to PDF...")
            with open(pdf_path, "wb") as f:
                f.write(img2pdf.convert(downloaded_files))
            
            # Clean up image files
            for img_file in downloaded_files:
                try:
                    os.remove(img_file)
                except Exception as e:
                    logger.warning(f"Failed to remove {img_file}: {e}")
            
            logger.info(f"PDF created: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error in download_and_convert: {e}")
            return None
    
    def _download_pages(self, base_url, page_count, temp_dir, code):
        """Download all pages concurrently"""
        session = FuturesSession(max_workers=self.max_workers)
        futures = []
        
        # Queue downloads for PNG format first
        for page_num in range(1, page_count + 1):
            url = f"{base_url}{page_num}.png"
            future = session.get(url)
            future.page_num = page_num
            future.format = "png"
            futures.append(future)
        
        downloaded = {}
        jpg_retry = []
        
        # Process PNG responses
        for future in as_completed(futures):
            try:
                resp = future.result()
                if resp.status_code == 200:
                    filename = os.path.join(temp_dir, f"{code}_{future.page_num:03d}.png")
                    with open(filename, "wb") as f:
                        f.write(resp.content)
                    downloaded[future.page_num] = filename
                else:
                    jpg_retry.append(future.page_num)
            except Exception as e:
                logger.warning(f"Failed PNG download for page {future.page_num}: {e}")
                jpg_retry.append(future.page_num)
        
        # Retry failed pages with JPG format
        if jpg_retry:
            logger.info(f"Retrying {len(jpg_retry)} pages as JPG...")
            futures_jpg = []
            for page_num in jpg_retry:
                url = f"{base_url}{page_num}.jpg"
                future = session.get(url)
                future.page_num = page_num
                futures_jpg.append(future)
            
            webp_retry = []
            for future in as_completed(futures_jpg):
                try:
                    resp = future.result()
                    if resp.status_code == 200:
                        filename = os.path.join(temp_dir, f"{code}_{future.page_num:03d}.png")
                        with open(filename, "wb") as f:
                            f.write(resp.content)
                        # Convert and save as PNG
                        try:
                            img = Image.open(filename)
                            img.save(filename)
                            downloaded[future.page_num] = filename
                        except:
                            downloaded[future.page_num] = filename
                    else:
                        webp_retry.append(future.page_num)
                except Exception as e:
                    logger.warning(f"Failed JPG download for page {future.page_num}: {e}")
                    webp_retry.append(future.page_num)
            
            # Final retry with WebP format
            if webp_retry:
                logger.info(f"Final retry for {len(webp_retry)} pages as WebP...")
                futures_webp = []
                for page_num in webp_retry:
                    url = f"{base_url}{page_num}.webp"
                    future = session.get(url)
                    future.page_num = page_num
                    futures_webp.append(future)
                
                for future in as_completed(futures_webp):
                    try:
                        resp = future.result()
                        if resp.status_code == 200:
                            filename = os.path.join(temp_dir, f"{code}_{future.page_num:03d}.png")
                            with open(filename, "wb") as f:
                                f.write(resp.content)
                            try:
                                img = Image.open(filename)
                                img.save(filename)
                                downloaded[future.page_num] = filename
                            except:
                                downloaded[future.page_num] = filename
                        else:
                            logger.error(f"Failed to download page {future.page_num}")
                    except Exception as e:
                        logger.error(f"Failed WebP download for page {future.page_num}: {e}")
        
        # Return files in order
        sorted_files = [downloaded[page_num] for page_num in sorted(downloaded.keys()) if page_num in downloaded]
        return sorted_files
