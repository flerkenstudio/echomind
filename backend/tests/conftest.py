import os
import sys
import tempfile
from pathlib import Path

os.environ["USE_MOCK_LLM"] = "true"
os.environ["USE_LOCAL_STORE"] = "true"
os.environ["LOCAL_DATA_DIR"] = tempfile.mkdtemp(prefix="echomind_test_")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
