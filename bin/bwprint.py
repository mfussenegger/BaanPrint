#!/usr/bin/env python

try:
    from baanprint import bwprint
except ImportError:
    import sys
    import os
    path = os.path.abspath(os.path.join(__file__, '../../'))
    sys.path.insert(0, path)
    from baanprint import bwprint

bwprint.main()
