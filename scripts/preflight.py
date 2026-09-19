# -*- coding: utf-8 -*-
"""scripts/preflight.py —— 发文前一键快筛（anti-ai-foolish）。
用法: python scripts/preflight.py <文章.md>
流程: 剥信源 → 全规则扫描 → 硬门（冒号/破折号/直引号/概念引用腔/疑问句密度）→ Z分 → 人味弹药检查 → 判定 发/改/停。"""
import os, sys, io, json, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanner import scan, strip_body, kilo

ALLOWED_EXT = ('.md', '.txt', '.markdown')

def _safe_read(path):
    """校验输入路径：必须存在、必须是常规文件、扩展名白名单，防路径注入。"""
    p = os.path.abspath(os.path.realpath(path))
    if not os.path.isfile(p):
        raise SystemExit('输入不是有效文件: %s' % p)
    if os.path.splitext(p)[1].lower() not in ALLOWED_EXT:
        raise SystemExit('仅支持 %s 文件: %s' % (ALLOWED_EXT, p))
    return io.open(p, encoding='utf-8').read()

def preflight(path):
    text = _safe_read(path)
    body = strip_body(text)
    rep = scan(text)
    gates = []
    colon = body.count('：')
    gates.append(('冒号=0', colon == 0, f'{colon}处'))
    dash = body.count('——')
    gates.append(('破折号=0', dash == 0, f'{dash}处'))
    dq = body.count('"')
    gates.append(('直引号=0', dq == 0, f'{dq}处'))
    concept = len(re.findall(r'[“"][^”"]{2,7}[”"]', body)) / kilo(body)
    gates.append(('概念引用腔≤3/千字', concept <= 3, f'{concept:.1f}/千字'))
    q = body.count('？') + body.count('?')
    qd = q / kilo(body)
    gates.append(('疑问句≤3/千字', qd <= 3, f'{qd:.1f}/千字'))
    sec_titles = len(re.findall(r'^#{1,6} |[一二三四五六七八九十]+、', body, re.M))
    gates.append(('无小节标题', sec_titles == 0, f'{sec_titles}处'))
    humane_hits = len(rep['humane_hits'])
    gates.append(('人味弹药≥2类', humane_hits >= 2, f'{humane_hits}类命中'))
    # 篇内骨架比门：把正文按段落切成约1200字的块，算每块的论证指标 vs 叙事指标。
    # 若某块论证指标显著高于篇内叙事基准（概念词≥基准3倍 且 经历信号=0 且 块≥800字），
    # 标点手术救不了它——朱雀读的是骨架（z21实测：亲历骨架块0.40 / 概念骨架块0.63，六门全过仍疑似）。
    skel_warn = skeleton_check(body)
    gates.append(('篇内骨架比（无纯概念块）', not skel_warn, skel_warn or '各块骨架均衡'))
    passed = sum(1 for _, ok, _ in gates if ok)
    hard_ok = all(ok for name, ok, _ in gates if name != '篇内骨架比（无纯概念块）')
    if skel_warn and hard_ok:
        verdict = '⚠️ 标点已净但存在概念骨架块——需换骨架（挂人挂事），不是继续改标点'
    elif passed == len(gates) and rep['z_score'] < 0:
        verdict = '✅ 可发（朱雀切块复测后发布）'
    elif passed >= len(gates) - 2:
        verdict = '⚠️ 改后复检'
    else:
        verdict = '❌ 停下手术'
    print(f"# Preflight — {os.path.basename(path)}")
    print(f"正文 {rep['chars']} 字 | Z分 {rep['z_score']}（AI确认{rep['z_components']['AI确认命中']} − 人味确认{rep['z_components']['人味确认命中']}）")
    for name, ok, detail in gates:
        print(f"  {'✓' if ok else '✗'} {name}: {detail}")
    print(f"门通过 {passed}/{len(gates)} → {verdict}")
    return verdict


def skeleton_check(body):
    """篇内块间骨架对比。返回警告字符串（最重的概念块描述），均衡则返回 ''。
    论证指标 = 概念词密度（标准/系统/结构/符号/谱系/权力/审美/话语）+ 所以密度 + 设问自答
    叙事指标 = 经历我 + 亲历时间 + 直接引语 + 具体量词细节"""
    paras = [p.strip() for p in body.split('\n') if p.strip()]
    if not paras:
        return ''
    blocks, cur, size = [], [], 0
    for p in paras:
        cur.append(p); size += len(p)
        if size >= 1200:
            blocks.append('\n'.join(cur)); cur, size = [], 0
    if cur:
        blocks.append('\n'.join(cur))
    if len(blocks) < 2:
        return ''
    def metrics(t):
        k = max(len(t) / 1000, .3)
        arg = (sum(t.count(w) for w in ('标准', '系统', '结构', '符号', '谱系', '权力', '审美', '话语', '叙事', '语境')) / k
               + 2 * t.count('所以') / k
               + len(re.findall(r'[？?][^。]{0,20}(?:是|因为|答案)', t)) / k)
        nar = (len(re.findall(r'我(?:前几天|那天|把|写|走|看|越想|小时候|以前|刚刚)', t))
               + len(re.findall(r'半小时后|那天|前几天|当时', t))
               + len(re.findall(r'告诉我|说[：，]', t))
               + len(re.findall(r'[0-9一二三四五六七八九十]+(?:分钟|米|号|岁|个字|年)', t))) / k
        return arg, nar
    ms = [metrics(b) for b in blocks]
    import statistics as _st
    nar_med = _st.median([m[1] for m in ms]) if ms else 0
    worst, worst_desc = None, ''
    for i, (arg, nar) in enumerate(ms):
        if len(blocks[i]) >= 800 and arg >= 5.0 and nar <= max(2.0, nar_med):
            desc = f'第{i+1}块（{len(blocks[i])}字）：论证指标{arg:.1f}/千字、经历信号{nar:.1f}/千字——概念骨架块'
            if worst is None or arg > worst:
                worst, worst_desc = arg, desc
    return worst_desc

if __name__ == '__main__':
    preflight(sys.argv[1])
