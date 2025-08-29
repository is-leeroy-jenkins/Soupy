'''
******************************************************************************************
  Assembly:                Soupy
  Filename:                converters.py
  Author:                  Terry D. Eppler (adapted by Bro)
  Created:                 05-31-2022
  Last Modified By:        Terry D. Eppler
  Last Modified On:        08-25-2025
******************************************************************************************
<copyright file="converters.py" company="Terry D. Eppler">

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
    converters.py — improved, more robust converters with clearer errors and typing
</summary>
******************************************************************************************
'''
from __future__ import annotations

from typing import Optional, List

from boogr import Error, ErrorDialog
from bs4 import BeautifulSoup

try:
	import html2text

	_HAS_HTML2TEXT = True
except Exception:
	_HAS_HTML2TEXT = False

def throw_if( name: str, value: object ) -> None:
	"""

	Purpose:
	--------
	Lightweight guard used across the soupy codebase to validate required
	arguments. Treats None and empty/whitespace-only strings as invalid.

	Parameters:
	----------
	name (str): Human-friendly name of the argument used in the raised
		ValueError message.
	value (object): The value to validate. If None or an empty/whitespace
		string, a ValueError is raised.

	Returns:
	-------
	None

	"""
	if value is None:
		raise ValueError( f'Argument "{name}" cannot be None!' )
	if isinstance( value, str ) and not value.strip( ):
		raise ValueError( f'Argument "{name}" cannot be empty or whitespace!' )

class MarkdownConverter:
	"""

	Purpose:
	--------
	Abstract base for HTML -> Markdown conversion strategies. Subclasses must
	implement ``convert(html: str) -> Optional[str]``.

	Contract:
	---------
	convert(html: str) -> Optional[str]

	"""

	raw_html: Optional[ str ] = None
	parsed_text: Optional[ str ] = None

	def convert( self, html: str ) -> Optional[ str ]:
		"""

		Purpose:
		--------
		Convert an HTML fragment or document to Markdown.

		Parameters:
		----------
		html (str): HTML source to convert.

		Returns:
		-------
		Optional[str]: Markdown string when conversion succeeds, otherwise None.

		"""
		raise NotImplementedError( "Subclasses must implement convert()" )

	def __dir__( self ) -> List[ str ]:
		"""
		Purpose:
		--------
		Provide a compact, stable list of attributes for GUI inspection and
		tooling.

		Returns:
		-------
		List[str]
		"""
		return [ "raw_html", "parsed_text", "convert" ]

class Html2TextConverter( MarkdownConverter ):
	"""

	Purpose:
	--------
	Use the html2text library for high-fidelity conversion when available.

	Notes:
	-----
	If html2text is not installed, conversion raises a RuntimeError.

	"""

	def __init__( self ) -> None:
		super( ).__init__( )

	def __dir__( self ) -> List[ str ]:
		return [ "raw_html", "parsed_text", "convert" ]

	def convert( self, html: str ) -> Optional[ str ]:
		"""

		Purpose:
		--------
		Convert HTML to Markdown using html2text.HTML2Text with sane defaults
		that preserve structure (disable body-width wrapping by default).

		Parameters:
		----------
		html (str): HTML fragment or full document.

		Returns:
		-------
		Optional[str]: Markdown representation when successful.

		Raises:
		------
		RuntimeError: If html2text is not available.

		"""
		try:
			throw_if( "html", html )
			if not _HAS_HTML2TEXT:
				raise RuntimeError( "html2text is not installed; cannot convert" )

			self.raw_html = html
			h = html2text.HTML2Text( )
			# sensible defaults — preserve paragraphs, do not hard-wrap lines
			h.bodywidth = 0
			h.ignore_images = True
			h.ignore_links = False
			h.protect_links = True

			md = h.handle( self.raw_html )
			self.parsed_text = md.strip( ) if md is not None else None
			return self.parsed_text
		except Exception as e:
			exception = Error( e )
			exception.module = "soupy"
			exception.cause = "Html2TextConverter"
			exception.method = "convert(self, html: str) -> Optional[str]"
			error = ErrorDialog( exception )
			error.show( )
			return None

class SoupFallbackConverter( MarkdownConverter ):
	"""

	Purpose:
	--------
	Simple, dependency-light fallback that preserves headings, paragraphs,
	lists, and blockquotes from a parsed DOM. Intended as a last-resort
	converter when richer libraries are unavailable or fail.

	"""

	soup: Optional[ BeautifulSoup ]
	blocks: List[ str ]

	def __init__( self ) -> None:
		super( ).__init__( )
		self.blocks = [ ]
		self.soup = None

	def __dir__( self ) -> List[ str ]:
		return [ "soup", "blocks", "strip_noise", "convert" ]

	def strip_noise( self, soup: BeautifulSoup ) -> None:
		"""

		Purpose:
		--------
		Remove non-content tags from the parsed DOM (scripts, styles, iframes,
		svgs, forms, etc.) to reduce noise prior to text extraction.

		Parameters:
		----------
		soup (BeautifulSoup): Parsed DOM.

		Returns:
		-------
		None

		"""
		try:
			throw_if( "soup", soup )
			self.soup = soup
			for tag in self.soup(
					[ "script", "style", "noscript", "svg", "canvas", "iframe", "form" ] ):
				tag.decompose( )
		except Exception as e:
			exception = Error( e )
			exception.module = "soupy"
			exception.cause = "SoupFallbackConverter"
			exception.method = "strip_noise(self, soup: BeautifulSoup) -> None"
			error = ErrorDialog( exception )
			error.show( )

	def convert( self, html: str ) -> Optional[ str ]:
		"""

		Purpose:
		--------
		Convert an HTML fragment to a simple, readable Markdown-like text by
		preserving block structure (headers, lists, blockquotes, code blocks).

		Parameters:
		----------
		html (str): HTML fragment or full document.

		Returns:
		-------
		Optional[str]: Markdown-like string when successful, otherwise None.

		"""
		try:
			throw_if( "html", html )
			self.raw_html = html
			self.soup = BeautifulSoup( self.raw_html, "html.parser" )

			# clear any previous run state
			self.blocks = [ ]

			# remove noisy tags first
			self.strip_noise( self.soup )

			# prefer body if present, otherwise fall back to entire document
			body = self.soup.body or self.soup

			for el in body.find_all(
					[ "h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "blockquote", "pre",
					  "code" ] ):
				txt = el.get_text( " ", strip = True )
				if not txt:
					continue

				tag_name = el.name.lower( )
				if tag_name.startswith( "h" ):
					# header level detection with safety
					level = 2
					if len( tag_name ) > 1 and tag_name[ 1: ].isdigit( ):
						try:
							level = int( tag_name[ 1: ] )
						except Exception:
							level = 2
					self.blocks.append( f"{"#" * level} {txt}" )
				elif tag_name == "li":
					self.blocks.append( f"- {txt}" )
				elif tag_name == "blockquote":
					self.blocks.append( "\n".join(
						[ f"> {line}" for line in txt.splitlines( ) if line.strip( ) ] ) )
				else:
					self.blocks.append( txt )

			if not self.blocks:
				# if nothing significant found, return cleaned text of body
				fallback = body.get_text( "\n", strip = True )
				self.parsed_text = fallback
				return self.parsed_text

			self.parsed_text = "\n\n".join( self.blocks )
			return self.parsed_text
		except Exception as e:
			exception = Error( e )
			exception.module = "soupy"
			exception.cause = "SoupFallbackConverter"
			exception.method = "convert(self, html: str) -> Optional[str]"
			error = ErrorDialog( exception )
			error.show( )
			return None

class CompositeMarkdownConverter( MarkdownConverter ):
	"""

	Purpose:
	--------
	Try multiple Markdown converters in order until one succeeds. Collects
	individual converter errors to provide a useful diagnostic when all fail.

	Parameters:
	----------
	converters (list[MarkdownConverter]): Ordered list of converter strategies.

	"""

	converters: Optional[ List[ MarkdownConverter ] ] = None
	errors: Optional[ List[ str ] ] = None

	def __init__( self, converters: List[ MarkdownConverter ] ) -> None:
		super( ).__init__( )
		self.converters = converters[ : ] if converters is not None else [ ]
		self.errors = [ ]

	def __dir__( self ) -> List[ str ]:
		return [ "converters", "errors", "raw_html", "parsed_text", "convert" ]

	def convert( self, html: str ) -> Optional[ str ]:
		"""

		Purpose:
		--------
		Apply each converter in order until one returns Markdown successfully.

		Parameters:
		----------
		html (str): HTML input.

		Returns:
		-------
		Optional[str]: Markdown output when a converter succeeds, otherwise None.

		Raises:
		------
		RuntimeError: If all converters fail (after collecting their error
			messages).

		"""
		try:
			throw_if( "html", html )

			self.raw_html = html
			self.errors = [ ]

			for c in self.converters:
				try:
					md = c.convert( html )
					if md:
						self.parsed_text = md
						return md
				except Exception as e:
					# collect the error but continue trying
					self.errors.append( f"{c.__class__.__name__}: {e}" )

			# none succeeded
			msg = "All Markdown converters failed:\n- " + "\n- ".join(
				self.errors or [ "<no errors captured>" ] )
			raise RuntimeError( msg )
		except Exception as e:
			exception = Error( e )
			exception.module = ""
			exception.cause = ""
			exception.method = ""
			error = ErrorDialog( exception )
			error.show( )
