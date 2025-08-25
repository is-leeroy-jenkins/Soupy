'''
  ******************************************************************************************
      Assembly:                Soupy
      Filename:                converters.py
      Author:                  Terry D. Eppler
      Created:                 05-31-2022

      Last Modified By:        Terry D. Eppler
      Last Modified On:        05-01-2025
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
    converters.py
  </summary>
  ******************************************************************************************
'''
from typing import Optional, List
from boogr import Error, ErrorDialog
from bs4 import BeautifulSoup
try:
	import html2text
	_HAS_HTML2TEXT = True
except Exception:
	_HAS_HTML2TEXT = False


def throw_if( name: str, value: object ):
	if not value:
		raise ValueError( f'Argument "{name}" cannot be empty!' )


class MarkdownConverter:
	"""
	
		Purpose:
		Abstract base for HTML → Markdown conversion.
	
	
		Contract:
		convert(html: str) -> str
		
	"""
	raw_html: Optional[ str ]
	parsed_text: Optional[ str ]

	def convert( self, html: str ) -> str | None:
		raise NotImplementedError( 'NOT IMPLEMENTED!' )


class Html2TextConverter( MarkdownConverter ):
	"""
	
		Purpose:
			Use the 'html2text' library for high-fidelity conversion when available.
	
		Notes:
			If html2text isn't installed, this converter raises RuntimeError.
			
	"""

	def __init__( self ) -> None:
		super( ).__init__( )

	def convert( self, html: str ) -> str | None:
		"""
		
			Purpose:
				Convert HTML to Markdown using html2text.
	
			Parameters:
				html (str):
					HTML fragment or full document.
	
			Returns:
				str:
					Markdown representation.
	
			Raises:
				RuntimeError:
					If html2text is unavailable.
					
		"""
		try:
			if not _HAS_HTML2TEXT:
				raise RuntimeError( 'html2text not installed.' )

			self.raw_html = html
			h = html2text.HTML2Text( )
			h.body_width = 0
			h.ignore_links = False
			h.ignore_images = True
			h.skip_internal_links = False
			h.protect_links = True
			self.parsed_text = h.handle( self.raw_html ).strip( )
			return self.parsed_text
		except Exception as e:
			exception = Error( e )
			exception.module = ''
			exception.cause = ''
			exception.method = ''
			error = ErrorDialog( exception )
			error.show( )


class SoupFallbackConverter( MarkdownConverter ):
	"""
		
		Purpose:
			Simple, dependency-light fallback that preserves headings, paragraphs,
			lists, and blockquotes from a parsed DOM.
		
	"""
	soup: Optional[ BeautifulSoup ]
	blocks: Optional[ List[ str ] ]


	def __init__( self ):
		super( ).__init__( )
		self.blocks = [ ]

	def __dir__( self ):
		return [ 'soup', 'blocks', 'strip_noise', 'convert' ]

	def strip_noise( self, soup: BeautifulSoup ) -> None:
		try:
			throw_if( 'soup', soup )
			self.soup = soup
			for tag in self.soup( [ 'script', 'style', 'noscript', 'svg', 'canvas', 'iframe', 'form' ] ):
				tag.decompose( )
		except Exception as e:
			exception = Error( e )
			exception.module = 'soupy'
			exception.cause = 'SoupFallbackConverter'
			exception.method = 'strip_noise( self, soup: BeautifulSoup ) -> None'
			error = ErrorDialog( exception )
			error.show( )


	def convert( self, html: str ) -> str | None:
		"""
		
			Purpose:
				Convert HTML to a basic Markdown string.
	
			Parameters:
				html (str):
					HTML fragment or full document.
	
			Returns:
				str:
					Markdown (simple).
					
		"""
		try:
			throw_if( 'html', html )
			self.raw_html = html
			self.soup = BeautifulSoup( self.raw_html, 'html.parser' )
			self.strip_noise( self.soup )
			body = self.soup.body
			for el in body.find_all( [ 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li',
			                           'blockquote', 'pre', 'code' ] ):
				txt = el.get_text( ' ', strip=True )
				if not txt:
					continue
				name = el.lower( )
				if name.startswith( 'h' ):
					level = int( name[ 1 ] ) if name[ 1: ].isdigit( ) else 2
					self.blocks.append( f'{'#' * level} {txt}' )
				elif name == 'li':
					self.blocks.append( f'- {txt}' )
				elif name == 'blockquote':
					self.blocks.append(
						'\n'.join( [ f'> {line}' for line in txt.splitlines( ) if line.strip( ) ] ) )
				else:
					self.blocks.append( txt )
			if not self.blocks:
				return body.get_text( '\n', strip=True )
			self.parsed_text = '\n\n'.join( self.blocks )
			return self.parsed_text
		except Exception as e:
			exception = Error( e )
			exception.module = 'soupy'
			exception.cause = 'SoupFallbackConverter'
			exception.method = 'convert( self, html: str ) -> str'
			error = ErrorDialog( exception )
			error.show( )


class CompositeMarkdownConverter( MarkdownConverter ):
	"""

		Purpose:
			Try multiple Markdown converters in order until one succeeds.

		Parameters:
			converters (list[MarkdownConverter]):
				Ordered list of converter strategies.

	"""
	converters: Optional[ List[ MarkdownConverter ] ]
	errors: Optional[ List[ str ] ]

	def __init__( self, converters: list[ MarkdownConverter ] ) -> None:
		super( ).__init__( )
		self.converters = converters[ : ]
		self.errors = [ ]

	def convert( self, html: str ) -> str | None:
		"""

			Purpose:
				Apply each converter in order until one returns Markdown successfully.

			Parameters:
				html (str):
					HTML input.

			Returns:
				str:
					Markdown output.

			Raises:
				RuntimeError:
					If all converters fail.

		"""
		try:
			for c in self.converters:
				try:
					return c.convert( html )
				except Exception as e:
					self.errors.append( f'{c.__class__.__name__}: {e}' )
			msg = 'All Markdown converters failed:\n- ' + '\n- '.join( self.errors )
			raise RuntimeError( msg )
		except Exception as e:
			exception = Error( e )
			exception.module = 'soupy'
			exception.cause = 'SoupFallbackConverter'
			exception.method = 'convert( self, html: str ) -> str'
			error = ErrorDialog( exception )
			error.show( )

