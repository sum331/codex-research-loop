from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent / "assets" / "codex_research_loop_simple_mindmap.png"


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def draw_card(draw: ImageDraw.ImageDraw, box, title: str, items: list[str], fill: str, outline: str) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=24, fill=fill, outline=outline, width=3)
    draw.text((x0 + 24, y0 + 22), title, font=load_font(28, True), fill="#0B2545")
    y = y0 + 76
    for item in items:
        draw.text((x0 + 30, y), "- " + item, font=load_font(24), fill="#1F2933")
        y += 36


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    width, height = 1600, 980
    image = Image.new("RGB", (width, height), "#FAFBFC")
    draw = ImageDraw.Draw(image)

    navy = "#0B2545"
    blue = "#2E74B5"
    line = "#9AA8B5"
    muted = "#52616B"

    draw.text((90, 55), "Codex Research Loop", font=load_font(48, True), fill=navy)
    draw.text(
        (92, 118),
        "通用科研工作流：从自然语言输入到多链路执行、质量阀门与成果交付",
        font=load_font(26),
        fill=muted,
    )

    center = (570, 350, 1030, 610)
    draw.rounded_rectangle(center, radius=36, fill=navy, outline=navy)
    draw.text((655, 415), "Research Loop", font=load_font(42, True), fill="white")
    draw.text((650, 482), "项目控制平面", font=load_font(30, True), fill="#D9EAF7")
    draw.text((626, 535), ".research-loop / route / gate", font=load_font(23), fill="#D9EAF7")

    nodes = [
        ((90, 215, 425, 365), "1  输入转化", ["自然语言补全", "normalize / route"], "#EEF6FF", blue),
        ((90, 435, 425, 585), "2  项目记忆", ["材料护照", "证据账本 / 决策日志"], "#F4F7FB", "#52616B"),
        ((90, 655, 425, 805), "3  存储规范", ["旧项目 adaptive", "新项目 canonical"], "#F4FFF7", "#2D7D46"),
        ((1175, 215, 1510, 365), "4  多链路执行", ["P1-P10 子链路", "文献 / 数据 / 写作 / 评审"], "#EEF6FF", blue),
        ((1175, 435, 1510, 585), "5  深循环阀门", ["deep-loop 判断", "auto-loop 自启动"], "#F5F3FF", "#6D5BD0"),
        ((1175, 655, 1510, 805), "6  问题与成果", ["P10 隔离诊断", "J1030 报告展示"], "#FFF7ED", "#B45309"),
    ]

    cx_left, cx_right = center[0], center[2]
    cy = (center[1] + center[3]) // 2
    for box, title, items, fill, outline in nodes:
        x0, y0, x1, y1 = box
        target_y = (y0 + y1) // 2
        if x1 < center[0]:
            draw.line((cx_left, cy, x1, target_y), fill=line, width=5)
            draw.ellipse((x1 - 8, target_y - 8, x1 + 8, target_y + 8), fill=outline)
        else:
            draw.line((cx_right, cy, x0, target_y), fill=line, width=5)
            draw.ellipse((x0 - 8, target_y - 8, x0 + 8, target_y + 8), fill=outline)
        draw_card(draw, box, title, items, fill, outline)

    strip = (250, 865, 1350, 925)
    draw.rounded_rectangle(strip, radius=28, fill="#E8EEF5", outline="#D3DCE6")
    flow = "输入 → 路由 → 执行 → 评审 → 继续/重试/诊断 → 交付"
    bbox = draw.textbbox((0, 0), flow, font=load_font(29, True))
    draw.text(((width - (bbox[2] - bbox[0])) // 2, 878), flow, font=load_font(29, True), fill=navy)

    image.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
