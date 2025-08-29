'''
******************************************************************************************
  Assembly:                Soupy
  Filename:                core.py
  Author:                  Terry D. Eppler (adapted by Bro)
  Created:                 05-31-2022
  Last Modified By:        Terry D. Eppler
  Last Modified On:        08-25-2025
******************************************************************************************
<copyright file="core.py" company="Terry D. Eppler">

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

 THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT.
 IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 DEALINGS IN THE SOFTWARE.

 You can contact me at:  terryeppler@gmail.com or eppler.terry@epa.gov

</copyright>
<summary>
    core.py — lightweight immutable result container and small core helpers
</summary>
******************************************************************************************
'''
from __future__ import annotations

from typing import Dict, Optional, Any

from boogr import Error, ErrorDialog

def throw_if( name: str, value: object ) -> None:
	"""

	Purpose:
	--------
	Lightweight guard used to validate required arguments. Treats None and
	empty/whitespace-only strings as invalid values and raises ValueError.

	Parameters:
	----------
	name (str): Human-friendly argument name used in the raised message.
	value (object): Value to validate.

	Returns:
	-------
	None

	"""
	if value is None:
		raise ValueError( f'Argument "{name}" cannot be None' )
	if isinstance( value, str ) and not value.strip( ):
		raise ValueError( f'Argument "{name}" cannot be an empty string' )

class Result:
	"""

	Purpose:
	--------
	Immutable container that represents the outcome of fetching a single
	page. It stores the canonical URL, http status code, extracted plain
	text, optional raw HTML, and response headers.

	Parameters:
	----------
	url (str): Canonical URL that was fetched.
	status_code (int): HTTP status code (use 0 when not applicable).
	text (str): Extracted plain text content (may be empty).
	html (Optional[str]): Raw HTML from the response, if available.
	headers (Optional[Dict[str, str]]): Response headers, if available.

	Returns:
	-------
	None

	"""

	__slots__ = ("url", "status_code", "text", "html", "headers")

	def __init__(
			self,
			url: str,
			status_code: int,
			text: str,
			html: Optional[ str ] = None,
			headers: Optional[ Dict[ str, str ] ] = None,
	) -> None:
		try:
			throw_if( "url", url )

			self.url: str = url
			self.status_code: int = int( status_code )
			self.text: str = text or ""
			self.html: Optional[ str ] = html
			self.headers: Dict[ str, str ] = dict( headers or { } )
		except Exception as exc:  # pragma: no cover - bubble up via ErrorDialog
			err = Error( exc )
			err.module = "soupy"
			err.cause = "Result.__init__"
			err.method = "__init__(url,status_code,text,html,headers)"
			dlg = ErrorDialog( err )
			dlg.show( )
			raise

	def __dir__( self ) -> list[ str ]:
		"""

		Purpose:
		--------
		Provide a stable ordering of attributes used by GUIs or inspector tooling.

		Returns:
		-------
		list[str]: attribute names in a stable order.

		"""
		return [ "url", "status_code", "text", "html", "headers", "has_html" ]

	def to_dict( self ) -> Dict[ str, Any ]:
		"""

		Purpose:
		--------
		Produce a plain dictionary representation of the Result for serialization
		or tests. This copies headers to avoid outside mutations.

		Parameters:
		----------
		None

		Returns:
		-------
		Dict[str, Any]: dictionary with keys url, status_code, text, html, headers

		"""
		return {
				"url": self.url,
				"status_code": self.status_code,
				"text": self.text,
				"html": self.html,
				"headers": dict( self.headers ),
		}

	@property
	def has_html( self ) -> bool:
		"""

		Purpose:
		--------
		Indicate whether the Result includes non-empty HTML content.

		Parameters:
		----------
		None

		Returns:
		-------
		bool: True when html is a non-empty string; otherwise False.

		"""
		return isinstance( self.html, str ) and bool( self.html.strip( ) )

	def __repr__( self ) -> str:
		return f"Result(url={self.url!r}, status_code={self.status_code}, text_len={len( self.text )})"

def result_from_response( url: str, response ) -> Result:
	"""

	Purpose:
	--------
	Helper factory that builds a Result from a requests-like response object.
	The function expects the response to have attributes .status_code, .text,
	.headers and .content (optional). It is forgiving for missing attributes
	to make testing easier.

	Parameters:
	----------
	url (str): Canonical URL that was fetched.
	response: Response-like object with attributes used above.

	Returns:
	-------
	Result: constructed Result instance.

	"""
	try:
		throw_if( "url", url )

		status = int( getattr( response, "status_code", 0 ) )
		text = getattr( response, "text", "" ) or ""
		headers = getattr( response, "headers", None ) or { }

		# prefer the text field for html when present
		html = getattr( response, "text", None )

		return Result( url = url, status_code = status, text = text, html = html,
			headers = headers )
	except Exception as exc:  # pragma: no cover - surface via ErrorDialog
		err = Error( exc )
		err.module = "soupy"
		err.cause = "result_from_response"
		err.method = "result_from_response(url,response)"
		dlg = ErrorDialog( err )
		dlg.show( )
		raise
