'''
	******************************************************************************************
	  Assembly:                Soupy
	  Filename:                writers.py
	  Author:                  Terry D. Eppler
	  Created:                 05-31-2022

	  Last Modified By:        Terry D. Eppler
	  Last Modified On:        05-01-2025
	******************************************************************************************
	<copyright file="writers.py" company="Terry D. Eppler">

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
	writers.py
	</summary>
	******************************************************************************************
'''
from pathlib import Path
from typing import Optional
from .core import Result


class Writer:
	"""

		Purpose:
			Responsible for writing extracted text into a Markdown (.md) file.

		Methods:
			write(text: str, filename: str, output_dir: str = "output") -> Optional[Path]:
				Saves text into a Markdown file in the specified directory.

	"""

	def write( self, text: str, filename: str, output_dir: str = 'output' ) -> Optional[ Path ]:
		"""

			Purpose:
				Save text into a Markdown file.

			Parameters:
				text (str): Text content to save.
				filename (str): Desired Markdown filename (without extension).
				output_dir (str): Directory to save the file into.

			Returns:
				Optional[Path]: Path to the saved file if successful, otherwise None.

		"""
		try:
			output_path = Path( output_dir )
			output_path.mkdir( parents = True, exist_ok = True )

			file_path = output_path / f'{filename}.md'
			file_path.write_text( text, encoding = 'utf-8' )
			return file_path
		except Exception:
			return None

class MarkdownWriter:
	"""

		Purpose:
			Serialize a `Result` into a Markdown file with a small YAML header.


	"""
	def write( self, result: Result, path: str | Path ) -> Path:
		"""

			Purpose:
				Write a `Result` to a Markdown file (front matter + body).

			Parameters:
				result (Result): Result object containing url/status/text/html.
				path (str | Path): Destination path to write.

			Returns:
				Path: The absolute path of the written file.

		"""
		if result is None:
			raise ValueError( 'result cannot be None' )
		if path is None:
			raise ValueError( 'path cannot be None' )
		p = Path( path ).resolve( )
		p.parent.mkdir( parents = True, exist_ok = True )

		front_matter = (
				'---\n'
				f'source_url: {result.url}\n'
				f'status_code: {result.status_code}\n'
				'---\n\n'
		)
		body = result.text if result.text.endswith( '\n' ) else result.text + '\n'
		p.write_text( front_matter + body, encoding = 'utf-8' )
		return p
