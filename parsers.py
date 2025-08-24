'''
  ******************************************************************************************
      Assembly:                Soupy
      Filename:                parsers.py
      Author:                  Terry D. Eppler
      Created:                 05-31-2022

      Last Modified By:        Terry D. Eppler
      Last Modified On:        05-01-2025
  ******************************************************************************************
  <copyright file="parsers.py" company="Terry D. Eppler">

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
    parsers.py
  </summary>
  ******************************************************************************************
'''
from bs4 import BeautifulSoup
from typing import Optional

class Parser( ):
	"""

		Purpose:
			Responsible for parsing raw HTML content into clean, readable text.

		Methods:
			parse(html: str) -> Optional[str]:
				Extracts and returns visible text content from HTML.

	"""
	def parse( self, html: str ) -> Optional[ str ]:
		"""

			Purpose:
				Convert raw HTML into clean text.

			Parameters:
				html (str): Raw HTML content.

			Returns:
				Optional[str]: Extracted readable text, or None if parsing fails.

		"""
		try:
			soup = BeautifulSoup( html, 'html.parser' )
			for tag in soup( [ 'script', 'style', 'noscript' ] ):
				tag.extract( )
			text = soup.get_text( separator = '\n' )
			clean_text = '\n'.join( line.strip( ) for line in text.splitlines( ) if line.strip( ) )
			return clean_text if clean_text else None
		except Exception:
			return None

class HTMLTextParser( Parser ):
	""""""
	_strip_scripts: bool
	_collapse_whitespace: bool

	def __init__( self, strip_scripts: bool=True, collapse_whitespace: bool=True ) -> None:
		"""
		
			Purpose
			Initialize an HTMLTextParser with basic cleaning controls.
	
	
			Parameters
			strip_scripts: bool
			If True, drop <script> and <style> prior to extraction.
			collapse_whitespace: bool
			If True, collapse repeated whitespace in extracted text.
	
	
			Returns
			None
			
		"""
		self._strip_scripts = strip_scripts
		self._collapse_whitespace = collapse_whitespace

	def to_text( self, html: str ) -> str | None:
		"""
			Purpose
			Extract human‑readable text from HTML.


			Parameters
			html: str
			The HTML source to parse. Must not be None.


			Returns
			str
			Cleaned, readable text suitable for markdown export.
		"""
		if html is None:
			raise ValueError( 'html must not be None' )
		try:
			soup = BeautifulSoup( html, 'lxml' )
			if self._strip_scripts:
				for tag in soup( [ 'script', 'style', 'noscript' ] ):
					tag.decompose( )
			_text = soup.get_text( '\n', strip = True )
			if self._collapse_whitespace:
				# Normalize common whitespace patterns without losing paragraph breaks entirely.
				lines = [ ln.strip( ) for ln in _text.splitlines( ) ]
				lines = [ ln for ln in lines if ln ]  # drop empty lines
				_text = '\n\n'.join( lines )
				return _text
		except Exception as exc:
			raise Exception( f'Failed to parse HTML: {exc}' )
