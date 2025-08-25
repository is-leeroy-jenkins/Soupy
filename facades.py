'''
  ******************************************************************************************
      Assembly:                Soupy
      Filename:                facades.py
      Author:                  Terry D. Eppler
      Created:                 05-31-2022

      Last Modified By:        Terry D. Eppler
      Last Modified On:        05-01-2025
  ******************************************************************************************
  <copyright file="facades.py" company="Terry D. Eppler">

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
    facades.py
  </summary>
  ******************************************************************************************
'''
from typing import Optional
from .scrapers import Scraper

class Soupy:
	"""
	Purpose:
		Facade class providing a simple, user-friendly interface for scraping websites.

	Methods:
		save_as_markdown(url: str, file: str, dir: str = "output") -> Optional[str]:
			High-level method to scrape a website and store the result in Markdown format.
	"""

	def __init__( self ) -> None:
		self.scraper = Scraper( )

	def save_as_markdown( self, url: str, filename: str, output_dir: str = "output" ) -> Optional[
		str ]:
		"""
		Purpose:
			Fetch, parse, and save a webpage's text to Markdown.

		Parameters:
			url (str): Target website URL.
			filename (str): Desired Markdown file (without extension).
			output_dir (str): Directory to save the file into.

		Returns:
			Optional[str]: Path to the saved file if successful, otherwise None.
		"""
		return self.scraper.scrape( url, filename, output_dir )