import sys
import traceback
from util import Logger

LOGGER = Logger()

try:
    LOGGER.log(str(sys.argv))
    sys.exit()

except Exception as e:
    LOGGER.log(traceback.format_exc())