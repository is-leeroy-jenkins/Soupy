from typing import Optional, List
from boogr import Error, ErrorDialog
from bs4 import BeautifulSoup
import html2text

_HAS_HTML2TEXT = True

def throw_if( name: str, value: object ):
	if value is None:
		raise ValueError( f'Argument "{name}" cannot be empty!' )

class MarkdownConverter:
	"""

		Purpose:
		-----------
		Base class for HTML → Markdown conversion.
		
		Contract:
		-----------
		convert(html: str) -> str

	"""
	raw_html: Optional[ str ] = None
	parsed_text: Optional[ str ] = None

	def __dir__( self ) -> List[ str ]:
		"""
		
		Returns:
		-----------
		List[str]: attribute names followed by public methods.
		
		"""
		return [ 'raw_html', 'parsed_text', 'convert' ]

	def convert( self, html: str ) -> str | None:
		raise NotImplementedError( 'NOT IMPLEMENTED!' )

class Html2TextConverter( MarkdownConverter ):
	"""

		Purpose:
		-----------
		Uses the 'html2text' library for high-fidelity conversion when available.

	"""
	_has_html2text: Optional[ bool ]

	def __init__( self ) -> None:
		super( ).__init__( )
		self.raw_html = None
		self.parsed_text = None

	def __dir__( self ) -> List[ str ]:
		"""
		
			Purpose:
			-----------
			Provide ordering for Html2TextConverter's attributes and methods.
			
			Returns:
			-----------
			List[str]: attribute names followed by public methods.
			
		"""
		return [ 'raw_html', 'parsed_text', 'convert' ]


	def convert( self, html: str ) -> str | None:
		"""

			Purpose:
			-----------
			Convert HTML to Markdown using html2text.

			Parameters:
			-----------
			html (str): HTML fragment or full document.

			Returns:
			-----------
			str: Markdown representation.


		"""
		try:
			throw_if( 'htmel', html )
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
			exception.module = 'parsers'
			exception.cause = 'Html2TextConverter'
			exception.method = 'convert( self, html: str ) -> str'
			error = ErrorDialog( exception )
			error.show( )


class SoupFallbackConverter( MarkdownConverter ):
	"""

		Purpose:
		-----------
		Simple, dependency-light fallback that preserves headings, paragraphs,
		lists, and blockquotes from a parsed DOM.

	"""
	soup: Optional[ BeautifulSoup ]
	blocks: Optional[ List[ str ] ]
	raw_html: Optional[ str ]
	parsed_text: Optional[ str ]

	def __init__( self ):
		super( ).__init__( )
		self.blocks = [ ]
		self.raw_html = None
		self.parsed_text = None

	def __dir__( self ) -> List[ str ]:
		"""
			
			Returns:
			-----------
			List[str]: attribute names followed by public methods.
			
		"""
		return [ 'soup', 'blocks', 'raw_html', 'parsed_text', 'strip_noise', 'convert' ]

	def strip_noise( self, soup: BeautifulSoup ) -> None:
		try:
			throw_if( 'soup', soup )
			self.soup = soup
			for tag in self.soup(
					[ 'script', 'style', 'noscript', 'svg', 'canvas', 'iframe', 'form' ] ):
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
			-----------
			Convert HTML to a basic Markdown string.

			Parameters:
			-----------
			html (str): HTML fragment or full document.

			Returns:
			-----------
			str: Markdown (simple).

		"""
		try:
			throw_if( 'html', html )
			self.raw_html = html
			self.soup = BeautifulSoup( self.raw_html, 'html.parser' )
			self.strip_noise( self.soup )
			body = self.soup.body
			if body is None:
				return self.soup.get_text( '\n', strip = True )
			tags = [ 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li',
			                           'blockquote', 'pre', 'code' ]
			for el in body.find_all( tags ):
				txt = el.get_text( ' ', strip = True )
				if not txt:
					continue
					
				name = el.name.lower( )
				if name.startswith( 'h' ):
					level = int( name[ 1 ] ) if name[ 1: ].isdigit( ) else 2
					self.blocks.append( f'{"#" * level} {txt}' )
				elif name == 'li':
					self.blocks.append( f'- {txt}' )
				elif name == 'blockquote':
					quote = [ f'> {line}' for line in txt.splitlines( ) if line.strip( ) ]
					self.blocks.append( '\n'.join( quote ) )
				else:
					self.blocks.append( txt )
			if not self.blocks:
				return body.get_text( '\n', strip = True )
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
		-----------
		Try multiple Markdown converters in order until one succeeds.

		Parameters:
		-----------
		converters (list[MarkdownConverter]): Ordered list of converter strategies.

	"""
	converters: Optional[ List[ MarkdownConverter ] ]
	errors: Optional[ List[ str ] ]
	raw_html: Optional[ str ]
	parsed_text: Optional[ str ]

	def __init__( self, converters: list[ MarkdownConverter ] ) -> None:
		super( ).__init__( )
		self.converters = converters[ : ]
		self.errors = [ ]
		self.raw_html = None
		self.parsed_text = None

	def __dir__( self ) -> List[ str ]:
		"""
		
			Purpose:
			-----------
			Provide a stable ordering for CompositeMarkdownConverter attributes/methods.
	
			Returns:
			-----------
			List[str]: attribute names followed by public methods.
			
		"""
		return [ 'converters', 'errors', 'raw_html', 'parsed_text', 'convert' ]

	def convert( self, html: str ) -> str | None:
		"""

			Purpose:
			-----------
			Apply each converter in order until one returns Markdown successfully.

			Parameters:
			-----------
			html (str): HTML input.

			Returns:
			-----------
			str: Markdown output.
 
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