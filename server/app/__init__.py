"""
Setup logging
"""
import logging
import os
import sys

DEBUG = os.environ.get("DEBUG", "False") != "False"

LEVEL = logging.DEBUG if DEBUG else logging.INFO

logging.basicConfig(
    level=LEVEL,
    stream=sys.stdout,
    format="%(asctime)s %(name)s.%(funcName)s +%(lineno)s:\
         %(levelname)-8s [%(process)d] %(message)s",
)
