#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "openai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
使用 Zyuncs 代理服务调用 Gemini 3.1 Flash Image 模型（nano-banana-pro-zyuncs）生成或编辑图片。
Zyuncs 为代理服务，接口兼容 OpenAI 格式，使用 OpenAI Python SDK 作为客户端。

用法：
    uv run generate_image.py --prompt "图片描述" --filename "output.png" [--input-image "input.png"] [--api-key KEY]
"""

import argparse
import base64
import os
import sys
from io import BytesIO
from pathlib import Path


# ==================== 常量定义 ====================

# API 模型名称（lyra-flash-12，底层为 Gemini 3.1 Flash Image，通过 Zyuncs 代理调用）
MODEL_NAME = "lyra-flash-12"

# API 默认基础地址（可通过环境变量 ZYUNCS_API_BASE_URL 覆盖）
DEFAULT_API_BASE_URL = "https://llm.api.zyuncs.com/v1"

# API 基础地址环境变量名
ENV_API_BASE_URL = "ZYUNCS_API_BASE_URL"

# API Key 环境变量名
ENV_API_KEY = "ZYUNCS_API_KEY"

# API 请求超时时间（秒）
API_TIMEOUT = 120

# 最大生成 token 数（Gemini 3.1 Flash Image 官方上限：输入 131,072 / 输出 32,768）
MAX_TOKENS = 32768

# 图片数据 URI 前缀
IMAGE_DATA_URI_PREFIX = "data:image/"

# 图片类型标识（API 返回的 images 数组中的类型字段）
IMAGE_TYPE = "image_url"

# PNG 保存格式标识
PNG_FORMAT = "PNG"

# RGBA 模式标识
IMAGE_MODE_RGBA = "RGBA"

# RGB 模式标识
IMAGE_MODE_RGB = "RGB"

# RGBA 转 RGB 时的白色背景
WHITE_BACKGROUND = (255, 255, 255)


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


def parse_arguments():
    """
    解析命令行参数

    @returns {argparse.Namespace} 解析后的参数对象
    """
    parser = argparse.ArgumentParser(
        description="使用 nano-banana-pro-zyuncs (Gemini 3.1 Flash Image) 生成或编辑图片"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="图片描述或编辑指令"
    )
    parser.add_argument(
        "--filename", "-f",
        required=True,
        help="输出文件名（例如：output.png）"
    )
    parser.add_argument(
        "--input-image", "-i",
        help="可选的输入图片路径，用于图片编辑"
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
        # 获取图片格式用于 MIME 类型
        img_format = img.format or PNG_FORMAT
        buffer = BytesIO()
        img.save(buffer, format=img_format)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")
    except Exception as e:
        print(f"加载输入图片失败: {e}", file=sys.stderr)
        sys.exit(1)


def build_messages(prompt: str, base64_image: str | None = None) -> list[dict]:
    """
    构建发送给 API 的消息数组

    如果提供了 base64_image，构建 Vision 多模态消息格式（图片 + 文本）；
    否则构建纯文本消息。

    @param {str} prompt - 用户提示词（图片描述或编辑指令）
    @param {str | None} base64_image - 输入图片的 base64 编码（可选）
    @returns {list[dict]} 消息数组
    """
    if base64_image:
        # 图片编辑模式：使用 Vision 多模态消息格式
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ]
    else:
        # 图片生成模式：纯文本消息
        return [
            {
                "role": "user",
                "content": prompt,
            }
        ]


def call_api(client, messages: list[dict]) -> dict:
    """
    调用 API 生成图片（非流式模式），返回原始响应字典

    必须使用 stream=False，因为流式模式不返回图片数据。
    使用 model_dump() 获取包含非标准 images 字段的完整响应。

    @param {OpenAI} client - OpenAI 客户端实例
    @param {list[dict]} messages - 消息数组
    @returns {dict} model_dump() 后的原始响应字典
    @raises SystemExit API 调用失败时退出
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=MAX_TOKENS,
            # 流式模式不返回图片数据，必须使用非流式
            stream=False,
        )
        return response.model_dump()
    except Exception as e:
        print(f"API 调用失败: {e}", file=sys.stderr)
        sys.exit(1)


def extract_image_data(raw_response: dict) -> list[str]:
    """
    从 model_dump() 后的原始响应中提取图片 Data URI 列表

    适配 lyra-flash-12 的返回格式：
    message.images: [{"type": "image_url", "image_url": {"url": "data:..."}, "index": 0}]

    @param {dict} raw_response - model_dump() 后的原始响应字典
    @returns {list[str]} 图片 Data URI 列表
    """
    images = []
    raw_message = raw_response.get("choices", [{}])[0].get("message", {})
    image_list = raw_message.get("images", [])

    for img in image_list:
        if isinstance(img, dict):
            # 格式: {"type": "image_url", "image_url": {"url": "data:..."}, "index": 0}
            if img.get("type") == IMAGE_TYPE:
                url = img.get("image_url", {}).get("url", "")
                if url.startswith(IMAGE_DATA_URI_PREFIX):
                    images.append(url)
            # 简化格式: {"url": "data:..."}
            elif "url" in img:
                url = img["url"]
                if url.startswith(IMAGE_DATA_URI_PREFIX):
                    images.append(url)

    # 兜底：检查 content 是否直接为 Data URI
    content = raw_message.get("content", "")
    if not images and isinstance(content, str) and content.startswith(IMAGE_DATA_URI_PREFIX):
        images.append(content)

    return images


def extract_text_content(raw_response: dict) -> str:
    """
    从原始响应中提取文本内容

    @param {dict} raw_response - model_dump() 后的原始响应字典
    @returns {str} 文本内容
    """
    raw_message = raw_response.get("choices", [{}])[0].get("message", {})
    return raw_message.get("content", "") or ""


def save_image_from_data_uri(data_uri: str, output_path: Path):
    """
    将 Data URI 格式的图片数据保存为 PNG 文件

    处理 RGBA → RGB 转换（使用白色背景），确保保存为 PNG 格式。

    @param {str} data_uri - 图片 Data URI 字符串（data:image/xxx;base64,...）
    @param {Path} output_path - 输出文件路径
    @raises SystemExit 保存失败时退出
    """
    try:
        from PIL import Image as PILImage

        # 解析 Data URI，提取 base64 数据
        _, base64_data = data_uri.split(",", 1)
        image_bytes = base64.b64decode(base64_data)
        image = PILImage.open(BytesIO(image_bytes))

        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 处理不同的图片模式，统一保存为 PNG
        if image.mode == IMAGE_MODE_RGBA:
            # RGBA 转 RGB：使用白色背景
            rgb_image = PILImage.new(IMAGE_MODE_RGB, image.size, WHITE_BACKGROUND)
            rgb_image.paste(image, mask=image.split()[3])
            rgb_image.save(str(output_path), PNG_FORMAT)
        elif image.mode == IMAGE_MODE_RGB:
            image.save(str(output_path), PNG_FORMAT)
        else:
            # 其他模式（如 L、P 等）统一转为 RGB
            image.convert(IMAGE_MODE_RGB).save(str(output_path), PNG_FORMAT)

    except Exception as e:
        print(f"保存图片失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    主函数：编排整个图片生成/编辑流程

    流程：
    1. 加载环境变量
    2. 解析命令行参数
    3. 获取并验证 API Key
    4. 创建 API 客户端
    5. 加载输入图片（如果是编辑模式）
    6. 构建消息
    7. 调用 API
    8. 提取并保存图片
    """
    # 加载 .env 文件中的环境变量
    load_dotenv()

    # 解析命令行参数
    args = parse_arguments()

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

    # 设置输出路径
    output_path = Path(args.filename)

    # 加载输入图片（如果是编辑模式）
    base64_image = None
    if args.input_image:
        input_path = Path(args.input_image)
        if not input_path.exists():
            print(f"错误：输入图片文件不存在: {args.input_image}", file=sys.stderr)
            sys.exit(1)
        print(f"加载输入图片: {args.input_image}")
        base64_image = load_input_image_as_base64(args.input_image)
        print("正在编辑图片...")
    else:
        print("正在生成图片...")

    # 构建消息
    messages = build_messages(args.prompt, base64_image)

    # 调用 API
    raw_response = call_api(client, messages)

    # 提取文本内容（如果有）
    text_content = extract_text_content(raw_response)
    if text_content:
        print(f"模型回复: {text_content}")

    # 提取图片数据
    image_data_uris = extract_image_data(raw_response)

    if not image_data_uris:
        print("错误：API 未返回图片数据。", file=sys.stderr)
        print("请重试，或尝试调整提示词。", file=sys.stderr)
        sys.exit(1)

    # 保存第一张图片（API 通常只返回一张）
    save_image_from_data_uri(image_data_uris[0], output_path)

    # 输出保存路径
    full_path = output_path.resolve()
    print(f"\n图片已保存: {full_path}")


if __name__ == "__main__":
    main()
