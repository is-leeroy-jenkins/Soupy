"""
Purpose:
    Soupy package initializer exposing public APIs.

Exports:
    Result, WebFetcher, WebCrawler, MarkdownWriter, Soupy
"""

from .core import Result
from .fetchers.web_fetcher import WebFetcher
from .fetchers.web_crawler import WebCrawler
from .io import MarkdownWriter
from .facade import Soupy

__all__ = [ "Result", "WebFetcher", "WebCrawler", "MarkdownWriter", "Soupy" ]