import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from render import carousel, contrast, humor, product, reel  # noqa: E402

FORMATS = {"product": product, "carousel": carousel, "contrast": contrast, "humor": humor, "reel": reel}


def render(spec, out):
    return FORMATS[spec.get("format", "product")].render(spec, out)


if __name__ == "__main__":
    spec_path, out_path = sys.argv[1], sys.argv[2]
    for f in render(json.loads(Path(spec_path).read_text(encoding="utf-8")), out_path):
        print(f)
