'''
  ******************************************************************************************
      Assembly:                Soupy
      Filename:                fetchers.py
      Author:                  Terry D. Eppler
      Created:                 05-31-2022

      Last Modified By:        Terry D. Eppler
      Last Modified On:        05-01-2025
  ******************************************************************************************
  <copyright file="fetchers.py" company="Terry D. Eppler">

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
import requests
from typing import Optional, Tuple, Mapping, Pattern, Dict
from oauthlib.common import CaseInsensitiveDict
from requests import Response
from .core import Result
import re
import crawl4ai
from playwright.sync_api import sync_playwright, Page, BrowserContext
from boogr import Error, ErrorDialog

def throw_if( name: str, value: object ):
	if not value:
		raise ValueError( f'Argument "{name}" cannot be empty!' )


class Fetcher:
	"""

		Purpose:
			Responsible for retrieving raw HTML content from a given URL using HTTP(S) requests.

		Methods:
			fetch(url: str, render_timeout: int = 10) -> Optional[str]:
				Makes an HTTP GET request to the provided URL and returns HTML text if successful.

	"""
	timeout: Optional[ int ]
	headers: Optional[ Dict[ str, str ] ]
	response: Optional[ Response ]
	url: Optional[ str ]

	def __init__( self ):
		self.headers = { 'User-Agent': 'Soupy 1.0' }

	def fetch( self, url: str, timeout: int=10 ) -> Optional[ str ]:
		"""

			Purpose:
				Fetch raw HTML from a URL.

			Parameters:
				url (str): Target website URL.
				timeout (int): Timeout in seconds for the HTTP request.

			Returns:
				Optional[str]: HTML content if the request succeeds, otherwise None.

		"""
		try:
			throw_if( 'url', url )
			self.url = url
			self.timeout = timeout
			response = requests.get( url, timeout = timeout,
				headers = { 'User-Agent': 'Soupy 1.0' } )
			response.raise_for_status( )
			return response.text
		except Exception as e:
			exception = Error( e )
			exception.module = ''
			exception.cause = ''
			exception.method = ''
			error = ErrorDialog( exception )
			error.show( )

# noinspection PyTypeChecker
class WebFetcher( Fetcher ):
	"""

		Purpose:
			Concrete synchronous fetcher using `requests` with naive HTML→text extraction.

		Parameters:
			headers (Mapping[str, str]): Optional HTTP headers (User-Agent auto-filled if missing).

		Returns:
			None

	"""
	agents: Optional[ str ]
	raw_url: Optional[ str ]
	raw_html: Optional[ str ]
	re_tag: Optional[ Pattern ]
	re_ws: Optional[ Pattern ]

	def __init__( self, headers: Mapping[ str, str ]=None ) -> None:
		"""

			Purpose:
				Initialize WebFetcher with optional headers and defaults.

			Parameters:
				headers (Mapping[str, str] | None): Optional headers to include in requests.

			Returns:
				None

		"""
		super( ).__init__( )
		self.timeout = 15
		self.re_tag = re.compile( r'<[^>]+>' )
		self.re_ws = re.compile( r'\s+' )
		if headers is None:
			self.headers = { }
		else:
			self.headers = dict( headers )
		self.agents = (
				'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
				'AppleWebKit/537.36 (KHTML, like Gecko) '
				'Chrome/124.0 Safari/537.36' )

		if 'User-Agent' not in self.headers:
			self.headers[ 'User-Agent' ] = self.agents

	def fetch( self, url: str, time: int=10 ) -> Result | None:
		"""

			Purpose:
				Perform an HTTP GET to fetch a page and return extracted text and HTML.

			Parameters:
				url (str): Absolute URL to fetch.
				time (str) : time

			Returns:
				Result: Result containing canonical URL, status, text, HTML, and headers.

		"""
		try:
			throw_if( 'url', url )
			self.raw_url = url
			resp = requests.get( url=self.raw_url, headers=self.headers, timeout=time )
			resp.raise_for_status( )
			html = resp.text
			text = self._html_to_text( html )
			result = Result( url = resp.url or url, status = resp.status_code, text = text,
				html = html, headers = resp.headers )
			return result
		except Exception as e:
			exception = Error( e )
			exception.module = ''
			exception.cause = ''
			exception.method = ''
			error = ErrorDialog( exception )
			error.show( )

	def _html_to_text( self, html: str ) -> str:
		"""

			Purpose:
				Convert HTML to compact plain text with minimal heuristics.

			Parameters:
				html (str): Raw HTML.

			Returns:
				str: Plain text content.

		"""
		throw_if( 'html', html )
		if html is None:
			raise ValueError( 'html cannot be None' )
		# Remove scripts and styles
		html = re.sub( r'<script[\s\S]*?</script>', ' ', html, flags = re.IGNORECASE )
		html = re.sub( r'<style[\s\S]*?</style>', ' ', html, flags = re.IGNORECASE )
		# Convert some tags to newlines
		html = re.sub( r'<(?:br|/p)\b[^>]*>', '\n', html, flags = re.IGNORECASE )
		# Strip remaining tags
		text = self.re_tag.sub( ' ', html )
		# Collapse whitespace
		text = self.re_ws.sub( ' ', text )
		# Normalize newlines
		text = re.sub( r'\s*\n\s*', '\n', text )
		return text.strip( )


class WebCrawler( Fetcher ):
	"""

			Purpose:
				Render and fetch a single URL using a headless browser stack.

			Parameters:
				user_agent (Optional[str]): Optional UA string to use for the browser context.

			Returns:
				None

	"""
	render_timeout: float
	navigation_timeout: float
	user_agent: Optional[ str ]
	raw_html: Optional[ str ]
	parsed_text: Optional[ str ]
	url: Optional[ str ]
	page: Optional[ Page ]
	context: Optional[ BrowserContext ]
	output: Optional[ str ]

	def __init__( self, user_agent: Optional[ str ]=None ) -> None:
		"""

			Purpose:
				Initialize the WebCrawler with optional user-agent overrides.

			Parameters:
				user_agent (Optional[str]): Browser user-agent string.

			Returns:
				None

		"""
		super( ).__init__( )
		self.user_agent = user_agent
		self.navigation_timeout = 30000.0
		self.render_timeout = 30.0

	def fetch( self, url: str, timeout: int=10 ) -> Result | None:
		"""

			Purpose:
				Fetch and render a single URL into text + HTML.
				Prefers `crawl4ai`, falls back to Playwright.

			Parameters:
				url (str): Absolute URL to fetch.
				timeout (str) : time

			Returns:
				Result: Result with extracted text and HTML.

		"""
		try:
			throw_if( 'url', url )
			self.url = url
			output = crawl4ai.crawl_url( url=self.url, timeout=self.render_timeout,
				user_agent=self.user_agent, browser='chrome' )
			self.raw_html = output.html
			self.parsed_text = output.text
			status = int( getattr( output, 'status', 200 ) )
			return Result( url=url, status=status, text=self.parsed_text, html=self.raw_html )
		except Exception as e:
			exception = Error( e )
			exception.module = ''
			exception.cause = ''
			exception.method = ''
			error = ErrorDialog( exception )
			error.show( )

		with sync_playwright( ) as p:
			browser = p.chromium.launch( channel='chrome', headless=True )
			try:
				context = browser.new_context( user_agent=self.user_agent )
				page = context.new_page( )
				page.set_default_navigation_timeout( self.navigation_timeout )
				page.goto( url, wait_until='networkidle' )
				page.wait_for_load_state( 'domcontentloaded' )
				html = page.content( )
				text = _sanitize_html_to_text( html )
				status = 200
				return Result( url=url, status=status, text=text, html=html )
			finally:
				browser.close( )


def _sanitize_html_to_text( html: str ) -> str:
	"""

		Purpose:
			Minimal HTML to text sanitizer used by the crawler path.

		Parameters:
			html (str): Raw HTML.

		Returns:
			str: Plain text content.

	"""
	if html is None:
		raise ValueError( 'html cannot be None' )
	import re as _re
	throw_if( 'html', html )
	html = _re.sub( r'<script[\s\S]*?</script>', ' ', html, flags = _re.IGNORECASE )
	html = _re.sub( r'<style[\s\S]*?</style>', ' ', html, flags = _re.IGNORECASE )
	html = _re.sub( r'<(?:br|/p)\b[^>]*>', '\n', html, flags = _re.IGNORECASE )
	text = _re.sub( r'<[^>]+>', ' ', html )
	text = _re.sub( r'\s+', ' ', text )
	text = _re.sub( r'\s*\n\s*', '\n', text )
	return text.strip( )