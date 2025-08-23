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
from typing import Optional

class Fetcher:
	"""

		Purpose:
			Responsible for retrieving raw HTML content from a given URL using HTTP(S) requests.

		Methods:
			fetch(url: str, timeout: int = 10) -> Optional[str]:
				Makes an HTTP GET request to the provided URL and returns HTML text if successful.

	"""

	def fetch( self, url: str, timeout: int = 10 ) -> Optional[ str ]:
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
			response = requests.get( url, timeout = timeout,
				headers = { "User-Agent": "SoupyBot/1.0" } )
			response.raise_for_status( )
			return response.text
		except requests.RequestException:
			return None