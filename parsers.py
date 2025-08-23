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

class Parser:
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
			soup = BeautifulSoup( html, "html.parser" )

			# Remove unwanted elements
			for tag in soup( [ "script", "style", "noscript" ] ):
				tag.extract( )

			text = soup.get_text( separator="\n" )
			clean_text = "\n".join( line.strip( ) for line in text.splitlines( ) if line.strip( ) )
			return clean_text if clean_text else None
		except Exception:
			return None