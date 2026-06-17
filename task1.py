import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(page_title="六轴机器人分析实践", layout="wide")

with st.sidebar:
    st.title("🤖 六轴协作机器人")
    st.markdown("**力学分析实践项目**")
    st.markdown("---")
    stage = st.radio(
        "分析阶段",
        ["📋 项目简介",
         "阶段1: 受力分析",
         "阶段2: 拉压与弯曲",
         "阶段3: 扭转分析",
         "阶段4: 组合变形",
         "阶段5: 稳定性评估",
         "📊 综合报告"]
    )
    st.markdown("---")
    st.caption("💡 点击各阶段，按顺序完成实践")

if "stage_progress" not in st.session_state:
    st.session_state.stage_progress = {
        "s1": False, "s2": False, "s3": False, "s4": False, "s5": False
    }
if "scores" not in st.session_state:
    st.session_state.scores = {}

def check_answer(user_input, correct_keywords, hint=""):
    if not user_input:
        return None, "请输入你的答案。"
    user_lower = user_input.lower()
    for kw in correct_keywords:
        if kw.lower() in user_lower:
            return True, "✅ 正确！" + hint
    return False, "❌ 再想想。" + hint

if stage == "📋 项目简介":
    st.title("🤖 六轴协作机器人 · 力学分析实践")
    st.markdown("""
    ### 📌 项目背景
    六轴协作机器人在工业自动化中广泛应用，其结构安全性至关重要。
    本实践项目将运用材料力学知识，对机器人的关键部件进行强度、刚度、稳定性分析。

    ### 🎯 项目目标
    通过本实践，你将能够：
    1. 对复杂工程结构进行受力分析与简化
    2. 综合运用拉压、弯曲、扭转、组合变形知识
    3. 完成强度校核、刚度校核、稳定校核
    4. 提出结构优化方案

    ### 🔧 分析对象
    六轴协作机器人关键部件：
    - 基座：分析固定螺栓（拉压+剪切）
    - 大臂：主要分析对象（压弯组合）
    - 关节1/2/3：传动轴扭转分析
    - 小臂：弯曲分析
    - 腕部/末端：受力传递

    ### 📋 分析流程
    问题定义 → 受力分析 → 内力计算 → 应力分析 → 强度校核 → 优化建议

    ### 📝 已知参数
    | 参数 | 数值 | 说明 |
    |------|------|------|
    | 最大负载 | 10 kg | 末端抓取重量 |
    | 大臂长度 | 500 mm | 主要受力臂 |
    | 大臂截面 | 80x60x5 mm | 空心矩形管 |
    | 材料 | 7075铝合金 | sigma_s=280MPa, E=70GPa |
    | 关节电机扭矩 | 50 N·m | 关节1驱动扭矩 |
    """)
    if st.button("🚀 开始实践"):
        st.success("已进入阶段1，请从侧边栏选择！")

elif stage == "阶段1: 受力分析":
    st.title("🔍 阶段1：受力分析")
    st.markdown("""
    ### 🎯 本阶段目标
    识别机器人最危险工况，分析大臂的受力，绘制受力简图。

    ### 💡 导师提示
    六轴机器人最危险工况通常是满载且大臂水平伸直状态。
    此时，末端负载对大臂根部的弯矩最大。
    """)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📝 任务1：识别危险工况")
        st.write("请描述：机器人哪个姿态下受力最大？为什么？")
        ans1 = st.text_area("你的回答", key="s1_1", height=80)
        if st.button("提交任务1", key="s1_1_btn"):
            result, msg = check_answer(ans1, ["水平", "伸直", "最大", "满载", "弯矩"])
            if result is True:
                st.success(msg)
                st.session_state.stage_progress["s1"] = True
            elif result is False:
                st.error(msg)
    with col2:
        st.markdown("### 📝 任务2：绘制受力简图")
        st.write("大臂根部受什么力？用文字描述（例如：弯矩M、轴力F、剪力Q）")
        ans2 = st.text_area("你的回答", key="s1_2", height=80)
        if st.button("提交任务2", key="s1_2_btn"):
            result, msg = check_answer(ans2, ["弯矩", "轴力", "剪力"])
            if result is True:
                st.success(msg)
            elif result is False:
                st.error(msg + " 提示：考虑大臂根部的弯矩、轴向压力和剪力")

    with st.expander("📖 查看参考答案"):
        st.markdown("""
        **任务1参考答案**：
        机器人大臂水平伸直且末端满载时，根部弯矩最大（M = F x L）

        **任务2参考答案**：
        大臂根部受到：弯矩M（由负载重力产生）、轴向压力F（由大臂自重+负载产生）、剪力Q（由重力分量产生）
        """)

elif stage == "阶段2: 拉压与弯曲":
    st.title("📐 阶段2：拉压与弯曲分析")
    st.markdown("""
    ### 🎯 本阶段目标
    计算大臂的轴力和弯矩，绘制内力图，计算最大正应力。

    ### 💡 导师提示
    大臂自重+末端负载 = 约 150 N（含自重），大臂长度 L = 0.5 m。
    大臂空心矩形截面：80x60x5 mm。
    大臂材料：7075铝合金，E = 70 GPa。
    """)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📝 任务1：计算轴力与弯矩")
        F_load = st.number_input("末端负载 (N)", value=150, step=10)
        L_arm = st.number_input("大臂长度 (m)", value=0.5, step=0.05)
        F_axial = st.number_input("轴力 F (N)", value=0, step=10, key="s2_f")
        M_max = st.number_input("最大弯矩 M (N·m)", value=0, step=5, key="s2_m")
        if st.button("提交任务1", key="s2_1_btn"):
            F_correct = F_load
            M_correct = F_load * L_arm
            score = 0
            if abs(F_axial - F_correct) < 10:
                score += 1
            if abs(M_max - M_correct) < 2:
                score += 1
            if score == 2:
                st.success(f"✅ 完全正确！F = {F_correct} N, M = {M_correct} N·m")
                st.session_state.stage_progress["s2"] = True
            else:
                st.warning(f"提示：轴力约 {F_correct} N，弯矩约 {M_correct} N·m，再试试！")
        st.markdown("---")
        st.markdown("### 📝 任务2：计算最大正应力")
        b = st.number_input("截面宽 b (mm)", value=80, step=5)
        h = st.number_input("截面高 h (mm)", value=60, step=5)
        t = st.number_input("壁厚 t (mm)", value=5, step=1)
        sigma_input = st.number_input("最大正应力 sigma_max (MPa)", value=0.0, step=0.5, key="s2_sigma")
        if st.button("提交任务2", key="s2_2_btn"):
            A = b*h - (b-2*t)*(h-2*t)
            I = (b*h**3 - (b-2*t)*(h-2*t)**3) / 12
            W = I / (h/2)
            sigma_correct = (F_load/A + M_correct/W) / 1e6
            if abs(sigma_input - sigma_correct) < 2:
                st.success(f"✅ 正确！sigma_max ≈ {sigma_correct:.1f} MPa")
            else:
                st.warning(f"提示：sigma = F/A + M/W，约 {sigma_correct:.1f} MPa")
    with col2:
        st.markdown("### 📊 内力图")
        x_plot = np.linspace(0, 0.5, 50)
        M_plot = F_load * x_plot
        F_plot = np.ones_like(x_plot) * F_load
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                           subplot_titles=("弯矩图", "轴力图"))
        fig.add_trace(go.Scatter(x=x_plot, y=M_plot, mode='lines',
                                 line=dict(color='red', width=3), name='弯矩'),
                     row=1, col=1)
        fig.add_trace(go.Scatter(x=x_plot, y=F_plot, mode='lines',
                                 line=dict(color='blue', width=3), name='轴力'),
                     row=2, col=1)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

elif stage == "阶段3: 扭转分析":
    st.title("🔄 阶段3：扭转分析")
    st.markdown("""
    ### 🎯 本阶段目标
    分析机器人关节传动轴的扭转问题，计算切应力和扭转角。

    ### 💡 导师提示
    关节1驱动扭矩 T = 50 N·m，传动轴直径 d = 30 mm。
    轴材料：40Cr钢，G = 80 GPa，L = 200 mm。
    """)
    col1, col2 = st.columns(2)
    with col1:
        T_input = st.number_input("关节扭矩 T (N·m)", value=50, step=5)
        d_input = st.number_input("轴直径 d (mm)", value=30, step=2)
        L_input = st.number_input("轴长 L (mm)", value=200, step=10)
        st.markdown("### 📝 任务1：计算最大切应力")
        tau_input = st.number_input("最大切应力 tau_max (MPa)", value=0.0, step=0.1, key="s3_tau")
        if st.button("提交任务1", key="s3_1_btn"):
            J = np.pi * (d_input/1000)**4 / 32
            tau_correct = T_input * (d_input/2000) / J / 1e6
            if abs(tau_input - tau_correct) < 1:
                st.success(f"✅ 正确！tau_max ≈ {tau_correct:.1f} MPa")
                st.session_state.stage_progress["s3"] = True
            else:
                st.warning(f"提示：tau = T*rho/J，rho = d/2，约 {tau_correct:.1f} MPa")
        st.markdown("### 📝 任务2：计算扭转角")
        phi_input = st.number_input("扭转角 phi (度)", value=0.0, step=0.01, key="s3_phi")
        if st.button("提交任务2", key="s3_2_btn"):
            J = np.pi * (d_input/1000)**4 / 32
            phi_correct = T_input * (L_input/1000) / (80e9 * J) * 180 / np.pi
            if abs(phi_input - phi_correct) < 0.05:
                st.success(f"✅ 正确！phi ≈ {phi_correct:.2f}度")
            else:
                st.warning(f"提示：phi = TL/GJ，约 {phi_correct:.2f}度")
    with col2:
        r = np.linspace(0, d_input/2, 50)
        J = np.pi * (d_input/1000)**4 / 32
        tau = T_input * (r/1000) / J / 1e6
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=r, y=tau, mode='lines', name='切应力分布',
                                 fill='tozeroy', line=dict(color='orange', width=3)))
        fig.update_layout(title="切应力沿半径分布", xaxis_title="半径 (mm)", yaxis_title="切应力 (MPa)", height=350)
        st.plotly_chart(fig, use_container_width=True)

elif stage == "阶段4: 组合变形":
    st.title("⚙️ 阶段4：组合变形与强度校核")
    st.markdown("""
    ### 🎯 本阶段目标
    大臂同时受压弯组合，选择强度理论进行校核，判断是否安全。

    ### 💡 导师提示
    大臂材料7075铝合金，sigma_s = 280 MPa，安全系数 n = 2。
    从前面阶段可知：sigma_axial = 0.12 MPa，sigma_bending = 3.18 MPa，tau = 9.4 MPa。
    """)
    col1, col2 = st.columns(2)
    with col1:
        sigma_axial = st.number_input("轴向应力 sigma (MPa)", value=0.12, step=0.01, format="%.2f")
        sigma_bending = st.number_input("弯曲应力 sigma_b (MPa)", value=3.18, step=0.01, format="%.2f")
        tau = st.number_input("切应力 tau (MPa)", value=9.4, step=0.1)
        st.markdown("### 📝 任务1：选择强度理论")
        theory = st.selectbox("哪个强度理论最适合？",
                             ["第一强度理论", "第二强度理论", "第三强度理论", "第四强度理论"])
        if st.button("提交任务1", key="s4_1_btn"):
            if "第四" in theory:
                st.success("✅ 正确！大臂为塑性材料（铝合金），应用第四强度理论（畸变能理论）")
                st.session_state.stage_progress["s4"] = True
            else:
                st.warning("提示：大臂是塑性材料，应用第四强度理论。")
        st.markdown("---")
        st.markdown("### 📝 任务2：计算等效应力")
        sigma_r4_input = st.number_input("等效应力 sigma_r4 (MPa)", value=0.0, step=0.1, key="s4_sigma")
        if st.button("提交任务2", key="s4_2_btn"):
            sigma_total = sigma_axial + sigma_bending
            sigma_r4 = np.sqrt(sigma_total**2 + 3*tau**2)
            if abs(sigma_r4_input - sigma_r4) < 1:
                st.success(f"✅ 正确！sigma_r4 = {sigma_r4:.1f} MPa，远小于许用应力 140 MPa，安全！")
            else:
                st.warning(f"提示：sigma_r4 = sqrt(sigma^2 + 3*tau^2)，约 {sigma_r4:.1f} MPa")
    with col2:
        y = np.linspace(-30, 30, 50)
        z = np.linspace(-40, 40, 50)
        Y, Z = np.meshgrid(y, z)
        sigma = sigma_bending * (Y / 30) + sigma_axial
        fig = go.Figure(data=go.Heatmap(
            z=sigma, x=z, y=y,
            colorscale='RdYlBu_r', zmid=0,
            colorbar=dict(title="应力 (MPa)")
        ))
        fig.update_layout(title="大臂截面组合应力分布", height=350)
        st.plotly_chart(fig, use_container_width=True)

elif stage == "阶段5: 稳定性评估":
    st.title("📏 阶段5：稳定性评估与优化")
    st.markdown("""
    ### 🎯 本阶段目标
    评估大臂的压杆稳定性，判断是否可能失稳，提出结构优化建议。

    ### 💡 导师提示
    大臂可简化为悬臂压杆（一端固定、一端自由），mu = 2。
    已知：L = 0.5 m，E = 70 GPa，I = 0.71e6 mm^4。
    """)
    col1, col2 = st.columns(2)
    with col1:
        L_stab = st.number_input("大臂长度 L (m)", value=0.5, step=0.05)
        I_stab = st.number_input("惯性矩 I (mm^4)", value=0.71e6, step=0.01e6, format="%.2e")
        st.markdown("### 📝 任务1：计算临界力")
        P_cr_input = st.number_input("临界力 P_cr (kN)", value=0.0, step=0.1, key="s5_pcr")
        if st.button("提交任务1", key="s5_1_btn"):
            mu = 2
            P_cr = np.pi**2 * 70e9 * I_stab*1e-12 / (mu * L_stab)**2 / 1000
            if abs(P_cr_input - P_cr) < 5:
                st.success(f"✅ 正确！P_cr ≈ {P_cr:.1f} kN")
                st.session_state.stage_progress["s5"] = True
            else:
                st.warning(f"提示：悬臂压杆 mu=2，P_cr = pi^2EI/(mu*L)^2，约 {P_cr:.1f} kN")
        st.markdown("---")
        st.markdown("### 📝 任务2：优化建议")
        suggestion = st.text_area("如何提高大臂的稳定性？提出2-3条建议", height=100)
        if st.button("提交任务2", key="s5_2_btn"):
            if any(kw in suggestion.lower() for kw in ["截面", "惯性矩", "材料", "支撑", "长度"]):
                st.success("✅ 很好的思路！继续深入优化分析。")
            else:
                st.warning("提示：可以从增大截面惯性矩、更换材料、增加支撑点等角度思考。")
    with col2:
        x = np.linspace(0, 1, 100)
        y = 1 - np.cos(np.pi * x / 2)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x*L_stab, y=y, mode='lines',
                                 name='失稳模态', line=dict(color='purple', width=4)))
        fig.update_layout(title="大臂一阶失稳模态（悬臂压杆）",
                          xaxis_title="杆长 (m)", yaxis_title="横向位移 (归一化)", height=350)
        st.plotly_chart(fig, use_container_width=True)

elif stage == "📊 综合报告":
    st.title("📊 分析报告")
    progress = sum(st.session_state.stage_progress.values())
    st.progress(progress / 5)
    st.write(f"完成进度：{progress}/5 阶段")
    if progress < 5:
        st.warning("⚠️ 还有阶段未完成，请完成所有阶段后生成完整报告。")
    st.markdown("""
    ### 📝 六轴协作机器人大臂分析报告

    #### 1. 问题定义
    分析六轴协作机器人大臂在最危险工况（满载水平伸直）下的力学性能。

    #### 2. 受力分析
    - 大臂根部弯矩：M = 75 N·m
    - 大臂轴向压力：F = 150 N

    #### 3. 应力分析
    | 项目 | 数值 |
    |------|------|
    | 轴向应力 | 0.12 MPa |
    | 弯曲应力 | 3.18 MPa |
    | 切应力 | 9.4 MPa |
    | 等效应力 (sigma_r4) | 16.4 MPa |
    | 许用应力 | 140 MPa |
    | 结论 | 强度满足 |

    #### 4. 刚度分析
    - 最大挠度：约 0.02 mm（远小于允许值）
    - 结论：刚度满足

    #### 5. 稳定性分析
    - 欧拉临界力：P_cr = 49.1 kN
    - 实际压力：0.15 kN
    - 安全系数：327
    - 结论：稳定性满足

    #### 6. 结论与建议
    大臂在满载工况下强度、刚度、稳定性均满足要求。
    建议：
    - 可采用更轻量化设计
    - 优化截面形状可进一步减重
    """)
    if progress == 5:
        st.balloons()
        st.success("🎉 恭喜完成全部实践！")

st.markdown("---")
st.caption("🤖 六轴协作机器人力学分析实践 | 材料力学智能教学系统")