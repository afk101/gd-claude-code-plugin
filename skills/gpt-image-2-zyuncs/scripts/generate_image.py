#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "openai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
使用 Zyuncs 代理服务调用 cortex-19 模型（GPT Image 2）生成或编辑图片。
Zyuncs 为代理服务，接口兼容 OpenAI Images API 格式，使用 OpenAI Python SDK 作为客户端。

用法：
    uv run generate_image.py --prompt "图片描述" --filename "output.png" [选项]

选项：
    --prompt / -p        图片描述或编辑指令（必选）
    --filename / -f      输出文件名（必选）
    --input-image / -i   输入图片路径，用于图片编辑（可选，通过 extra_body.images 传递）
    --size / -s          图片尺寸：1024x1024 | 1024x1536 | 1536x1024（默认 1024x1024）
    --quality / -q       图片质量：low | medium | high | auto（默认 auto）
    --output-format / -of 输出格式：png | jpeg（默认 png）
    --n / -n             生成图片数量：1 或 2（默认 1）
    --api-key / -k       API Key（覆盖 ZYUNCS_API_KEY 环境变量）
"""

import argparse
import base64
import os
import sys
from io import BytesIO
from pathlib import Path


# ==================== 常量定义 ====================

# API 模型名称（cortex-19，底层为 GPT Image 2，通过 Zyuncs 代理调用）
MODEL_NAME = "cortex-19"

# API 默认基础地址（可通过环境变量 ZYUNCS_API_BASE_URL 覆盖）
DEFAULT_API_BASE_URL = "https://llm.api.zyuncs.com/v1"

# API 基础地址环境变量名
ENV_API_BASE_URL = "ZYUNCS_API_BASE_URL"

# API Key 环境变量名
ENV_API_KEY = "ZYUNCS_API_KEY"

# API 请求超时时间（秒，GPT Image 2 生成较慢，需较长超时）
API_TIMEOUT = 300

# 默认图片尺寸
DEFAULT_SIZE = "1024x1024"

# 默认图片质量
DEFAULT_QUALITY = "auto"

# 默认输出格式
DEFAULT_OUTPUT_FORMAT = "png"

# 默认生成数量
DEFAULT_N = 1

# 支持的尺寸列表
SUPPORTED_SIZES = ["1024x1024", "1024x1536", "1536x1024"]

# 支持的质量列表
SUPPORTED_QUALITIES = ["low", "medium", "high", "auto"]

# 支持的输出格式列表
SUPPORTED_OUTPUT_FORMATS = ["png", "jpeg"]

# 支持的生成数量列表
SUPPORTED_N_VALUES = [1, 2]

# 图片数据 URI 前缀
IMAGE_DATA_URI_PREFIX = "data:image/"

# PNG 保存格式标识
PNG_FORMAT = "PNG"

# JPEG 保存格式标识
JPEG_FORMAT = "JPEG"

# RGBA 模式标识
IMAGE_MODE_RGBA = "RGBA"

# RGB 模式标识
IMAGE_MODE_RGB = "RGB"

# RGBA 转 RGB 时的白色背景
WHITE_BACKGROUND = (255, 255, 255)

# extra_body.images 的最大输入图片数量
MAX_INPUT_IMAGES = 1


def load_dotenv(env_path: str = ".env"):
    """
    简单的 .env 文件加载器

    @param {str} env_path - .env 文件路径
    """
    env_file = Path(env_path)
    if not env_file.exists():
        return

    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ.setdefault(key, value)


def get_api_key(provided_key: str | None) -> str | None:
    """
    获取 API Key（参数优先，其次环境变量 ZYUNCS_API_KEY）

    @param {str | None} provided_key - 用户通过命令行参数提供的 Key
    @returns {str | None} API Key，不存在时返回 None
    """
    if provided_key:
        return provided_key
    return os.environ.get(ENV_API_KEY)


def create_api_client(api_key: str):
    """
    创建 OpenAI 客户端（同步模式），连接 Zyuncs API 代理

    @param {str} api_key - API 密钥
    @returns {OpenAI} OpenAI 客户端实例
    """
    from openai import OpenAI

    return OpenAI(
        api_key=api_key,
        base_url=os.environ.get(ENV_API_BASE_URL, DEFAULT_API_BASE_URL),
        timeout=API_TIMEOUT,
    )


def validate_size(size: str) -> str:
    """
    验证尺寸参数是否合法

    @param {str} size - 尺寸字符串（如 "1024x1024"）
    @returns {str} 验证后的尺寸字符串
    @raises SystemExit 尺寸不合法时退出
    """
    if size not in SUPPORTED_SIZES:
        print(f"错误：不支持的尺寸 '{size}'。", file=sys.stderr)
        print(f"支持的尺寸: {', '.join(SUPPORTED_SIZES)}", file=sys.stderr)
        sys.exit(1)
    return size


def validate_quality(quality: str) -> str:
    """
    验证质量参数是否合法

    @param {str} quality - 质量字符串（如 "high"）
    @returns {str} 验证后的质量字符串
    @raises SystemExit 质量不合法时退出
    """
    if quality not in SUPPORTED_QUALITIES:
        print(f"错误：不支持的质量 '{quality}'。", file=sys.stderr)
        print(f"支持的质量: {', '.join(SUPPORTED_QUALITIES)}", file=sys.stderr)
        sys.exit(1)
    return quality


def validate_output_format(output_format: str) -> str:
    """
    验证输出格式参数是否合法

    @param {str} output_format - 输出格式字符串（如 "png" 或 "jpeg"）
    @returns {str} 验证后的输出格式字符串
    @raises SystemExit 输出格式不合法时退出
    """
    if output_format not in SUPPORTED_OUTPUT_FORMATS:
        print(f"错误：不支持的输出格式 '{output_format}'。", file=sys.stderr)
        print(f"支持的格式: {', '.join(SUPPORTED_OUTPUT_FORMATS)}", file=sys.stderr)
        sys.exit(1)
    return output_format


def validate_n(n: int) -> int:
    """
    验证生成数量参数是否合法

    @param {int} n - 生成图片数量
    @returns {int} 验证后的数量
    @raises SystemExit 数量不合法时退出
    """
    if n not in SUPPORTED_N_VALUES:
        print(f"错误：不支持的生成数量 '{n}'。", file=sys.stderr)
        print(f"支持的数量: {', '.join(str(v) for v in SUPPORTED_N_VALUES)}", file=sys.stderr)
        sys.exit(1)
    return n


def parse_arguments():
    """
    解析命令行参数

    @returns {argparse.Namespace} 解析后的参数对象
    """
    parser = argparse.ArgumentParser(
        description="使用 cortex-19 (GPT Image 2) 生成或编辑图片"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="图片描述"
    )
    parser.add_argument(
        "--filename", "-f",
        required=True,
        help="输出文件名（例如：output.png）"
    )
    parser.add_argument(
        "--size", "-s",
        default=DEFAULT_SIZE,
        help=f"图片尺寸，可选: {', '.join(SUPPORTED_SIZES)}（默认 {DEFAULT_SIZE}）"
    )
    parser.add_argument(
        "--quality", "-q",
        default=DEFAULT_QUALITY,
        help=f"图片质量，可选: {', '.join(SUPPORTED_QUALITIES)} (默认 {DEFAULT_QUALITY})"
    )
    parser.add_argument(
        "--output-format", "-of",
        default=DEFAULT_OUTPUT_FORMAT,
        help=f"输出格式，可选: {', '.join(SUPPORTED_OUTPUT_FORMATS)}（默认 {DEFAULT_OUTPUT_FORMAT}）"
    )
    parser.add_argument(
        "--n", "-n",
        type=int,
        default=DEFAULT_N,
        help=f"生成图片数量，可选: {', '.join(str(v) for v in SUPPORTED_N_VALUES)}（默认 {DEFAULT_N}）"
    )
    parser.add_argument(
        "--input-image", "-i",
        help="可选的输入图片路径，用于图片编辑（通过 extra_body.images 传递给 API）"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="API Key（覆盖 ZYUNCS_API_KEY 环境变量）"
    )

    return parser.parse_args()


def load_input_image_as_base64(image_path: str) -> str:
    """
    加载本地图片文件并转换为 base64 编码字符串

    @param {str} image_path - 图片文件路径
    @returns {str} 图片的 base64 编码字符串（不含 data URI 前缀）
    @raises SystemExit 图片加载失败时退出
    """
    try:
        from PIL import Image as PILImage

        img = PILImage.open(image_path)
        img_format = img.format or PNG_FORMAT
        buffer = BytesIO()
        img.save(buffer, format=img_format)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")
    except Exception as e:
        print(f"加载输入图片失败: {e}", file=sys.stderr)
        sys.exit(1)


def call_api(client, prompt: str, size: str, quality: str, output_format: str, n: int, input_images: list[str] | None = None) -> dict:
    """
    调用 images.generate API 生成或编辑图片，返回原始响应字典

    cortex-19 使用 OpenAI Images API 端点（/v1/images/generations），
    不支持 chat.completions 端点（会返回 502）。
    不支持 response_format 参数（会报 Unknown parameter），
    默认返回 b64_json 格式的图片数据。

    图片编辑通过 extra_body.images 传递 base64 编码的输入图片实现，
    这是 Zyuncs 代理服务的透传参数。

    output_format 通过 extra_body 传递，因为 OpenAI SDK 不直接支持该参数。

    @param {OpenAI} client - OpenAI 客户端实例
    @param {str} prompt - 图片描述或编辑指令
    @param {str} size - 图片尺寸
    @param {str} quality - 图片质量
    @param {str} output_format - 输出格式（png/jpeg）
    @param {int} n - 生成图片数量
    @param {list[str] | None} input_images - 输入图片的 base64 编码列表（用于图片编辑）
    @returns {dict} model_dump() 后的原始响应字典
    @raises SystemExit API 调用失败时退出
    """
    try:
        # 构建 API 参数
        api_params = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "n": n,
            "size": size,
            "quality": quality,
        }

        # 构建 extra_body（合并 output_format 和 images）
        extra_body = {}
        if output_format != DEFAULT_OUTPUT_FORMAT:
            extra_body["output_format"] = output_format
        if input_images:
            extra_body["images"] = input_images

        if extra_body:
            api_params["extra_body"] = extra_body

        response = client.images.generate(**api_params)
        return response.model_dump()
    except Exception as e:
        print(f"API 调用失败: {e}", file=sys.stderr)
        sys.exit(1)


def extract_images_from_response(raw_response: dict) -> list[dict]:
    """
    从 images.generate 响应中提取图片数据列表

    cortex-19 的响应格式：
    data: [{"b64_json": "...", "revised_prompt": null, "url": null}]

    @param {dict} raw_response - model_dump() 后的原始响应字典
    @returns {list[dict]} 图片数据列表，每项包含 b64_json 和可选的 revised_prompt
    @raises SystemExit 未找到图片数据时退出
    """
    data = raw_response.get("data", [])
    if not data:
        print("错误：API 未返回图片数据。", file=sys.stderr)
        print("请重试，或尝试调整提示词。", file=sys.stderr)
        sys.exit(1)

    images = []
    for item in data:
        b64_json = item.get("b64_json")
        if b64_json:
            images.append({
                "b64_json": b64_json,
                "revised_prompt": item.get("revised_prompt"),
            })
        else:
            # URL 模式（如果 b64_json 为 null 但 url 有值）
            url = item.get("url", "")
            if url and url.startswith(IMAGE_DATA_URI_PREFIX):
                # data URI 格式
                _, b64_data = url.split(",", 1)
                images.append({
                    "b64_json": b64_data,
                    "revised_prompt": item.get("revised_prompt"),
                })

    if not images:
        print("错误：响应中无有效的图片数据。", file=sys.stderr)
        sys.exit(1)

    return images


def save_image_from_b64(b64_data: str, output_path: Path, output_format: str = "png"):
    """
    将 base64 编码的图片数据保存为文件

    根据 output_format 参数选择保存格式（png 或 jpeg）。
    处理 RGBA → RGB 转换（使用白色背景），确保 jpeg 格式下不会出错。

    @param {str} b64_data - base64 编码的图片数据
    @param {Path} output_path - 输出文件路径
    @param {str} output_format - 输出格式（"png" 或 "jpeg"）
    @raises SystemExit 保存失败时退出
    """
    try:
        from PIL import Image as PILImage

        image_bytes = base64.b64decode(b64_data)
        image = PILImage.open(BytesIO(image_bytes))

        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 处理不同的图片模式
        if output_format == "jpeg":
            # JPEG 不支持 RGBA，需要转换为 RGB
            if image.mode == IMAGE_MODE_RGBA:
                rgb_image = PILImage.new(IMAGE_MODE_RGB, image.size, WHITE_BACKGROUND)
                rgb_image.paste(image, mask=image.split()[3])
                rgb_image.save(str(output_path), JPEG_FORMAT, quality=95)
            elif image.mode == IMAGE_MODE_RGB:
                image.save(str(output_path), JPEG_FORMAT, quality=95)
            else:
                image.convert(IMAGE_MODE_RGB).save(str(output_path), JPEG_FORMAT, quality=95)
        else:
            # PNG 格式：保留所有模式
            if image.mode == IMAGE_MODE_RGBA:
                image.save(str(output_path), PNG_FORMAT)
            elif image.mode == IMAGE_MODE_RGB:
                image.save(str(output_path), PNG_FORMAT)
            else:
                # 其他模式（如 L、P 等）转为 RGB 再保存
                image.convert(IMAGE_MODE_RGB).save(str(output_path), PNG_FORMAT)

    except Exception as e:
        print(f"保存图片失败: {e}", file=sys.stderr)
        sys.exit(1)


def generate_output_filenames(base_filename: str, n: int) -> list[Path]:
    """
    根据生成数量生成输出文件名列表

    n=1 时使用原始文件名，n>1 时添加序号后缀。

    @param {str} base_filename - 用户指定的基础文件名
    @param {int} n - 生成图片数量
    @returns {list[Path]} 输出文件路径列表
    """
    if n == 1:
        return [Path(base_filename)]

    # 多张图片时添加序号后缀
    base_path = Path(base_filename)
    parent = base_path.parent
    stem = base_path.stem
    ext = base_path.suffix or ".png"
    return [parent / f"{stem}_{i}{ext}" for i in range(1, n + 1)]


def main():
    """
    主函数：编排整个图片生成流程

    流程：
    1. 加载环境变量
    2. 解析并验证命令行参数
    3. 获取并验证 API Key
    4. 创建 API 客户端
    5. 调用 images.generate API
    6. 提取并保存图片
    7. 输出保存路径和修订提示词
    """
    # 加载 .env 文件中的环境变量
    load_dotenv()

    # 解析命令行参数
    args = parse_arguments()

    # 验证参数
    size = validate_size(args.size)
    quality = validate_quality(args.quality)
    output_format = validate_output_format(args.output_format)
    n = validate_n(args.n)

    # 获取 API Key
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("错误：未提供 API Key。", file=sys.stderr)
        print("请通过以下方式之一提供：", file=sys.stderr)
        print("  1. 使用 --api-key 参数", file=sys.stderr)
        print("  2. 设置 ZYUNCS_API_KEY 环境变量", file=sys.stderr)
        sys.exit(1)

    # 创建 API 客户端
    client = create_api_client(api_key)

    # 加载输入图片（如果是编辑模式）
    input_images = None
    if args.input_image:
        input_path = Path(args.input_image)
        if not input_path.exists():
            print(f"错误：输入图片文件不存在: {args.input_image}", file=sys.stderr)
            sys.exit(1)
        print(f"加载输入图片: {args.input_image}")
        b64_image = load_input_image_as_base64(args.input_image)
        input_images = [b64_image]
        print("正在编辑图片...")
    else:
        print("正在生成图片...")

    print(f"（模型={MODEL_NAME}, 尺寸={size}, 质量={quality}, 数量={n}）")

    # 调用 API
    raw_response = call_api(client, args.prompt, size, quality, output_format, n, input_images)

    # 提取图片数据
    images = extract_images_from_response(raw_response)

    # 生成输出文件名列表
    output_paths = generate_output_filenames(args.filename, n)

    # 确保输出路径数量与图片数量一致
    while len(output_paths) < len(images):
        base_path = Path(args.filename)
        stem = base_path.stem
        ext = base_path.suffix or ".png"
        idx = len(output_paths) + 1
        output_paths.append(Path(f"{stem}_{idx}{ext}"))

    # 保存每张图片
    saved_paths = []
    for i, img_data in enumerate(images):
        output_path = output_paths[i]
        save_image_from_b64(img_data["b64_json"], output_path, output_format)
        full_path = output_path.resolve()
        saved_paths.append(full_path)

        # 输出修订提示词（如果有）
        revised_prompt = img_data.get("revised_prompt")
        if revised_prompt:
            print(f"修订提示词: {revised_prompt}")

    # 输出保存路径
    print("\n图片已保存:")
    for path in saved_paths:
        print(f"  {path}")


if __name__ == "__main__":
    main()