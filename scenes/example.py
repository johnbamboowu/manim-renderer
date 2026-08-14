"""
将军过河问题 — 反射原理求最短路径

经典数学问题：
将军从 A 点出发，要到河边（直线 l）取水，再到 B 点。
问：在河边哪个位置取水，走的总距离最短？

解法：将 A 关于直线 l 做对称点 A'，连接 A'B，
与 l 的交点 P 就是最短路径的取水点。
因为 AP = A'P（对称性），所以 AP + PB = A'P + PB = A'B。
"""

from manim import *
import numpy as np


class GeneralRiverCrossing(Scene):
    """将军过河问题 — 完整动画演示（正确坐标版）"""

    def construct(self):
        # === 坐标设定 ===
        # 河: y = 0
        # A: (-3, 3), B: (4, 2)  (都在河上方，需要过河取水再回来)
        # A': (-3, -3) (A 关于 y=0 的对称点)
        # A'B 直线: (-3,-3) → (4,2), 斜率 = 5/7
        # 与 y=0 交点: x = 21/5 - 3 = 1.2
        # 所以 P = (1.2, 0)

        A = np.array([-3, 3, 0])
        B = np.array([4, 2, 0])
        A_prime = np.array([-3, -3, 0])
        P = np.array([1.2, 0, 0])

        # === 标题 ===
        title = Text("将军过河问题", font_size=48, color=WHITE)
        subtitle = Text("反射原理 × 最短路径", font_size=28, color=GRAY_B)
        subtitle.next_to(title, DOWN, buff=0.3)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=0.8)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))

        # === 河流 ===
        river = Line(LEFT * 5.5, RIGHT * 5.5, color=BLUE_D, stroke_width=5)
        river_label = Text("河", font_size=24, color=BLUE_C).shift(RIGHT * 5 + UP * 0.3)
        self.play(Create(river), FadeIn(river_label))

        # === A 点和 B 点 ===
        dot_a = Dot(A, color=YELLOW, radius=0.12)
        dot_b = Dot(B, color=YELLOW, radius=0.12)
        lbl_a = Text("A（将军）", font_size=20, color=YELLOW).next_to(dot_a, UP, 0.2)
        lbl_b = Text("B（营地）", font_size=20, color=YELLOW).next_to(dot_b, UP, 0.2)
        self.play(FadeIn(dot_a, scale=1.5), Write(lbl_a), FadeIn(dot_b, scale=1.5), Write(lbl_b))
        self.wait(1)

        # === 题目说明 ===
        problem = VGroup(
            Text("从 A 出发 → 到河边取水 → 到 B", font_size=20, color=WHITE),
            Text("❓ 哪个位置取水走的路最短？", font_size=22, color=YELLOW),
        ).arrange(DOWN, buff=0.2).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(problem))
        self.wait(2)
        self.play(FadeOut(problem))

        # === 几个候选取水点（灰色路径）===
        candidates_x = [-1.5, 0, 2.5]
        c_dots = VGroup()
        c_paths = VGroup()
        c_labels = VGroup()
        for i, cx in enumerate(candidates_x):
            cp = Dot(RIGHT * cx, color=GRAY, radius=0.06)
            cl = Text(f"P{i+1}", font_size=14, color=GRAY).next_to(cp, UP, 0.1)
            path1 = Line(A, cp.get_center(), color=GRAY, stroke_width=1.5, stroke_opacity=0.4)
            path2 = Line(cp.get_center(), B, color=GRAY, stroke_width=1.5, stroke_opacity=0.4)
            c_dots.add(cp)
            c_labels.add(cl)
            c_paths.add(VGroup(path1, path2))

        self.play(
            *[FadeIn(d) for d in c_dots],
            *[FadeIn(l) for l in c_labels],
            *[Create(p) for p in c_paths],
            run_time=1
        )
        self.wait(1.5)

        # 清除候选
        self.play(*[FadeOut(m) for m in [*c_dots, *c_labels, *c_paths]])

        # === 反射原理 ===
        method = VGroup(
            Text("💡 反射原理", font_size=24, color=YELLOW),
            Text("1. 将 A 关于河岸做对称点 A'", font_size=18, color=WHITE),
            Text("2. 连接 A'B，交河岸于 P", font_size=18, color=WHITE),
            Text("3. AP + PB 最短！", font_size=18, color=GREEN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_edge(LEFT, buff=0.4).shift(UP * 0.3)
        self.play(FadeIn(method, shift=RIGHT * 0.3))
        self.wait(1.5)

        # === A' 对称点 ===
        dot_ap = Dot(A_prime, color=RED, radius=0.12)
        lbl_ap = Text("A'", font_size=24, color=RED).next_to(dot_ap, DOWN, 0.15)
        dash = DashedLine(A, A_prime, color=RED, stroke_width=1.5, dash_length=0.1)
        mirror_lbl = Text("对称", font_size=16, color=RED).next_to(dash, LEFT, 0.1)

        self.play(Create(dash), FadeIn(dot_ap, scale=1.5), Write(lbl_ap), run_time=1)
        self.play(Write(mirror_lbl))
        self.wait(1)

        # === A'B 连线 ===
        line_ap_b = Line(A_prime, B, color=RED, stroke_width=2, stroke_opacity=0.6)
        self.play(Create(line_ap_b), run_time=1)
        self.wait(0.5)

        # === 交点 P ===
        dot_p = Dot(P, color=GREEN, radius=0.14)
        lbl_p = Text("P（最优取水点）", font_size=22, color=GREEN).next_to(dot_p, UP, 0.2)
        self.play(FadeIn(dot_p, scale=1.5), Write(lbl_p), run_time=0.8)
        self.wait(1)

        # === 最短路径高亮 ===
        path_ap = Line(A, P, color=GREEN, stroke_width=4)
        path_pb = Line(P, B, color=GREEN, stroke_width=4)
        self.play(Create(path_ap), run_time=0.8)
        self.play(Create(path_pb), run_time=0.8)

        d1 = np.linalg.norm(A - P)
        d2 = np.linalg.norm(B - P)
        total = d1 + d2

        dist = Text(f"AP + PB = {total:.2f}（最短）", font_size=22, color=GREEN)
        dist.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(dist))
        self.wait(1.5)

        # === 证明要点 ===
        self.play(FadeOut(method))
        proof = VGroup(
            Text("证明要点：", font_size=22, color=YELLOW),
            Text("AP = A'P（对称）", font_size=18, color=WHITE),
            Text("AP + PB = A'P + PB = A'B", font_size=18, color=WHITE),
            Text("任何其他点 Q：AQ + QB = A'Q + QB > A'B", font_size=18, color=GRAY),
            Text("∴ P 是唯一最优点 ✓", font_size=20, color=GREEN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_edge(LEFT, buff=0.5).shift(UP * 0.5)
        for line in proof:
            self.play(Write(line), run_time=0.5)
        self.wait(2)

        # === 闪烁 ===
        self.play(Indicate(path_ap, color=GREEN, scale_factor=1.1))
        self.play(Indicate(path_pb, color=GREEN, scale_factor=1.1))

        # === 结束 ===
        end = Text("反射原理：化折线为直线", font_size=30, color=YELLOW)
        end.to_edge(DOWN, buff=0.3)
        self.play(FadeOut(dist), FadeIn(end))
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.5)


class QuickDemo(Scene):
    """30秒快速演示版"""

    def construct(self):
        title = Text("将军过河 × 反射原理", font_size=36, color=YELLOW)
        self.play(Write(title))
        self.wait(0.5)
        self.play(FadeOut(title))

        # 河
        river = Line(LEFT * 5, RIGHT * 5, color=BLUE_D, stroke_width=4)
        self.play(Create(river))

        # A, B
        a = Dot(LEFT * 3 + UP * 2.5, color=YELLOW, radius=0.12)
        b = Dot(RIGHT * 3 + UP * 2.5, color=YELLOW, radius=0.12)
        la = Text("A", font_size=24, color=YELLOW).next_to(a, UP, 0.15)
        lb = Text("B", font_size=24, color=YELLOW).next_to(b, UP, 0.15)
        self.play(FadeIn(a), Write(la), FadeIn(b), Write(lb))

        # A'
        a_prime = Dot(LEFT * 3 + DOWN * 2.5, color=RED, radius=0.12)
        lap = Text("A'", font_size=24, color=RED).next_to(a_prime, DOWN, 0.15)
        dash = DashedLine(a.get_center(), a_prime.get_center(), color=RED, stroke_width=1.5)
        self.play(Create(dash), FadeIn(a_prime), Write(lap))

        # A'B
        self.play(Create(Line(a_prime.get_center(), b.get_center(), color=RED, stroke_width=2, stroke_opacity=0.7)))

        # P
        # A'(−3,−2.5) → B(3,2.5): 斜率=5/6, y=0 → x=0
        p = Dot(ORIGIN, color=GREEN, radius=0.12)
        lp = Text("P", font_size=24, color=GREEN).next_to(p, UP, 0.15)
        self.play(FadeIn(p, scale=1.5), Write(lp))

        # 最短路径
        self.play(Create(Line(a.get_center(), p.get_center(), color=GREEN, stroke_width=3)))
        self.play(Create(Line(p.get_center(), b.get_center(), color=GREEN, stroke_width=3)))

        conclusion = Text("AP + PB 最短 ✓", font_size=28, color=GREEN).to_edge(DOWN, 0.4)
        self.play(Write(conclusion))
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])
