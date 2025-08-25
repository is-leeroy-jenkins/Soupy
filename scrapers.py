'''
	******************************************************************************************
	  Assembly:                Soupy
	  Filename:                scrapers.py
	  Author:                  Terry D. Eppler
	  Created:                 05-31-2022

	  Last Modified By:        Terry D. Eppler
	  Last Modified On:        05-01-2025
	******************************************************************************************
		<copyright file="scrapers.py" company="Terry D. Eppler">

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
			scrapers.py
		</summary>
	******************************************************************************************
'''
from pathlib import Path
from typing import Optional
from .fetchers import Fetcher
from .parsers import Parser
from .writers import Writer
from boogr import Error, ErrorDialog

def throw_if( name: str, value: object ):
	if not value:
		raise ValueError( f'Argument "{name}" cannot be empty!' )

class Scraper:
	"""

		Purpose:
			Orchestrates the scraping process by combining fetch, parse, and write operations.

		Methods:
			scrape(url: str, file: str, dir: str = "output") -> Optional[str]:
				Executes the complete scrape and save workflow.

	"""
	fethcher: Optional[ Fetcher ]
	parser: Optional[ Parser ]
	writer: Optional[ Writer ]
	url: Optional[ str ]
	file_path: Optional[ Path ]
	raw_html: Optional[ str ]
	parsed_text: Optional[ str ]

	def __init__( self ) -> None:
		self.fetcher = Fetcher( )
		self.parser = Parser( )
		self.writer = Writer( )

	def scrape( self, url: str, file: str, dir: str= 'output' ) -> str | None:
		"""

			Purpose:
				Scrape a webpage and save the text content to a Markdown file.

			Parameters:
				url (str): Target website URL.
				file (str): Desired Markdown filename (without extension).
				dir (str): Directory to save the file into.

			Returns:
				Optional[str]: Path to the saved file if successful, otherwise None.

		"""
		try:
			try:
				throw_if( 'url', url )
				throw_if( 'file', file )
				self.raw_html = self.fetcher.fetch( url )
				if not self.raw_html:
					return None
				self.parsed_text = self.parser.parse( self.raw_html )
				if not self.parsed_text:
					return None
				self.file_path = self.writer.write( self.parsed_text, file, dir )
				return self.file_path
			except Exception as e:
				exception = Error( e )
				exception.module = 'soupy'
				exception.cause = 'Scraper'
				exception.method = 'scrape( self, url: str, file: str, dir: str=output ) -> str'
				error = ErrorDialog( exception )
				error.show( )

