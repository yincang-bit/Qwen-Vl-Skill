"""
Qwen-VL image analysis helper.
Usage:
    python qwen_vl.py <image_path> [--prompt "your question"] [--model qwen3-vl-flash]
    python qwen_vl.py <image_path> --ocr
"""
import sys, os, json, base64, argparse, io

# Fix Windows GBK encoding issue
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

API_KEY = os.environ.get("DASHSCOPE_API_KEY")
API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
DEFAULT_MODEL = "qwen3-vl-flash"
OCR_MODEL = "qwen-vl-ocr-latest"

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def get_mime(path):
    ext = os.path.splitext(path)[1].lower()
    return {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "gif": "image/gif", "webp": "image/webp", "bmp": "image/bmp"}.get(ext, "image/png")

def call_vl(image_paths, prompt="请详细描述这张图片的内容。", model=DEFAULT_MODEL, max_tokens=2000):
    import urllib.request

    if not API_KEY:
        raise RuntimeError("DASHSCOPE_API_KEY is not set")

    content = [{"type": "text", "text": prompt}]
    for path in image_paths:
        b64 = encode_image(path)
        mime = get_mime(path)
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{b64}"}
        })

    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": max_tokens
    }).encode()

    req = urllib.request.Request(API_URL, data=body, headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    })

    resp = urllib.request.urlopen(req, timeout=120)
    data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]

def main():
    parser = argparse.ArgumentParser(description="Qwen-VL image analysis")
    parser.add_argument("images", nargs="+", help="Image file path(s)")
    parser.add_argument("--prompt", "-p", default=None, help="Custom question about the image")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help=f"Model (default: {DEFAULT_MODEL})")
    parser.add_argument("--ocr", action="store_true", help="OCR-optimized mode")
    parser.add_argument("--max-tokens", type=int, default=2000, help="Max output tokens")
    parser.add_argument("--output", "-o", default=None, help="Save result to file")

    args = parser.parse_args()

    # Validate images
    for path in args.images:
        if not os.path.exists(path):
            print(f"ERROR: File not found: {path}", file=sys.stderr)
            sys.exit(1)

    model = OCR_MODEL if args.ocr else args.model

    if args.prompt:
        prompt = args.prompt
    elif args.ocr:
        prompt = "请识别并提取这张图片中的所有文字内容，保持原文格式，不要遗漏任何文字。"
    else:
        prompt = "请详细描述这张图片的内容，包括布局、文字、图表、数据等所有可见信息。如有表格，请逐行列出；如有图表，请解释其含义。"

    try:
        result = call_vl(args.images, prompt=prompt, model=model, max_tokens=args.max_tokens)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"Saved to: {args.output}")
        print(result)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()