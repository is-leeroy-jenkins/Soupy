'''
  ******************************************************************************************
      Assembly:                Soupy
      Filename:                httppy
      Author:                  Terry D. Eppler
      Created:                 05-31-2022

      Last Modified By:        Terry D. Eppler
      Last Modified On:        05-01-2025
  ******************************************************************************************
  <copyright file="http.py" company="Terry D. Eppler">

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
    http.py
  </summary>
  ******************************************************************************************
'''

from typing import Dict, Optional

class Result:
	"""
	Purpose:
		Immutable container for a single-page scrape outcome.

	Parameters:
		url (str): Canonical URL that was fetched.
		status_code (int): HTTP status if available; use 0 when not applicable.
		text (str): Extracted plain text content (may be empty).
		html (Optional[str]): Raw HTML used to derive `text`, if available.
		headers (Optional[Dict[str, str]]): Response headers, if available.

	Returns:
		None
	"""
	url: str
	status_code: int
	text: str
	html: Optional[ str ]
	headers: Dict[ str, str ]

	@property
	def has_html( self ) -> bool:
		"""
		Purpose:
			Indicate whether HTML is attached to the result.
		"""
		return isinstance( self.html, str ) and len( self.html ) > 0

	def __init__(
			self,
			url: str,
			status_code: int,
			text: str,
			html: Optional[ str ] = None,
			headers: Optional[ Dict[ str, str ] ] = None,
	) -> None:
		"""
		Purpose:
			Initialize Result with canonical URL, status, extracted text, and optional HTML/headers.

		Parameters:
			url (str): Canonical URL for the content.
			status_code (int): HTTP status code or 0 if not applicable.
			text (str): Extracted text content (can be empty).
			html (Optional[str]): Raw HTML used for extraction.
			headers (Optional[Dict[str, str]]): Response headers.
		"""
		self.url = url
		self.status_code = status_code
		self.text = text
		self.html = html
		self.headers = dict( headers or { } )
