from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent / "assets" / "codex_research_loop_gate_flowchart.png"


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


def center_text(draw: ImageDraw.ImageDraw, box, text: str, font, fill: str, line_gap: int = 4) -> None:
    x0, y0, x1, y1 = box
    lines = text.split("\n")
    heights = []
    widths = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = y0 + ((y1 - y0) - total_h) / 2 - 2
    for line, w, h in zip(lines, widths, heights):
        x = x0 + ((x1 - x0) - w) / 2
        draw.text((x, y), line, font=font, fill=fill)
        y += h + line_gap


def box(draw: ImageDraw.ImageDraw, xy, text: str, fill="#202E21", outline="#344125") -> None:
    draw.rectangle(xy, fill=fill, outline=outline, width=2)
    center_text(draw, xy, text, load_font(22, True), "#E7C24C")


def arrow(draw: ImageDraw.ImageDraw, start, end, color="#B99A33", width=2) -> None:
    draw.line([start, end], fill=color, width=width)
    sx, sy = start
    ex, ey = end
    if abs(ex - sx) < abs(ey - sy):
        if ey >= sy:
            pts = [(ex, ey), (ex - 6, ey - 12), (ex + 6, ey - 12)]
        else:
            pts = [(ex, ey), (ex - 6, ey + 12), (ex + 6, ey + 12)]
    else:
        if ex >= sx:
            pts = [(ex, ey), (ex - 12, ey - 6), (ex - 12, ey + 6)]
        else:
            pts = [(ex, ey), (ex + 12, ey - 6), (ex + 12, ey + 6)]
    draw.polygon(pts, fill=color)


def polyline_arrow(draw: ImageDraw.ImageDraw, points, color="#B99A33", width=2) -> None:
    for a, b in zip(points, points[1:]):
        draw.line([a, b], fill=color, width=width)
    arrow(draw, points[-2], points[-1], color=color, width=width)


def curve_arrow(draw: ImageDraw.ImageDraw, bbox, start_deg, end_deg, end_point, color="#B99A33") -> None:
    draw.arc(bbox, start=start_deg, end=end_deg, fill=color, width=2)
    # Short final arrow segment gives a crisp arrowhead.
    if start_deg < end_deg:
        pass
    arrow(draw, (end_point[0] - 2, end_point[1] - 2), end_point, color=color, width=2)


def bezier_points(p0, p1, p2, p3, steps=60):
    points = []
    for i in range(steps + 1):
        t = i / steps
        x = (
            (1 - t) ** 3 * p0[0]
            + 3 * (1 - t) ** 2 * t * p1[0]
            + 3 * (1 - t) * t**2 * p2[0]
            + t**3 * p3[0]
        )
        y = (
            (1 - t) ** 3 * p0[1]
            + 3 * (1 - t) ** 2 * t * p1[1]
            + 3 * (1 - t) * t**2 * p2[1]
            + t**3 * p3[1]
        )
        points.append((int(x), int(y)))
    return points


def bezier_arrow(draw: ImageDraw.ImageDraw, p0, p1, p2, p3, color="#B99A33", width=2) -> None:
    pts = bezier_points(p0, p1, p2, p3)
    draw.line(pts, fill=color, width=width)
    arrow(draw, pts[-4], pts[-1], color=color, width=width)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    W, H = 1143, 965
    bg = "#061F1D"
    panel = "#082622"
    gold = "#C6A33A"
    node_fill = "#202E21"
    node_outline = "#344125"

    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # Outer subtle panel.
    draw.rounded_rectangle((16, 2, W - 58, H - 10), radius=14, outline="#12322E", fill=panel, width=1)

    # Nodes.
    nodes = {
        "input": (410, 28, 620, 114),
        "normalize": (388, 176, 644, 242),
        "router": (428, 304, 604, 368),
        "execute": (428, 430, 604, 496),
        "gate": (414, 557, 618, 623),
        "human": (388, 727, 644, 793),
        "pass_review": (46, 716, 302, 803),
        "next_route": (151, 865, 367, 930),
        "fail_review": (706, 716, 962, 803),
        "retry_plan": (781, 865, 1057, 930),
    }

    labels = {
        "input": "自然语言输入 /\n当前项目状态",
        "normalize": "入口转译与任务补全",
        "router": "任务路由器",
        "execute": "子链路执行",
        "gate": "通用阀门 Gate",
        "human": "人工确认或安全暂停",
        "pass_review": "评审链路:\n下一子链路工作指导",
        "next_route": "下一子链路路由",
        "fail_review": "评审链路:\n问题诊断与修复指导",
        "retry_plan": "同一子链路下一轮计划",
    }
    for key, xy in nodes.items():
        box(draw, xy, labels[key], fill=node_fill, outline=node_outline)

    # Main vertical flow.
    x = 516
    arrow(draw, (x, 114), (x, 176), gold)
    arrow(draw, (x, 242), (x, 304), gold)
    arrow(draw, (x, 368), (x, 430), gold)
    arrow(draw, (x, 496), (x, 557), gold)
    arrow(draw, (x, 623), (x, 727), gold)

    # Branch labels.
    draw.text((150, 657), "通过", font=load_font(20, True), fill="#E7C24C")
    draw.text((800, 657), "未通过", font=load_font(20, True), fill="#E7C24C")
    draw.text((430, 657), "达到硬上限/高风险", font=load_font(20, True), fill="#E7C24C")

    # Pass branch to review, then next route, then loop back to execute.
    polyline_arrow(draw, [(414, 590), (245, 632), (175, 682), (174, 716)], gold)
    arrow(draw, (174, 803), (216, 865), gold)
    # left loop back to subchain execution.
    bezier_arrow(draw, (258, 865), (360, 830), (344, 520), (428, 493), gold)

    # Fail branch to review, then retry plan, then loop back.
    polyline_arrow(draw, [(618, 590), (785, 632), (834, 682), (834, 716)], gold)
    arrow(draw, (834, 803), (872, 865), gold)
    # right loop back to subchain execution.
    bezier_arrow(draw, (920, 865), (1018, 828), (1008, 505), (604, 475), gold)

    # Small corner icon approximation.
    draw.rounded_rectangle((1057, 22, 1065, 30), radius=2, outline="#6E6529", width=1)
    draw.rounded_rectangle((1061, 18, 1069, 26), radius=2, outline="#6E6529", width=1)

    img.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
