'''
  ******************************************************************************************
      Assembly:                Soupy
      Filename:                extractors.py
      Author:                  Terry D. Eppler
      Created:                 05-31-2022

      Last Modified By:        Terry D. Eppler
      Last Modified On:        05-01-2025
  ******************************************************************************************
  <copyright file="extractors.py" company="Terry D. Eppler">

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
    extractors.py
  </summary>
  ******************************************************************************************
'''
from typing import Optional, List
from bs4 import BeautifulSoup
from boogr import Error, ErrorDialog

def throw_if( name: str, value: object ):
	if not value:
		raise ValueError( f'Argument "{name}" cannot be empty!' )

class Extractor( ):
	"""

		Purpose:
			Abstract base for HTML → plain-text extraction.

	"""
	raw_html: Optional[ str ]
	extracted_text: Optional[ str ]
	
	def __init__( self ):
		self.raw_html = None
		self.extracted_text = None

	def __dir__( self ) -> List[ str ]:
		"""Provide a stable ordering for tooling and REPL use."""
		return [ 'raw_html', 'extract' ]

	def extract( self, html: str ) -> str:
		raise NotImplementedError( "NOT IMPLEMENTED!" )

class ParagraphExtractor( Extractor ):
	"""

		Strategy:
		Pulls all <p> tags and joins their text.

	"""
	def __init__( self ):
		super( ).__init__( )

	def __dir__( self ) -> List[ str ]:
		return [ 'raw_html', 'extract' ]

	def extract( self, html: str ) -> str | None:
		try:
			throw_if( 'html', html )
			soup = BeautifulSoup( html, 'html.parser' )
			paragraphs = [ p.get_text( separator=' ', strip=True ) for p in  soup.find_all( 'p' ) ]
			return ''.join( x for x in paragraphs if x )
		except Exception as e:
			exception = Error( e )
			exception.module = 'soupy'
			exception.cause = 'HeuristicExtractor'
			exception.method = 'extract( self, html: str ) -> str'
			error = ErrorDialog( exception )
			error.show( )

class ArticleExtractor( Extractor ):
	"""

		Strategy:
		Tries to grab the <article> element text; falls back to full document text.

	"""

	def __init__( self ):
		super( ).__init__( )

	def __dir__( self ) -> List[ str ]:
		return [ 'raw_html', 'extract' ]

	def extract( self, html: str ) -> str | None:
		"""
		
			Extracts text from the input html
			
		"""
		try:
			throw_if( 'html', html )
			soup = BeautifulSoup( html, 'html.parser' )
			article = soup.find( 'article' )
			if article is not None:
				self.extracted_text = article.get_text( separator=' ', strip=True )
			else:
				self.extracted_text = soup.get_text( ' ', strip=True )
			return self.extracted_text
		except Exception as e:
			exception = Error( e )
			exception.module = 'soupy'
			exception.cause = 'ReadabilityExtractor'
			exception.method = 'extract( self, html: str ) -> str'
			error = ErrorDialog( exception )
			error.show( )
