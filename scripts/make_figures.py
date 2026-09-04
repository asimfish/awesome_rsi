# -*- coding: utf-8 -*-
"""Survey-grade overview figures for awesome_rsi.
Fig.1  Swimlane timeline (families x years, one labeled pill per work; 1965-2014 prehistory + 2023-2026)
Fig.2  Taxonomy tree (root -> 7 branches -> sub-categories with representative works)
Outputs light (README / full report) and dark (slides) SVG variants under assets/.
Usage: python3 scripts/make_figures.py
"""
import pathlib
from xml.sax.saxutils import escape as E

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "assets"; OUT.mkdir(exist_ok=True)

# (label, year, month, family, star)  month = arXiv v1 month; non-arXiv materials approximate to release month
WORKS = [
 ("Good '65",1965,1,"origin",0),("Vinge '93",1993,3,"origin",0),("GISAI",2001,6,"origin",0),
 ("Gödel Machine",2003,9,"origin",0),("Omohundro",2008,1,"origin",0),("Chalmers",2010,6,"origin",0),
 ("IEM",2013,9,"origin",0),("Superintelligence",2014,7,"origin",0),
 ("Voyager",2023,5,"knowledge",0),("Erdil&Besiroglu",2023,9,"survey",0),("STOP",2023,10,"frame",0),
 ("AI Scientist",2024,8,"industry",0),("ADAS",2024,8,"harness",0),("Gödel Agent",2024,10,"frame",0),("AFlow",2024,10,"harness",0),
 ("METR 地平线",2025,3,"survey",0),("SICA",2025,4,"frame",0),("DGM",2025,5,"frame",1),("AlphaEvolve",2025,6,"industry",0),
 ("GEPA",2025,7,"harness",0),("TMLR 综述",2025,7,"survey",0),("ShinkaEvolve",2025,9,"industry",0),("ACE",2025,10,"harness",0),
 ("ASG-SI",2025,12,"safety",0),
 ("ECHO",2026,1,"model",1),("MCE",2026,1,"harness",0),("Why LLMs≠Scientists",2026,1,"industry",0),
 ("ARA",2026,2,"safety",0),("SkillRL",2026,2,"knowledge",0),
 ("HyperAgents",2026,3,"frame",0),("Meta-Harness",2026,3,"harness",0),
 ("AHE",2026,4,"harness",0),
 ("EvoLM",2026,5,"eval",1),("Continual Harness",2026,5,"online",1),("MOSS",2026,5,"frame",1),("Evolving-RL",2026,5,"knowledge",0),
 ("DemoEvolve",2026,5,"harness",0),("ScientistOne",2026,5,"industry",0),("SIA",2026,5,"harness",0),("Harness≠Benefit",2026,5,"harness",0),
 ("Self-Harness",2026,6,"harness",0),("Adaptive Auto-Harness",2026,6,"harness",0),("SCORE",2026,6,"eval",0),
 ("RHO",2026,6,"eval",0),("HarnessFix",2026,6,"safety",0),("Autodata",2026,6,"industry",0),("RQGM",2026,6,"eval",1),
 ("Weng 总纲",2026,7,"industry",1),("Anthropic 进度报告",2026,7,"industry",1),("WGtG",2026,7,"eval",1),
 ("Falsifiable Gates",2026,7,"safety",0),("Co-Harness",2026,7,"model",0),
 ("SkillProx",2026,8,"knowledge",0),("Coding 综述",2026,8,"survey",0),("SESG",2026,8,"safety",0),("HSI",2026,8,"harness",0),
 ("OLE",2026,8,"safety",0),("Co-Evolution 综述",2026,8,"survey",0),("ERSkill",2026,8,"knowledge",0),("Evo-Harness",2026,8,"knowledge",0),
 ("SkillCommit",2026,8,"knowledge",0),("HyperSkill",2026,8,"knowledge",0),("EvalCEGAR",2026,8,"eval",0),("EnvHarness",2026,8,"online",0),
 ("HVTB",2026,8,"safety",0),("AutoSaddler",2026,8,"harness",0),("MetaCaster",2026,8,"harness",0),("Prime Agent",2026,8,"online",0),
 ("Metan",2026,8,"frame",0),("WikiSkill",2026,8,"knowledge",1),("iCoder",2026,8,"industry",1),
]
FAM = {
 "origin":   ("思想史 · 前史",             "#475569"),
 "survey":   ("综述 · 宏观与测量",         "#a16207"),
 "frame":    ("框架侧 · 自改写源码",       "#d97706"),
 "harness":  ("harness 工程 · 脚手架进化", "#0e7490"),
 "eval":     ("评估侧 · 评估器共进化",     "#dc2626"),
 "model":    ("权重侧 · 模型自训练",       "#7c3aed"),
 "knowledge":("知识侧 · 经验→技能",        "#059669"),
 "online":   ("在线侧 · 免重置 / 环境侧",  "#db2777"),
 "safety":   ("安全治理 · 部署纪律",       "#ea580c"),
 "industry": ("自动研究 · 工业实证",       "#2563eb"),
}
LANES = ["industry","frame","harness","eval","model","knowledge","online","safety","survey","origin"]

TAXONOMY = [
 ("思想史与判据\n（1965-2014）", "origin", [
   ("正反馈猜想 · 智能爆炸", ["Good '65","Vinge '93"]),
   ("能力构造与持续条件", ["GISAI '01（三能力 · 每级须开新机会）"]),
   ("自指完备的形式化极限", ["Gödel Machine '03"]),
   ("动力学判据 crossover / recalcitrance", ["Superintelligence '14","IEM '13","Chalmers '10"]),
   ("工具性驱力 · 安全起点", ["Omohundro '08"]),
 ]),
 ("改哪层\n（自我修改的介质）", "frame", [
   ("源码层 · 改自身 harness 代码", ["DGM","MOSS","Gödel Agent","SICA","Meta-Harness","HyperAgents"]),
   ("文本层 · 提示 / 技能 / 记忆", ["GEPA","ACE","MCE","Continual Harness","AutoSaddler","Self-Harness","RHO"]),
   ("权重层 · 微调 / RL", ["EvoLM","ECHO","Co-Harness","iCoder","SESG","SkillRL","Evolving-RL"]),
   ("环境层 · 进化任务而非 agent", ["EnvHarness"]),
   ("改输入不改机器 · 递归 Ω", ["Metan"]),
 ]),
 ("锚在哪\n（不参与进化的部件）", "eval", [
   ("人工锚定集 · 人类标注", ["Who Grades the Grader","RQGM（CRAVE / APReS / IMO-GradingBench）"]),
   ("冻结评估器 / PRM / 教师", ["Continual Harness","RQGM（epoch 内冻结）","ECHO（环境奖励）"]),
   ("回归门 / 泛化门", ["Self-Harness","AutoSaddler","SkillProx","Co-Harness"]),
   ("冻结外层 proposer / Ω", ["Meta-Harness","Metan"]),
   ("原始验证器锁死", ["EnvHarness","iCoder","MetaCaster"]),
   ("锚驱动进化 · 碰撞对", ["EvalCEGAR"]),
   ("无锚 · 自偏好（单轮）", ["RHO"]),
 ]),
 ("时间模式\n（何时改）", "online", [
   ("重置式 · 完整评测后选择", ["DGM","RQGM","GEPA","Meta-Harness"]),
   ("免重置 · 故障现场精炼", ["Continual Harness","Prime Agent"]),
   ("离线批次 · 双环交替", ["Co-Harness","AutoSaddler"]),
   ("任务时 / 任务后 / 阶段式", ["Self-Evolving Coding Agents 综述"]),
 ]),
 ("知识侧\n（经验如何复利）", "knowledge", [
   ("经验 → wiki → 技能", ["WikiSkill"]),
   ("行为验证的层级抽象", ["SkillCommit"]),
   ("超图 · 组合关系保留", ["HyperSkill"]),
   ("检索行为技能化 · 双 frontier", ["ERSkill"]),
   ("近端文本梯度 · 删除一等公民", ["SkillProx"]),
   ("单次执行编译为 harness", ["Evo-Harness"]),
   ("技能库随 RL 共进化", ["SkillRL","Evolving-RL","Voyager"]),
 ]),
 ("安全治理\n（部署纪律）", "safety", [
   ("批准 / 回滚门控 · 资产版本化", ["MOSS","OpenLoopEvolve"]),
   ("可证伪发布门 · 常驻不变量", ["Falsifiable Release Gates"]),
   ("失败归因 · 轨迹 IR", ["HarnessFix","Co-Harness（HarnessCritic）"]),
   ("reward hacking 测量", ["HVTB","ARA","ASG-SI"]),
   ("生产自进化护栏", ["SESG（深信服 14/15）"]),
 ]),
 ("测量与宏观\n（外部视角）", "survey", [
   ("三份综述", ["TMLR 四维","Co-Evolution 三阶段","Coding Agents 三维"]),
   ("工业证据", ["Anthropic 进度报告","iCoder","Weng 总纲"]),
   ("宏观节奏 · σ 之争", ["METR 地平线","Erdil & Besiroglu","Forethought"]),
   ("自动研究谱系", ["AI Scientist","AlphaEvolve","ShinkaEvolve","ScientistOne","Why LLMs≠Scientists"]),
 ]),
]

def twidth(s, fs):
    return sum(fs if ord(c) > 0x2E80 else fs*0.56 for c in s)

def theme(dark):
    return dict(bg="#0b0f17" if dark else "#ffffff", fg="#e6edf3" if dark else "#111827",
                dim="#9aa4b2" if dark else "#6b7280", grid="#243040" if dark else "#e5e7eb",
                lane_alt="#101722" if dark else "#f8fafc", pill_txt="#0b0f17" if dark else "#111827")

def tint(hexcol, dark):
    r,g,b = int(hexcol[1:3],16), int(hexcol[3:5],16), int(hexcol[5:7],16)
    if dark: r,g,b = [min(255, int(v*0.55+255*0.45)) for v in (r,g,b)]
    else:    r,g,b = [int(v*0.16+255*0.84) for v in (r,g,b)]
    return f"#{r:02x}{g:02x}{b:02x}"

YEARS = [1965,1993,2001,2003,2008,2010,2013,2014,2023,2024,2025,2026]
YEAR_W = {1965:105,1993:105,2001:95,2003:130,2008:115,2010:105,2013:95,2014:150,2023:270,2024:330,2025:520,2026:1180}

def fig1(dark, years=None, year_w=None, title_suffix="", lanes=None):
    T = theme(dark)
    FS, PH, ROW, PADX = 13, 24, 30, 9
    LEFT, TOP = 300, 118
    years = years or YEARS; year_w = year_w or YEAR_W
    lanes = lanes or LANES
    xs = {}; x = LEFT
    WORKS_V = [w for w in WORKS if w[1] in years and w[3] in lanes]
    for y in years: xs[y] = x; x += year_w[y]
    W = x + 40
    def xpos(y,m): return xs[y] + (m-0.5)/12*year_w[y]
    lane_rows, placed = {}, {}
    for fam in lanes:
        items = sorted([w for w in WORKS_V if w[3]==fam], key=lambda w:(w[1],w[2],w[0]))
        rows_end, out = [], []
        for name,y,m,_,hd in items:
            label = ("★ " if hd else "") + name
            pw = twidth(label, FS) + 2*PADX
            px = xpos(y,m) - pw/2
            px = max(px, xs[y] + 2)
            if px + pw > xs[y] + year_w[y] - 2: px = xs[y] + year_w[y] - 2 - pw
            r = 0
            while r < len(rows_end) and px < rows_end[r] + 8: r += 1
            if r == len(rows_end): rows_end.append(0)
            rows_end[r] = px + pw
            out.append((label, px, pw, r, hd))
        lane_rows[fam] = max(1, len(rows_end)); placed[fam] = out
    lane_y, y0 = {}, TOP
    for fam in lanes:
        lane_y[fam] = y0; y0 += lane_rows[fam]*ROW + 14
    H = y0 + 70
    n_star = sum(1 for w in WORKS_V if w[4])
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="-apple-system,Helvetica,Arial,\'PingFang SC\',\'Noto Sans CJK SC\',sans-serif">',
         f'<rect width="{W}" height="{H}" fill="{T["bg"]}"/>',
         f'<text x="36" y="42" font-size="24" font-weight="700" fill="{T["fg"]}">Figure 1{title_suffix} · Recursive Self-Improvement：{len(WORKS_V)} 项工作的时间线（{years[0]}–{years[-1]}）</text>',
         f'<text x="36" y="68" font-size="13.5" fill="{T["dim"]}">按十个家族分泳道、按 arXiv 首版年月定位（非 arXiv 材料取发布月近似）；★ 为 {n_star} 份核心精读材料。1965-2014 为思想史，2015-2022 无收录（断轴），2025-2026 两年集中了 {sum(1 for w in WORKS_V if w[1]>=2025)} 项。</text>']
    for i,y in enumerate(years):
        if i % 2 == 0: o.append(f'<rect x="{xs[y]}" y="{TOP-10}" width="{year_w[y]}" height="{H-TOP-50}" fill="{T["lane_alt"]}"/>')
        o.append(f'<line x1="{xs[y]}" y1="{TOP-10}" x2="{xs[y]}" y2="{H-58}" stroke="{T["grid"]}" stroke-dasharray="3 4"/>')
        n = sum(1 for w in WORKS_V if w[1]==y)
        o.append(f'<text x="{xs[y]+year_w[y]/2:.0f}" y="{H-32}" font-size="15" font-weight="700" text-anchor="middle" fill="{T["fg"]}">{y}</text>')
        o.append(f'<text x="{xs[y]+year_w[y]/2:.0f}" y="{H-14}" font-size="11.5" text-anchor="middle" fill="{T["dim"]}">{n} works</text>')
    if 2014 in years and 2023 in years:  # axis break marker
        bx = xs[2023]
        o.append(f'<rect x="{bx-7}" y="{TOP-10}" width="14" height="{H-TOP-50}" fill="{T["bg"]}"/>')
        o.append(f'<path d="M{bx-4},{TOP-10} L{bx+4},{TOP+30} L{bx-4},{TOP+70}" fill="none" stroke="{T["dim"]}" stroke-width="2"/>')
        o.append(f'<text x="{bx}" y="{TOP-16}" font-size="11.5" text-anchor="middle" fill="{T["dim"]}">断轴 2015-2022</text>')
    if 2026 in years:
        bx = xpos(2026,8) - year_w[2026]/24; bw = year_w[2026]/12
        o.append(f'<rect x="{bx:.0f}" y="{TOP-10}" width="{bw:.0f}" height="{H-TOP-50}" fill="{FAM["eval"][1]}" opacity="{0.16 if dark else 0.08}"/>')
        o.append(f'<text x="{bx+bw/2:.0f}" y="{TOP-16}" font-size="12" font-weight="700" text-anchor="middle" fill="{FAM["eval"][1]}">2026-08 密集月</text>')
    for fam in lanes:
        col = FAM[fam][1]; ly = lane_y[fam]; lh = lane_rows[fam]*ROW
        o.append(f'<line x1="{LEFT}" y1="{ly+lh+7}" x2="{W-40}" y2="{ly+lh+7}" stroke="{T["grid"]}"/>')
        o.append(f'<rect x="36" y="{ly}" width="6" height="{lh}" rx="3" fill="{col}"/>')
        o.append(f'<text x="52" y="{ly+lh/2+5}" font-size="14.5" font-weight="700" fill="{T["fg"]}">{E(FAM[fam][0])}</text>')
        o.append(f'<text x="52" y="{ly+lh/2+22}" font-size="11.5" fill="{T["dim"]}">{len(placed[fam])} works</text>')
        for label,px,pw,r,hd in placed[fam]:
            py = ly + r*ROW + (ROW-PH)/2
            fill = col if hd else tint(col, dark); stroke = col
            txt = ("#ffffff" if hd else T["pill_txt"])
            o.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{PH}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="{1.6 if hd else 1}"/>')
            o.append(f'<text x="{px+pw/2:.1f}" y="{py+PH/2+4.5:.1f}" font-size="{FS}" text-anchor="middle" fill="{txt}"' + (' font-weight="700"' if hd else '') + f'>{E(label)}</text>')
    o.append('</svg>')
    return "\n".join(o), W, H

def fig2(dark, branches=None, title_suffix=""):
    T = theme(dark)
    TAX = [TAXONOMY[i] for i in branches] if branches else TAXONOMY
    FS_B, FS_S, FS_W = 15, 13.5, 12.5
    ROOT_W, BR_W, SUB_W = 200, 230, 250
    X_ROOT, X_BR, X_SUB, X_W = 40, 320, 620, 920
    W_MAX = 1380
    ROWH, GAP_SUB, GAP_BR = 24, 10, 22
    layout = []; y = 110
    for bl, fam, subs in TAX:
        sub_boxes = []
        for sl, works in subs:
            lines, cur = [], ""
            for w in works:
                cand = (cur + " · " + w) if cur else w
                if twidth(cand, FS_W) > (W_MAX - X_W - 20) and cur:
                    lines.append(cur); cur = w
                else: cur = cand
            lines.append(cur)
            h = max(ROWH, 18*len(lines) + 12)
            sub_boxes.append((sl, lines, y, h)); y += h + GAP_SUB
        y_top = sub_boxes[0][2]; y_bot = sub_boxes[-1][2] + sub_boxes[-1][3]
        layout.append((bl, fam, sub_boxes, y_top, y_bot)); y += GAP_BR
    H = y + 40; W = W_MAX + 40
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="-apple-system,Helvetica,Arial,\'PingFang SC\',\'Noto Sans CJK SC\',sans-serif">',
         f'<rect width="{W}" height="{H}" fill="{T["bg"]}"/>',
         f'<text x="36" y="42" font-size="24" font-weight="700" fill="{T["fg"]}">Figure 2{title_suffix} · 递归自改进的分类体系（Taxonomy）</text>',
         f'<text x="36" y="68" font-size="13.5" fill="{T["dim"]}">{len(TAX)} 个一级维度 · {sum(len(s) for _,_,s in TAX)} 个子类；"锚在哪"是本仓库独有的主轴——三份公开综述都没有这一列。同一工作可出现在多个维度（如 Continual Harness 既是文本层介质，又是免重置时间模式，锚为冻结 PRM）。</text>']
    root_y0, root_y1 = layout[0][3], layout[-1][4]
    ry = (root_y0 + root_y1)/2
    o.append(f'<rect x="{X_ROOT}" y="{ry-34}" width="{ROOT_W}" height="68" rx="10" fill="{T["fg"]}"/>')
    o.append(f'<text x="{X_ROOT+ROOT_W/2}" y="{ry-6}" font-size="16" font-weight="700" text-anchor="middle" fill="{T["bg"]}">递归自改进</text>')
    o.append(f'<text x="{X_ROOT+ROOT_W/2}" y="{ry+16}" font-size="12.5" text-anchor="middle" fill="{T["bg"]}">Recursive Self-Improvement</text>')
    xr = X_ROOT + ROOT_W; xm = (xr + X_BR)/2
    for bl, fam, subs, yt, yb in layout:
        col = FAM[fam][1]; bc = (yt+yb)/2; bh = max(56, yb-yt)
        o.append(f'<path d="M{xr},{ry} H{xm} V{bc} H{X_BR}" fill="none" stroke="{T["grid"]}" stroke-width="1.6"/>')
        o.append(f'<rect x="{X_BR}" y="{bc-bh/2:.1f}" width="{BR_W}" height="{bh:.1f}" rx="9" fill="{tint(col,dark)}" stroke="{col}" stroke-width="1.6"/>')
        lines = bl.split("\n")
        for i,ln in enumerate(lines):
            yy = bc + (i - (len(lines)-1)/2)*20 + 5
            o.append(f'<text x="{X_BR+BR_W/2}" y="{yy:.1f}" font-size="{FS_B if i==0 else 12.5}" font-weight="{700 if i==0 else 400}" text-anchor="middle" fill="{T["pill_txt"]}">{E(ln)}</text>')
        xb = X_BR + BR_W; xm2 = (xb + X_SUB)/2
        for sl, wl, sy, sh in subs:
            sc = sy + sh/2
            o.append(f'<path d="M{xb},{bc:.1f} H{xm2} V{sc:.1f} H{X_SUB}" fill="none" stroke="{col}" stroke-width="1.2" opacity="0.8"/>')
            o.append(f'<rect x="{X_SUB}" y="{sy}" width="{SUB_W}" height="{sh}" rx="6" fill="{T["bg"]}" stroke="{col}" stroke-width="1.2"/>')
            o.append(f'<text x="{X_SUB+12}" y="{sc+5:.1f}" font-size="{FS_S}" font-weight="600" fill="{T["fg"]}">{E(sl)}</text>')
            o.append(f'<line x1="{X_SUB+SUB_W}" y1="{sc:.1f}" x2="{X_W-8}" y2="{sc:.1f}" stroke="{col}" stroke-width="1" opacity="0.6"/>')
            for i,ln in enumerate(wl):
                yy = sy + 6 + 18*(i+1) - 4
                o.append(f'<text x="{X_W}" y="{yy:.1f}" font-size="{FS_W}" fill="{T["fg"]}">{E(ln)}</text>')
    o.append('</svg>')
    return "\n".join(o), W, H

if __name__ == "__main__":
    for dark, suf in [(False,""),(True,"_dark")]:
        s,w,h = fig1(dark); (OUT/f"fig1_timeline{suf}.svg").write_text(s, encoding="utf-8"); print(f"fig1{suf}: {w}x{h}")
        s,w,h = fig2(dark); (OUT/f"fig2_taxonomy{suf}.svg").write_text(s, encoding="utf-8"); print(f"fig2{suf}: {w}x{h}")
    # slide variants (1280px wide): timeline split by era; taxonomy split by branches
    s,w,h = fig1(True, years=[1965,1993,2001,2003,2008,2010,2013,2014,2023,2024,2025], year_w={1965:120,1993:120,2001:110,2003:150,2008:130,2010:120,2013:110,2014:170,2023:330,2024:430,2025:640}, title_suffix="a")
    (OUT/"fig1_timeline_dark_a.svg").write_text(s, encoding="utf-8"); print("fig1_dark_a:", w, h)
    s,w,h = fig1(True, years=[2026], year_w={2026:2200}, title_suffix="b")
    (OUT/"fig1_timeline_dark_b.svg").write_text(s, encoding="utf-8"); print("fig1_dark_b:", w, h)
    s,w,h = fig2(True, branches=[0,1,2], title_suffix="a"); (OUT/"fig2_taxonomy_dark_a.svg").write_text(s, encoding="utf-8"); print("fig2_dark_a:", w, h)
    s,w,h = fig2(True, branches=[3,4,5,6], title_suffix="b"); (OUT/"fig2_taxonomy_dark_b.svg").write_text(s, encoding="utf-8"); print("fig2_dark_b:", w, h)
    print("works:", len(WORKS))
