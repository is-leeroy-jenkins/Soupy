'''
  ******************************************************************************************
      Assembly:                Soupy
      Filename:                fetchers.py
      Author:                  Terry D. Eppler
      Created:                 05-31-2022

      Last Modified By:        Terry D. Eppler
      Last Modified On:        05-01-2025
  ******************************************************************************************
  <copyright file='fetchers.py' company='Terry D. Eppler'>

	     Soupy is a python framework for web scraping information into ML pipelines.
	     Copyright ©  2022  Terry Eppler

     Permission is hereby granted, free of charge, to any person obtaining a copy
     of this software and associated documentation files (the “Software”),
     to deal in the Software without restriction,
     including without limitation the rights to use,
     copy, modify, merge, publish, distribute, sublicense,
     and/or sell copies of the Software,
     and to permit persons to whom the Software is furnished to do so,
     subject to the following conditions:

     The above copyright notice and this permission notice shall be included in all
     copies or substantial portions of the Software.

     THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
     INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
     FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT.
     IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
     DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
     ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
     DEALINGS IN THE SOFTWARE.

     You can contact me at:  terryeppler@gmail.com or eppler.terry@epa.gov

  </copyright>
  <summary>
    fetchers.py
  </summary>
  ******************************************************************************************
  '''
from __future__ import annotations
from typing import Any, Dict, Optional, Pattern
import re
import requests
from requests import Response
from .core import Result
from boogr import Error, ErrorDialog
import crawl4ai

def throw_if( name: str, value: Any ) -> None:
	'''
		
		Purpose:
		-----------
		Simple guard which raises ValueError when `value` is falsy (None, empty).
			
		Parameters:
		-----------
		name (str): Variable name used in the raised message.
		value (Any): Value to validate.
			
		Returns:
		-----------
		None: Raises ValueError when `value` is falsy.
			
	'''
	if not value:
		raise ValueError( f"Argument '{name}' cannot be empty!" )

class Fetcher:
	'''
	
		Purpose:
		--------
		Base class for fetchers. Implement `fetch(...)` in concrete subclasses.
			
	'''
	timeout: Optional[ int ]
	headers: Optional[ Dict[ str, str ] ]
	response: Optional[ Response ]
	url: Optional[ str ]
	result: Optional[ Result ]

	def __init__( self ) -> None:
		'''
		
			Purpose:
			-----------
			Base initializer. Subclasses should set defaults they require.
		
		'''
		self.timeout = None
		self.headers = None
		self.response = None
		self.url = None
		self.result = None

	def __dir__( self ) -> list[ str ]:
		'''
			
			Purpose:
			-----------
			Control ordering for introspection.
				
			Parameters:
			-----------
			None
				
			Returns:
			-----------
			list[str]: Ordered attribute/method names.
				
		'''
		return [ 'timeout', 'headers', 'response', 'url', 'result', 'fetch', 'html_to_text' ]

	def fetch( self, url: str, time: int=10, show_dialog: bool=True ) -> Result | None:
		'''
		
			Purpose:
			--------
			Abstract fetch method to be implemented by subclasses.
				
			Parameters:
			-----------
			url (str): Resource URL to fetch.
			time (int): Timeout in seconds.
			show_dialog (bool): If True, show an ErrorDialog on exception.
				
			Returns:
			---------
			Optional[Result]: Should return Result on success or None on failure.
			
		'''
		raise NotImplementedError( 'Fetcher.fetch must be implemented by a subclass.' )

class WebFetcher( Fetcher ):
	'''
		
		Purpose:
		---------
		Concrete synchronous fetcher using `requests` and minimal HTML→text
		extraction.
		
		Parameters:
		-----------
		headers (Optional[Dict[str, str]]): Optional HTTP headers; User-Agent
		auto-filled if missing.
		
		Returns:
		-----------
		None
		
	'''
	agents: Optional[ str ]
	raw_url: Optional[ str ]
	raw_html: Optional[ str ]
	re_tag: Optional[ Pattern ]
	re_ws: Optional[ Pattern ]
	response: Optional[ Response ]

	def __init__( self, headers: Optional[ Dict[ str, str ] ]=None ) -> None:
		'''
			Purpose:
			-----------
			Initialize WebFetcher with optional headers and sane defaults.
			
			Parameters:
			-----------
			headers (Optional[Dict[str, str]]): Optional headers for requests.
			
			Returns:
			-----------
			None
		'''
		super( ).__init__( )

		self.timeout = 15
		self.re_tag = re.compile( r'<[^>]+>' )
		self.re_ws = re.compile( r'\s+' )
		self.raw_url = None
		self.raw_html = None
		self.response = None

		if headers is None:
			self.headers = { }
		else:
			self.headers = dict( headers )

		self.agents = (
				'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
				'AppleWebKit/537.36 (KHTML, like Gecko) '
				'Chrome/124.0 Safari/537.36'
		)

		if 'User-Agent' not in self.headers:
			self.headers[ 'User-Agent' ] = self.agents

	def __dir__( self ) -> list[ str ]:
		'''
			
			Purpose:
			-----------
			Control visible ordering for WebFetcher.
			
			Parameters:
			-----------
			None
			
			Returns:
			-----------
			list[str]: Ordered attribute/method names.
			
		'''
		return [ 'agents', 'raw_url', 'raw_html', 'timeout', 'headers', 'fetch', 'html_to_text' ]

	def fetch( self, url: str, time: int=10  ) -> Result | None:
		'''
			
			Purpose:
			-------
			Perform an HTTP GET to fetch a page and return canonicalized Result.
				
			Parameters:
			-----------
			url (str): Absolute URL to fetch.
			time (int): Timeout seconds to use for the request.
			show_dialog (bool): If True, show an ErrorDialog on exception.
				
			Returns:
			---------
			Optional[Result]: Result with url, status, text, html, headers on success.
			
		'''
		try:
			throw_if( 'url', url )
			self.raw_url = url
			self.timeout = int( time )
			resp = requests.get( url=self.raw_url, headers=self.headers, timeout=self.timeout )
			resp.raise_for_status( )
			self.response = resp
			html = resp.text
			text = self.html_to_text( html )
			result = Result( url = resp.url, status=resp.status_code, text=text, html=html,
				headers = resp.headers )
			self.result = result
			return result
		except Exception as exc:  
			exception = Error( exc )
			exception.module = 'scrapers'
			exception.cause = 'WebFetcher'
			exception.method = 'fetch( self, url: str, time: int=10  ) -> Result'
			dialog = ErrorDialog( exception )
			dialog.show( )

	def html_to_text( self, html: str ) -> str:
		'''
			
			Purpose:
			--------
			Convert HTML to compact plain text with minimal heuristics (scripts and
			styles removed, tags replaced with whitespace, whitespace normalized).
			
			Parameters:
			---------
			html (str): Raw HTML string.
			show_dialog (bool): If True, show an ErrorDialog on exception.
			
			Returns:
			--------
			str: Plain text extracted from HTML.
			
		'''
		try:
			throw_if( 'html', html )
			html = re.sub( r'<script[\s\S]*?</script>', ' ', html, flags = re.IGNORECASE )
			html = re.sub( r'<style[\s\S]*?</style>', ' ', html, flags = re.IGNORECASE )
			html = re.sub( r'</?(p|div|br|li|h[1-6])[^>]*>', '\n', html, flags = re.IGNORECASE )
			text = re.sub( self.re_tag, ' ', html )
			text = re.sub( self.re_ws, ' ', text ).strip( )
			return text
		except Exception as exc:  
			exception = Error( exc )
			exception.module = 'fetchers'
			exception.cause = 'scrapers'
			exception.method = 'html_to_text( )'
			dialog = ErrorDialog( exception )
			dialog.show( )

class WebCrawler( WebFetcher ):
	'''
		
		Purpose:
		-------
		A crawler that attempts `crawl4ai` first (if installed) and falls back to
		Playwright headful rendering only when required. Designed to be used when
		pages require JS to render content.
			
		Parameters:
		----------
		headers (Optional[Dict[str, str]]): Optional headers for requests/playwright.
			
		Returns:
		-------
		None
		
	'''
	use_playwright: bool
	_browser_context: Optional[ Any ]

	def __init__( self, headers: Optional[ Dict[ str, str ] ]=None,
	              use_playwright: bool=False ) -> None:
		'''
		
			Purpose:
			-------
			Initialize crawler. By default prefer `crawl4ai` when available and
			only enable Playwright when `use_playwright=True`.
				
			Parameters:
			-----------
			headers (Optional[Dict[str, str]]): Optional headers.
			use_playwright (bool): If True, enable Playwright fallback.
				
			Returns:
			--------
			None
			
		'''
		super( ).__init__( headers = headers )
		self.use_playwright = bool( use_playwright )
		self._browser_context = None

	def __dir__( self ) -> list[ str ]:
		'''
		
			Purpose:
			-----------
			Ordering for WebCrawler introspection.
			
			Parameters:
			-----------
			None
			
			Returns:
			-----------
			list[str]: Ordered attribute/method names.
			
		'''
		return [ 'use_playwright', '_browser_context', 'fetch', 'html_to_text',
		         'render_with_playwright' ]

	def fetch( self, url: str, time: int=15 ) -> Result | None:
		'''
			
			Purpose:
			-------
			Try `crawl4ai` (if installed) to fetch JS-rendered content. If not
			available or it returns empty, fall back to the synchronous fetch or
			(optionally) to Playwright rendering.
				
			Parameters:
			-------
			url (str): Absolute URL to fetch.
			time (int): Timeout seconds.
			show_dialog (bool): If True, show an ErrorDialog on exception.
				
			Returns:
			-------
			Optional[Result]: Result with url, status, text, html, headers on success.
				
		'''
		try:
			throw_if( 'url', url )
			if crawl4ai is not None:
				try:
					cfg = { 'url': url }
					payload = crawl4ai.fetch_and_render( cfg )
					if payload and isinstance( payload, dict ) and 'content' in payload:
						html = payload.get( 'content', '' )
						text = self.html_to_text( html )
						result = Result( url = url, status=200, text=text, html=html,
							headers = { } )
						self.result = result
						return result
				except Exception:
					pass

			try:
				return super( ).fetch( url, time = time )
			except Exception:
				pass

			if self.use_playwright:
				try:
					html = self.render_with_playwright( url, timeout=time )
					text = self.html_to_text( html )
					result = Result( url=url, status=200, text=text, html=html, headers = { } )
					self.result = result
					return result
				except Exception: 
					pass
 
			raise RuntimeError( f'Failed to fetch URL via crawl4ai/requests/playwright: {url}' )
		except Exception as exc:
			exception = Error( exc )
			exception.module = 'scrapers'
			exception.cause = 'WebCrawler'
			exception.method = 'fetch( self, url: str, time: int=15 ) -> Result'
			dialog = ErrorDialog( exception )
			dialog.show( )

	def render_with_playwright( self, url: str, timeout: int=15 ) -> str:
		'''
		
			Purpose:
			-----------
			Render the page with Playwright (synchronous API) and return the page HTML.
			This method imports Playwright lazily so the package is optional.
			
			Parameters:
			-----------
			url (str): URL to render.
			timeout (int): Timeout seconds for render.
			
			Returns:
			-----------
			str: Rendered HTML of the page.
			
		'''
		try:
			with sync_playwright( ) as p:
				browser = p.chromium.launch( )
				page = browser.new_page( )
				page.goto( url, timeout = timeout * 1000 )
				page.wait_for_load_state( 'networkidle', timeout = timeout * 1000 )
				html = page.content( )
				browser.close( )
				return html
		except Exception as exc: 
			exception = Error( exc )
			exception.module = 'scrapers'
			exception.cause = 'WebCrawler'
			exception.method = 'render_with_playwright'
			dialog = ErrorDialog( exception )
			dialog.show( )