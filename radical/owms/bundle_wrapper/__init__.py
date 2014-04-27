import os
import sys

BUNDLE_REL_DIR='../external/bundle/src'

self_dir = os.path.dirname(__file__)
bundle_root = os.path.join(self_dir, BUNDLE_REL_DIR)
sys.path.append(bundle_root)

from bundle import BundleManager
