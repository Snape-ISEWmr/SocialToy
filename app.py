# -*- coding: utf-8 -*-
"""
情绪裂变标签测试网站 - Streamlit版本
支持国内多端访问，简洁美观的极简性冷淡风格
"""

import streamlit as st
from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont
import os
import requests
import json

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="人格测试",
    page_icon="🎭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==================== 自定义CSS - 极简性冷淡风格（优化版）====================
st.markdown("""
<style>
    /* 全局样式 - 小清新渐变背景 */
    .stApp {
        background: linear-gradient(135deg, #fdfbf7 0%, #f8f9fa 100%);
    }

    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}

    /* 沉浸式模式 - 隐藏所有导航 */
    .immersive-mode #MainMenu,
    .immersive-mode footer,
    .immersive-mode header,
    .immersive-mode .stDeployButton {
        display: none !important;
    }

    /* 沉浸式模式 - 全屏容器 */
    .immersive-mode .main .block-container {
        max-width: 100%;
        padding: 1rem;
    }

    /* 主容器优化 */
    .main .block-container {
        padding-top: 4rem;
        padding-bottom: 4rem;
        max-width: 800px;
    }

    /* 标题样式 - 小清新 */
    .main-title {
        font-size: clamp(1.875rem, 5vw, 3rem);
        font-weight: 400;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 4rem;
        line-height: 1.4;
        letter-spacing: 0.02em;
    }

    /* 副标题/描述文字 - 小清新 */
    .subtitle {
        font-size: 0.875rem;
        color: #95a5a6;
        text-align: center;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 1rem;
        font-weight: 500;
    }

    /* 按钮容器 */
    .button-container {
        display: flex;
        flex-direction: column;
        gap: 1.25rem;
        width: 100%;
        max-width: 500px;
        margin: 0 auto;
    }

    /* 按钮样式 - 小清新渐变圆角 + 动画 */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
        border: none;
        padding: 1.25rem 2rem;
        font-size: 1rem;
        font-weight: 500;
        letter-spacing: 0.02em;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }

    .stButton>button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }

    .stButton>button:hover::before {
        left: 100%;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #5568d3 0%, #6b3d8f 100%);
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    .stButton>button:active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        transform: translateY(0) scale(0.98);
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.2);
    }

    /* 轮廓按钮 - 小清新 */
    .outline-button .stButton>button {
        background: #ffffff;
        color: #667eea;
        border: 2px solid #667eea;
    }

    .outline-button .stButton>button:hover {
        background: #f8f9ff;
        border-color: #5568d3;
        color: #5568d3;
    }

    /* 进度条样式 - 小清新圆角 */
    .progress-container {
        width: 100%;
        margin-bottom: 3rem;
    }

    .progress-bar {
        width: 100%;
        height: 6px;
        background-color: #e9ecef;
        border-radius: 3px;
    }

    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 3px;
        transition: width 0.3s ease;
    }

    /* 结果标签样式 - 小清新 + 动画 */
    .result-label {
        font-size: clamp(2.5rem, 8vw, 4rem);
        font-weight: 500;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 0.02em;
        line-height: 1.2;
        animation: bounceIn 0.6s ease-out;
    }

    /* 结果标签动画 */
    @keyframes bounceIn {
        0% {
            opacity: 0;
            transform: scale(0.3);
        }
        50% {
            opacity: 1;
            transform: scale(1.05);
        }
        70% {
            transform: scale(0.9);
        }
        100% {
            transform: scale(1);
        }
    }

    /* 评价文字样式 - 小清新 + 渐入动画 */
    .evaluation-text {
        font-size: 1rem;
        color: #495057;
        text-align: center;
        line-height: 1.8;
        margin-bottom: 2rem;
        font-weight: 400;
        letter-spacing: 0.01em;
        animation: fadeInUp 0.5s ease-out;
        animation-fill-mode: both;
    }

    /* 评价文字动画 - 延迟 */
    .evaluation-text:nth-child(1) { animation-delay: 0.2s; }
    .evaluation-text:nth-child(2) { animation-delay: 0.4s; }
    .evaluation-text:nth-child(3) { animation-delay: 0.6s; }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* 图片容器 + 动画 */
    .image-container {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
        animation: rotateIn 0.8s ease-out;
    }

    @keyframes rotateIn {
        from {
            opacity: 0;
            transform: rotate(-180deg) scale(0.5);
        }
        to {
            opacity: 1;
            transform: rotate(0) scale(1);
        }
    }

    /* 占比文字样式 - 小清新标签 + 脉冲动画 */
    .percentage-text {
        font-size: 0.875rem;
        color: #adb5bd;
        text-align: center;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 3rem;
        font-weight: 500;
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.6;
        }
    }

    /* 底部提示 - 小清新 */
    .footer-text {
        font-size: 0.75rem;
        color: #ced4da;
        text-align: center;
        letter-spacing: 0.03em;
        margin-top: 4rem;
    }

    /* 选项按钮容器 */
    .options-container {
        display: flex;
        flex-direction: column;
        gap: 0.875rem;
        width: 100%;
        max-width: 500px;
        margin: 0 auto;
    }

    /* 题目文字 - 小清新 */
    .question-text {
        font-size: clamp(1.25rem, 4vw, 1.75rem);
        font-weight: 400;
        color: #343a40;
        text-align: center;
        margin-bottom: 3rem;
        line-height: 1.6;
        letter-spacing: 0.01em;
    }

    /* 分割线 - 小清新 */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #dee2e6 50%, transparent 100%);
        margin: 3rem 0;
    }

    /* 图片容器 */
    .image-container {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
    }

    /* 标签图标样式 */
    .test-icon {
        font-size: 2rem;
        margin-right: 0.75rem;
    }

    /* 响应式调整 - 移动端优化 */
    @media (max-width: 640px) {
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .main-title {
            margin-bottom: 2.5rem;
            font-size: clamp(1.5rem, 6vw, 2.5rem);
        }

        .subtitle {
            font-size: 0.75rem;
            margin-bottom: 0.75rem;
        }

        .button-container {
            gap: 1rem;
        }

        .stButton>button {
            padding: 1rem 1.5rem;
            font-size: 0.9375rem;
            border-radius: 10px;
        }

        .question-text {
            font-size: clamp(1.125rem, 5vw, 1.5rem);
            margin-bottom: 2rem;
            line-height: 1.7;
        }

        .options-container {
            gap: 0.75rem;
        }

        .progress-container {
            margin-bottom: 2rem;
        }

        .progress-bar {
            height: 4px;
        }

        .result-label {
            font-size: clamp(2rem, 10vw, 3.5rem);
            margin-bottom: 1.5rem;
        }

        .evaluation-text {
            font-size: 0.9375rem;
            margin-bottom: 1.5rem;
        }

        .divider {
            margin: 2rem 0;
        }

        .footer-text {
            font-size: 0.6875rem;
            margin-top: 2rem;
        }
    }

    /* 超小屏幕优化 */
    @media (max-width: 375px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .main-title {
            font-size: clamp(1.25rem, 7vw, 2rem);
        }

        .stButton>button {
            padding: 0.875rem 1.25rem;
            font-size: 0.875rem;
        }
    }

    /* 平板优化 */
    @media (min-width: 641px) and (max-width: 1024px) {
        .main .block-container {
            max-width: 700px;
        }
    }

    /* 沉浸式测试页面样式 */
    .immersive-test {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, #fdfbf7 0%, #f8f9fa 100%);
        z-index: 1000;
        overflow-y: auto;
    }

    /* 趣味引导按钮动画 */
    .fun-button {
        animation: bounce 2s infinite;
    }

    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-20px);
        }
        60% {
            transform: translateY(-10px);
        }
    }

    /* 旋转箭头动画 */
    .arrow-bounce {
        animation: arrowDown 1.5s ease-in-out infinite;
    }

    @keyframes arrowDown {
        0%, 100% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
        }
        50% {
            transform: translateY(10px) rotate(10deg);
            opacity: 0.5;
        }
    }

    /* 脉冲光环动画 */
    .pulse-ring {
        position: relative;
    }

    .pulse-ring::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 100%;
        height: 100%;
        background: inherit;
        border-radius: inherit;
        transform: translate(-50%, -50%);
        animation: pulseRing 2s ease-out infinite;
        opacity: 0;
    }

    @keyframes pulseRing {
        0% {
            transform: translate(-50%, -50%) scale(1);
            opacity: 0.8;
        }
        100% {
            transform: translate(-50%, -50%) scale(1.5);
            opacity: 0;
        }
    }

    /* 浮动动画 */
    .float {
        animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-10px);
        }
    }

    /* 闪烁动画 */
    .sparkle {
        animation: sparkle 1.5s ease-in-out infinite;
    }

    @keyframes sparkle {
        0%, 100% {
            opacity: 1;
            transform: scale(1);
        }
        50% {
            opacity: 0.5;
            transform: scale(1.2);
        }
    }

    /* 其他测试按钮样式 */
    .other-test-btn {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        font-size: 1rem;
        font-weight: 500;
        border-radius: 12px;
        cursor: pointer;
        width: 100%;
        max-width: 500px;
        box-shadow: 0 4px 15px rgba(240, 87, 108, 0.3);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }

    .other-test-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(240, 87, 108, 0.4);
    }

    .other-test-btn:active {
        transform: translateY(0);
        box-shadow: 0 2px 10px rgba(240, 87, 108, 0.3);
    }

    /* 其他测试按钮特殊样式 */
    [data-testid*="other_test_"] > button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        color: white !important;
        border: none !important;
        padding: 1rem 2rem !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(240, 87, 108, 0.3) !important;
        transition: all 0.3s ease !important;
        margin-bottom: 1rem !important;
    }

    [data-testid*="other_test_"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(240, 87, 108, 0.4) !important;
    }

    [data-testid*="other_test_"] > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 10px rgba(240, 87, 108, 0.3) !important;
    }
</style>

<script>
    // 处理其他测试按钮点击
    document.querySelectorAll('.other-test-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const testType = this.getAttribute('data-test');
            if (testType) {
                // 更新URL参数
                const url = new URL(window.location);
                url.searchParams.set('test', testType);
                window.history.pushState({}, '', url);
                // 刷新页面
                window.location.reload();
            }
        });
    });
</script>
""", unsafe_allow_html=True)

# ==================== 测试数据 ====================
TEST_DATA = {
    "worker": {
        "title": "打工人摸鱼人格测试",
        "icon": "🏢",
        "questions": [
            {
                "text": "周一早上9点，你刚到公司，第一件事做什么？",
                "options": [
                    {"text": "立刻打开电脑，列出今天的待办事项", "type": "A"},
                    {"text": "先去茶水间泡杯咖啡，顺便和同事寒暄", "type": "B"},
                    {"text": "打开手机刷10分钟朋友圈再开工", "type": "C"},
                    {"text": "发个朋友圈：新的一周，加油打工人", "type": "D"}
                ]
            },
            {
                "text": "开会时领导在讲PPT，你通常在做什么？",
                "options": [
                    {"text": "认真做笔记，生怕漏掉任何细节", "type": "A"},
                    {"text": "假装在记笔记，实际在偷偷回微信", "type": "D"},
                    {"text": "神游太虚，思考中午吃什么", "type": "C"},
                    {"text": "适时点头附和，演技堪比影帝", "type": "B"}
                ]
            },
            {
                "text": "下午3点，同事约你去茶水间摸鱼，你会？",
                "options": [
                    {"text": "拒绝，手头还有工作没做完", "type": "A"},
                    {"text": "欣然前往，摸鱼是打工人的基本权利", "type": "C"},
                    {"text": "去是可以去，但5分钟就回来", "type": "B"},
                    {"text": "不仅去，还顺便带上了零食和八卦", "type": "D"}
                ]
            },
            {
                "text": "快到下班时间，老板突然布置新任务，你的反应是？",
                "options": [
                    {"text": "二话不说，加班搞定", "type": "A"},
                    {"text": "嘴上答应，明天再做", "type": "B"},
                    {"text": "假装没看到消息，准时溜走", "type": "C"},
                    {"text": "先发个朋友圈控诉，然后默默加班", "type": "D"}
                ]
            },
            {
                "text": "午休时间到了，你通常怎么度过？",
                "options": [
                    {"text": "边吃饭边看工作文档，争分夺秒", "type": "A"},
                    {"text": "准时吃饭，准时午睡，雷打不动", "type": "B"},
                    {"text": "刷短视频刷到忘记时间", "type": "C"},
                    {"text": "和同事组队开黑，午休就是我的战场", "type": "D"}
                ]
            },
            {
                "text": "看到同事在朋友圈晒加班，你的想法是？",
                "options": [
                    {"text": "向优秀的人学习，今晚我也加班", "type": "A"},
                    {"text": "内心毫无波澜，甚至想点个赞", "type": "B"},
                    {"text": "呵呵，表演型加班，谁不会啊", "type": "D"},
                    {"text": "关掉朋友圈，继续摸我的鱼", "type": "C"}
                ]
            },
            {
                "text": "周末收到工作群消息，你会怎么处理？",
                "options": [
                    {"text": "秒回，工作消息不能等", "type": "A"},
                    {"text": "已读不回，周一再说", "type": "C"},
                    {"text": "隔两小时再回，显得我很忙", "type": "D"},
                    {"text": "看情况，真急就回，不急就装死", "type": "B"}
                ]
            },
            {
                "text": "公司团建活动，你的参与度如何？",
                "options": [
                    {"text": "积极组织，团建是增进团队感情的好机会", "type": "A"},
                    {"text": "佛系参与，去不去都行", "type": "B"},
                    {"text": "能不去就不去，社恐发作", "type": "C"},
                    {"text": "必须去！免费吃喝谁不去谁傻", "type": "D"}
                ]
            },
            {
                "text": "遇到不懂的工作问题，你通常怎么做？",
                "options": [
                    {"text": "自己查资料研究，绝不麻烦别人", "type": "A"},
                    {"text": "直接问同事，效率第一", "type": "B"},
                    {"text": "先放一放，说不定明天就懂了", "type": "C"},
                    {"text": "问是会问的，但先夸对方一波", "type": "D"}
                ]
            },
            {
                "text": "如果给你一个月带薪假期，你最想做什么？",
                "options": [
                    {"text": "报个培训班提升自己，假期不能浪费", "type": "A"},
                    {"text": "在家躺平，能不动就不动", "type": "C"},
                    {"text": "出去旅游，朋友圈素材不能断", "type": "D"},
                    {"text": "先睡三天三夜，然后再做打算", "type": "B"}
                ]
            }
        ],
        "results": {
            "A": {
                "label": "卷王之王",
                "percentage": "5%",
                "evaluations": [
                    "你是天选的卷王，工作就是你的信仰，加班就是你的朝圣。",
                    "别人摸鱼你加班，别人睡觉你复盘，你的KPI永远比体重涨得快。",
                    "建议去医院挂个号——不是身体有病，是脑子有病。"
                ]
            },
            "B": {
                "label": "摸鱼达人",
                "percentage": "18%",
                "evaluations": [
                    "你是摸鱼界的教科书，工作摸鱼两不误，效率与快乐并存。",
                    "你的摸鱼不是偷懒，是艺术——精准卡点，从不翻车。",
                    "同事以为你在努力，老板以为你在加班，只有你知道真相。"
                ]
            },
            "C": {
                "label": "躺平大师",
                "percentage": "25%",
                "evaluations": [
                    "你已经参透了打工的本质——给多少钱干多少活，多一分都是亏。",
                    "你的工位就是你的禅修场，手机就是你的木鱼，刷屏就是你的念经。",
                    "佛系不是你的态度，是你的战略——躺得越平，子弹越打不着。"
                ]
            },
            "D": {
                "label": "表演型选手",
                "percentage": "15%",
                "evaluations": [
                    "你是职场奥斯卡影帝，表演努力比真正努力还累。",
                    "朋友圈加班照、深夜打卡、工位绿植——你的努力，必须被看见。",
                    "其实你摸鱼比谁都狠，只是演技太好，连自己都信了。"
                ]
            },
            "AB": {
                "label": "职场老油条",
                "percentage": "12%",
                "evaluations": [
                    "你深谙职场潜规则，该卷的时候卷，该摸的时候摸，进退自如。",
                    "领导面前你是劳模，同事面前你是兄弟，谁都不得罪。",
                    "你的生存技能点满了，但你的良心——好像也磨没了。"
                ]
            },
            "AC": {
                "label": "打工皇帝",
                "percentage": "8%",
                "evaluations": [
                    "你混日子的功力登峰造极，但活干得比谁都漂亮——这就是天赋。",
                    "你从不加班，但绩效永远中等偏上，领导也挑不出毛病。",
                    "你不是在打工，你是在演一出「看似摸鱼实则靠谱」的戏。"
                ]
            },
            "BD": {
                "label": "隐形人",
                "percentage": "10%",
                "evaluations": [
                    "你的存在感低到令人发指，开会没人点你名，团建没人叫你。",
                    "但这也意味着——没人找你麻烦，没人给你加活，完美隐身。",
                    "你不是不合群，你只是把社交电量省下来用来摸鱼了。"
                ]
            },
            "CD": {
                "label": "佛系打工人",
                "percentage": "7%",
                "evaluations": [
                    "你对一切佛系对待——升职加薪随缘，加班摸鱼随缘，连生气都随缘。",
                    "你的座右铭是「都行、可以、没关系」，三个词走天下。",
                    "别人在卷，你在看；别人在争，你在笑——笑他们太年轻。"
                ]
            }
        }
    },
    "love": {
        "title": "恋爱脑等级测试",
        "icon": "❤️",
        "questions": [
            {"text": "喜欢的人已读不回，你会？", "options": [
                {"text": "继续发消息，万一对方只是忙", "type": "A"},
                {"text": "等半小时再发一条，保持矜持", "type": "B"},
                {"text": "放下手机，该干嘛干嘛", "type": "C"},
                {"text": "开始分析对方每条消息的潜台词", "type": "D"}
            ]},
            {"text": "约会时对方迟到了30分钟，你？", "options": [
                {"text": "没关系，等再久也值得", "type": "A"},
                {"text": "有点不爽但不会说出来", "type": "B"},
                {"text": "直接走人，不尊重我时间的人不值得", "type": "C"},
                {"text": "发朋友圈暗示，让对方看到", "type": "D"}
            ]},
            {"text": "恋爱后你的社交圈？", "options": [
                {"text": "基本只剩对象了，其他人都无所谓", "type": "A"},
                {"text": "减少了但还维持着几个好友", "type": "B"},
                {"text": "该聚聚该玩玩，恋爱不能影响社交", "type": "C"},
                {"text": "表面维持社交，心里只想和对象待着", "type": "D"}
            ]},
            {"text": "对象说「我没事」，你信吗？", "options": [
                {"text": "不信！一定有事！追问到底！", "type": "A"},
                {"text": "半信半疑，但不敢多问", "type": "B"},
                {"text": "信，说没事就是没事", "type": "C"},
                {"text": "不信，但假装信，暗中观察", "type": "D"}
            ]},
            {"text": "分手后你的状态？", "options": [
                {"text": "天塌了，世界末日，活不下去了", "type": "A"},
                {"text": "哭三天三夜，然后慢慢走出来", "type": "B"},
                {"text": "难过归难过，日子还得过", "type": "C"},
                {"text": "表面云淡风轻，深夜疯狂emo", "type": "D"}
            ]},
            {"text": "你会为对象改变自己吗？", "options": [
                {"text": "会！爱一个人就要变成对方喜欢的样子", "type": "A"},
                {"text": "小习惯可以改，底线不能动", "type": "B"},
                {"text": "不会，爱我就要爱真实的我", "type": "C"},
                {"text": "嘴上说不会，实际已经在改了", "type": "D"}
            ]},
            {"text": "对象和异性同事走得近，你？", "options": [
                {"text": "醋坛子打翻，必须问清楚", "type": "A"},
                {"text": "心里不舒服，但装作不在意", "type": "B"},
                {"text": "正常社交而已，不用大惊小怪", "type": "C"},
                {"text": "表面淡定，背地里翻对方朋友圈", "type": "D"}
            ]},
            {"text": "纪念日忘了准备礼物，你？", "options": [
                {"text": "自责到不行，立刻补上双倍", "type": "A"},
                {"text": "赶紧补救，能补多少补多少", "type": "B"},
                {"text": "道个歉就好，不是什么大事", "type": "C"},
                {"text": "先发个红包，再想怎么圆场", "type": "D"}
            ]},
            {"text": "你手机里有对象多少照片？", "options": [
                {"text": "几百张，相册全是对方", "type": "A"},
                {"text": "几十张，精选了一些", "type": "B"},
                {"text": "几张合照而已", "type": "C"},
                {"text": "不多，但截图保存了很多聊天记录", "type": "D"}
            ]},
            {"text": "你觉得恋爱中最重要的是？", "options": [
                {"text": "全心全意付出，爱就要轰轰烈烈", "type": "A"},
                {"text": "互相理解和包容", "type": "B"},
                {"text": "保持独立，互相尊重", "type": "C"},
                {"text": "感觉对了，其他都不重要", "type": "D"}
            ]}
        ],
        "results": {
            "A": {"label": "重度恋爱脑", "percentage": "12%", "evaluations": [
                "你的恋爱脑已经晚期了，恋爱就是你的氧气，没对象就窒息。",
                "你的世界围着对方转，连吃饭都要先问对方吃了没。",
                "建议把手机放下，出门走走——世界很大，不只有一个人。"
            ]},
            "B": {"label": "轻度恋爱脑", "percentage": "28%", "evaluations": [
                "你有恋爱脑的倾向，但好在还有一丝理智在苦苦支撑。",
                "你会为对方改变，但还没到失去自我的地步——暂时。",
                "小心，你离重度只差一个「已读不回」的距离。"
            ]},
            "C": {"label": "理智型选手", "percentage": "20%", "evaluations": [
                "你的恋爱脑已经被理智成功切除，堪称情感界的无影灯。",
                "你爱归爱，但底线清晰，原则明确，绝不恋爱脑上头。",
                "对方既庆幸你清醒，又遗憾你不够疯狂——人就是这么矛盾。"
            ]},
            "D": {"label": "闷骚型恋爱脑", "percentage": "15%", "evaluations": [
                "你表面云淡风轻，内心戏比韩剧还多。",
                "嘴上说「没事」，心里已经演完了一整部狗血剧。",
                "你的恋爱脑不是没有，只是藏得太深——连你自己都骗了。"
            ]},
            "AB": {"label": "间歇性恋爱脑", "percentage": "10%", "evaluations": [
                "你的恋爱脑是阵发性的，平时清醒，一上头就失控。",
                "上一秒「我要独立」，下一秒「你在干嘛为什么不回我」。",
                "你是最危险的那种——因为你总以为自己很理智。"
            ]},
            "AC": {"label": "双面人", "percentage": "5%", "evaluations": [
                "你在恋爱和自我之间反复横跳，精分得令人心疼。",
                "一半想为爱奋不顾身，一半想转身就跑。",
                "你的内心OS：我到底要当恋爱脑还是事业脑？答案是：都不行。"
            ]},
            "BD": {"label": "暗恋型选手", "percentage": "6%", "evaluations": [
                "你的恋爱脑全用在了暗恋上，正主根本不知道。",
                "对方一个眼神你能解读出三层含义，其实人家只是近视。",
                "你的恋爱是独角戏，观众只有你自己——和你的备忘录。"
            ]},
            "CD": {"label": "佛系恋爱人", "percentage": "4%", "evaluations": [
                "你对恋爱的态度：有也行，没有也行，随缘吧。",
                "别人在追爱，你在追剧；别人在emo，你在睡觉。",
                "你不是不渴望爱情，你只是懒得主动——连心动都嫌累。"
            ]}
        }
    },
    "holiday": {
        "title": "五一假期人格测试",
        "icon": "🏖️",
        "questions": [
            {"text": "五一放假前最后一小时，你在？", "options": [
                {"text": "还在认真工作，站好最后一班岗", "type": "A"},
                {"text": "已经在规划假期行程了", "type": "B"},
                {"text": "工位上坐着，灵魂已经到家了", "type": "C"},
                {"text": "发朋友圈倒计时，仪式感拉满", "type": "D"}
            ]},
            {"text": "五一你选择怎么过？", "options": [
                {"text": "报个学习班，假期是弯道超车的好机会", "type": "A"},
                {"text": "出去旅游，朋友圈不能输", "type": "B"},
                {"text": "在家躺5天，能不下床就不下", "type": "C"},
                {"text": "前两天躺，后两天玩，最后一天焦虑", "type": "D"}
            ]},
            {"text": "景点人山人海，你？", "options": [
                {"text": "来都来了，挤一挤又何妨", "type": "A"},
                {"text": "拍照打卡就走，绝不恋战", "type": "B"},
                {"text": "看到人多直接掉头回家", "type": "C"},
                {"text": "边挤边发朋友圈：人好多啊好开心（假的）", "type": "D"}
            ]},
            {"text": "假期第二天，你的状态？", "options": [
                {"text": "按计划执行，行程排得满满当当", "type": "A"},
                {"text": "玩得很开心，但已经开始累了", "type": "B"},
                {"text": "还没出过门，床是我最好的朋友", "type": "C"},
                {"text": "计划全打乱了，但无所谓", "type": "D"}
            ]},
            {"text": "假期朋友约你出门，你？", "options": [
                {"text": "约！社交不能断", "type": "A"},
                {"text": "看情况，近的话可以考虑", "type": "B"},
                {"text": "不想动，下次一定", "type": "C"},
                {"text": "嘴上答应，到时候看心情", "type": "D"}
            ]},
            {"text": "假期花销超预算了，你？", "options": [
                {"text": "没关系，假期嘛，开心最重要", "type": "A"},
                {"text": "有点心疼，但花都花了", "type": "B"},
                {"text": "本来就没什么花销，躺家不花钱", "type": "C"},
                {"text": "开始算账，然后默默心痛", "type": "D"}
            ]},
            {"text": "假期最后一天晚上，你？", "options": [
                {"text": "整理照片，发朋友圈总结", "type": "A"},
                {"text": "开始焦虑明天上班，睡不着", "type": "D"},
                {"text": "还在玩，明天的事明天再说", "type": "B"},
                {"text": "早早就睡了，为明天储备能量", "type": "C"}
            ]},
            {"text": "假期你最大的收获是？", "options": [
                {"text": "完成了学习计划，充实！", "type": "A"},
                {"text": "拍了一堆美照，朋友圈素材够了", "type": "B"},
                {"text": "睡够了，精神饱满", "type": "C"},
                {"text": "好像什么都没做，但也不后悔", "type": "D"}
            ]},
            {"text": "假期结束回到工位，你的心情？", "options": [
                {"text": "元气满满，休息好了继续冲", "type": "A"},
                {"text": "有点不想上班，但能接受", "type": "B"},
                {"text": "灵魂还在假期，身体已经打卡", "type": "C"},
                {"text": "已经在倒计时下一个假期了", "type": "D"}
            ]},
            {"text": "如果假期可以无限延长，你？", "options": [
                {"text": "还是会找事做，闲不住", "type": "A"},
                {"text": "环游世界，看遍风景", "type": "B"},
                {"text": "永远躺下去，这就是我的终极梦想", "type": "C"},
                {"text": "先躺一个月，再考虑要不要动", "type": "D"}
            ]}
        ],
        "results": {
            "A": {"label": "假期卷王", "percentage": "8%", "evaluations": [
                "放假对你来说只是换个地方卷，你的假期比上班还忙。",
                "别人在躺平，你在学习；别人在旅游，你在充电。",
                "你的人生没有假期，只有「换个姿势努力」。"
            ]},
            "B": {"label": "打卡型选手", "percentage": "30%", "evaluations": [
                "你的假期就是一场大型打卡活动，不去几个景点等于白放。",
                "朋友圈九宫格是你的勋章，定位是你的军功章。",
                "你玩的不是假期，是朋友圈的点赞数。"
            ]},
            "C": {"label": "躺平型选手", "percentage": "25%", "evaluations": [
                "你的假期只有两个姿势：躺着和翻身。",
                "床是你最忠诚的伙伴，外卖是你最亲密的朋友。",
                "你不是在休息，你是在进行一场与床的深度对话。"
            ]},
            "D": {"label": "焦虑型选手", "percentage": "15%", "evaluations": [
                "你的假期被焦虑填满——玩的时候觉得浪费时间，躺的时候觉得应该出门。",
                "假期前规划满满，假期中一事无成，假期后更加焦虑。",
                "你的假期不是用来放松的，是用来证明自己有多纠结的。"
            ]},
            "AB": {"label": "精致假期人", "percentage": "10%", "evaluations": [
                "你的假期精致到令人发指——行程、穿搭、美食全都要完美。",
                "你不是在度假，你是在拍生活方式广告。",
                "你的假期比上班还累，但你乐在其中——毕竟朋友圈需要你。"
            ]},
            "AC": {"label": "薛定谔的假期", "percentage": "5%", "evaluations": [
                "你的假期处于「卷」和「躺」的叠加态，直到有人问你才坍缩。",
                "上午还在学习，下午就开始躺平，一天体验两种人生。",
                "你是最真实的打工人——既想努力又想摆烂，两头都占。"
            ]},
            "BD": {"label": "佛系度假人", "percentage": "4%", "evaluations": [
                "你对假期没有执念，去哪都行，干啥都行，随缘。",
                "别人精心规划，你随机漫步；别人打卡拍照，你随走随停。",
                "你的假期哲学：计划赶不上变化，不如没有计划。"
            ]},
            "CD": {"label": "回血型选手", "percentage": "3%", "evaluations": [
                "你的假期只有一个目的——把打工消耗的血条回满。",
                "不社交、不出门、不折腾，安静地做一株植物。",
                "你不是在浪费假期，你是在为下一个工作周期储能。"
            ]}
        }
    }
}

# ==================== 辅助函数 ====================
def calculate_result(test_type, answers):
    """根据答案计算结果"""
    test = TEST_DATA[test_type]
    counts = {}
    for ans in answers:
        counts[ans] = counts.get(ans, 0) + 1

    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    top1 = sorted_counts[0][0]
    top2 = sorted_counts[1][0] if len(sorted_counts) > 1 else None

    # 尝试组合键
    combo_key1 = top1 + (top2 or "")
    combo_key2 = (top2 or "") + top1 if top2 else ""

    if combo_key1 in test["results"]:
        return combo_key1
    if combo_key2 and combo_key2 in test["results"]:
        return combo_key2
    if top1 in test["results"]:
        return top1

    # 默认返回第一个结果
    return list(test["results"].keys())[0]

def generate_label_image(label):
    """生成标签图片 - 卡通风格"""
    img_size = 400
    img = Image.new('RGB', (img_size, img_size), color='#fff9f0')
    draw = ImageDraw.Draw(img)

    # 卡通风格圆角边框 - 渐变色
    border_width = 8
    # 绘制多层边框营造卡通效果
    colors = ['#667eea', '#764ba2', '#9b59b6', '#8e44ad']
    for i, color in enumerate(colors):
        offset = i * 2
        draw.rounded_rectangle(
            [border_width - offset, border_width - offset, 
             img_size - border_width + offset, img_size - border_width + offset],
            radius=25,
            outline=color,
            width=3
        )

    # 尝试使用系统字体
    try:
        font = ImageFont.truetype("msyhbd.ttc", 58)  # 粗体
    except:
        try:
            font = ImageFont.truetype("Arial Unicode MS", 58)
        except:
            font = ImageFont.load_default()

    # 绘制文字（支持自动换行）+ 卡通阴影效果
    max_width = img_size - 80
    lines = []
    current_line = ""

    for char in label:
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width > max_width and current_line:
            lines.append(current_line)
            current_line = char
        else:
            current_line = test_line

    if current_line:
        lines.append(current_line)

    # 绘制每一行 - 添加阴影效果
    line_height = 72
    total_height = len(lines) * line_height
    start_y = (img_size - total_height) // 2 + line_height // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (img_size - text_width) // 2
        y = start_y + i * line_height
        
        # 阴影
        draw.text((x + 2, y + 2), line, fill='#b8c5d6', font=font)
        # 主文字
        draw.text((x, y), line, fill='#2c3e50', font=font)

    # 添加装饰元素 - 卡通星星
    star_positions = [(50, 50), (350, 50), (50, 350), (350, 350), (200, 60), (200, 340)]
    for star_x, star_y in star_positions:
        # 简单的星星形状
        points = [
            (star_x, star_y - 10),
            (star_x + 3, star_y - 3),
            (star_x + 10, star_y),
            (star_x + 3, star_y + 3),
            (star_x, star_y + 10),
            (star_x - 3, star_y + 3),
            (star_x - 10, star_y),
            (star_x - 3, star_y - 3)
        ]
        draw.polygon(points, fill='#f1c40f')

    return img

def generate_share_image(test_type, result_key):
    """生成分享图片 - 卡通游戏风格"""
    test = TEST_DATA[test_type]
    result = test["results"][result_key]

    # 创建画布 (9:16 比例)
    width, height = 1080, 1920
    img = Image.new('RGB', (width, height), color='#fff9f0')
    draw = ImageDraw.Draw(img)

    # 尝试加载字体
    try:
        title_font = ImageFont.truetype("msyhbd.ttc", 46)
        label_font = ImageFont.truetype("msyhbd.ttc", 94)
        content_font = ImageFont.truetype("msyh.ttc", 38)
        small_font = ImageFont.truetype("msyhbd.ttc", 32)
    except:
        try:
            title_font = ImageFont.truetype("Arial Unicode MS", 46)
            label_font = ImageFont.truetype("Arial Unicode MS", 94)
            content_font = ImageFont.truetype("Arial Unicode MS", 38)
            small_font = ImageFont.truetype("Arial Unicode MS", 32)
        except:
            title_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

    # 绘制装饰性卡通边框
    border_colors = ['#667eea', '#764ba2', '#9b59b6', '#e91e63', '#f39c12']
    border_width = 12
    for i, color in enumerate(border_colors):
        offset = i * 4
        draw.rounded_rectangle(
            [border_width - offset, border_width - offset,
             width - border_width + offset, height - border_width + offset],
            radius=30,
            outline=color,
            width=4
        )

    # 绘制测试标题
    title_bbox = draw.textbbox((0, 0), test["title"], font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) // 2, 180), test["title"], fill='#764ba2', font=title_font)

    # 绘制标签（支持换行）
    label_lines = []
    current_line = ""
    max_label_width = width - 120

    for char in result["label"]:
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=label_font)
        text_width = bbox[2] - bbox[0]

        if text_width > max_label_width and current_line:
            label_lines.append(current_line)
            current_line = char
        else:
            current_line = test_line

    if current_line:
        label_lines.append(current_line)

    # 绘制标签文字 - 卡通风格
    label_start_y = 400
    line_height = 112

    for i, line in enumerate(label_lines):
        bbox = draw.textbbox((0, 0), line, font=label_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = label_start_y + i * line_height
        
        # 卡通阴影
        draw.text((x + 4, y + 4), line, fill='#d4d9e0', font=label_font)
        # 主文字
        draw.text((x, y), line, fill='#2c3e50', font=label_font)

    # 绘制卡通装饰分割线 - 彩虹色
    after_label_y = label_start_y + len(label_lines) * line_height + 70
    rainbow_colors = ['#667eea', '#764ba2', '#9b59b6', '#e91e63', '#f39c12']
    line_height_div = 8
    for i, color in enumerate(rainbow_colors):
        y_pos = after_label_y + i * line_height_div
        draw.line([(80, y_pos), (width - 80, y_pos)], fill=color, width=4)

    # 绘制占比 - 卡通风格
    percentage_text = f"全国占比 {result['percentage']}"
    per_bbox = draw.textbbox((0, 0), percentage_text, font=content_font)
    per_width = per_bbox[2] - per_bbox[0]
    draw.text(((width - per_width) // 2, after_label_y + 70 + len(rainbow_colors) * line_height_div + 30),
              percentage_text, fill='#764ba2', font=content_font)

    # 绘制评价 - 卡通风格
    eval_start_y = after_label_y + 70 + len(rainbow_colors) * line_height_div + 120
    eval_line_height = 46
    max_eval_width = width - 220

    for i, eval_text in enumerate(result["evaluations"]):
        # 分割评价文字
        eval_lines = []
        current_line = ""

        for char in eval_text:
            test_line = current_line + char
            bbox = draw.textbbox((0, 0), test_line, font=content_font)
            text_width = bbox[2] - bbox[0]

            if text_width > max_eval_width and current_line:
                eval_lines.append(current_line)
                current_line = char
            else:
                current_line = test_line

        if current_line:
            eval_lines.append(current_line)

        # 绘制每一行 - 添加卡通边框背景
        for j, line in enumerate(eval_lines):
            bbox = draw.textbbox((0, 0), line, font=content_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = eval_start_y + i * (len(eval_lines) * eval_line_height + 46) + j * eval_line_height
            
            # 卡通气泡背景
            bubble_padding = 16
            bubble_x = x - bubble_padding
            bubble_y = y - text_height // 2 - bubble_padding // 2
            bubble_w = text_width + bubble_padding * 2
            bubble_h = text_height + bubble_padding
            
            # 不同评价使用不同颜色
            bubble_colors = ['#f8f9ff', '#fff5f5', '#f0fdf4']
            bubble_color = bubble_colors[i % len(bubble_colors)]
            
            draw.rounded_rectangle(
                [bubble_x, bubble_y, bubble_x + bubble_w, bubble_y + bubble_h],
                radius=16,
                fill=bubble_color,
                outline='#667eea',
                width=2
            )
            
            # 文字
            draw.text((x, y), line, fill='#374151', font=content_font)

    # 绘制底部彩虹分割线
    footer_line_y = height - 180
    for i, color in enumerate(rainbow_colors):
        y_pos = footer_line_y + i * line_height_div
        draw.line([(80, y_pos), (width - 80, y_pos)], fill=color, width=4)

    # 绘制底部文字 - 卡通风格
    footer_text = "来测测你是什么人格？"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=small_font)
    footer_width = footer_bbox[2] - footer_bbox[0]
    draw.text(((width - footer_width) // 2, height - 130), footer_text, fill='#764ba2', font=small_font)

    # 添加卡通装饰元素 - 星星和圆点
    # 随机位置的星星
    import random
    random.seed(42)  # 固定种子确保一致性
    for _ in range(8):
        star_x = random.randint(100, width - 100)
        star_y = random.randint(300, height - 300)
        star_size = random.randint(8, 15)
        star_color = random.choice(['#f1c40f', '#e74c3c', '#9b59b6', '#3498db'])
        
        # 绘制星星
        points = [
            (star_x, star_y - star_size),
            (star_x + star_size * 0.3, star_y - star_size * 0.3),
            (star_x + star_size, star_y),
            (star_x + star_size * 0.3, star_y + star_size * 0.3),
            (star_x, star_y + star_size),
            (star_x - star_size * 0.3, star_y + star_size * 0.3),
            (star_x - star_size, star_y),
            (star_x - star_size * 0.3, star_y - star_size * 0.3)
        ]
        draw.polygon(points, fill=star_color)

    # 添加圆点装饰
    for _ in range(12):
        dot_x = random.randint(100, width - 100)
        dot_y = random.randint(300, height - 300)
        dot_size = random.randint(4, 8)
        dot_color = random.choice(['#667eea', '#764ba2', '#9b59b6', '#e91e63'])
        draw.ellipse([dot_x - dot_size, dot_y - dot_size, dot_x + dot_size, dot_y + dot_size],
                     fill=dot_color)

    return img

def image_to_base64(img):
    """将图片转换为base64"""
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

# ==================== 页面状态管理 ====================
if 'current_test' not in st.session_state:
    st.session_state.current_test = None
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'result_key' not in st.session_state:
    st.session_state.result_key = None
if 'show_result' not in st.session_state:
    st.session_state.show_result = False
if 'immersive_mode' not in st.session_state:
    st.session_state.immersive_mode = False

# ==================== URL路由处理 ====================
query_params = st.query_params
if 'test' in query_params:
    test_type = query_params['test'][0]
    if test_type in TEST_DATA:
        st.session_state.current_test = test_type
        st.session_state.current_question = 0
        st.session_state.answers = []
        st.session_state.result_key = None
        st.session_state.show_result = False
        st.session_state.immersive_mode = True
        st.rerun()

# ==================== 沉浸式模式切换 ====================
if st.session_state.immersive_mode:
    st.markdown('<div class="immersive-mode"></div>', unsafe_allow_html=True)

# ==================== 首页 ====================
if st.session_state.current_test is None:
    # 页面标题
    st.markdown('<p class="subtitle">Personality Test</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">当代人类<br>身份鉴定中心</h1>', unsafe_allow_html=True)

    # 测试介绍
    st.markdown('<p style="text-align: center; color: #7c8db8; margin-bottom: 2rem; font-size: 1rem;">选择一个测试，开始探索你的真实人格</p>', unsafe_allow_html=True)

    # 按钮容器
    st.markdown('<div class="button-container">', unsafe_allow_html=True)

    for test_key, test_data in TEST_DATA.items():
        # 为每个测试创建独立的链接
        test_url = f"?test={test_key}"
        if st.button(test_data['title'], key=f"test_{test_key}", help=f"开始{test_data['title']}"):
            st.session_state.current_test = test_key
            st.session_state.current_question = 0
            st.session_state.answers = []
            st.session_state.result_key = None
            st.session_state.show_result = False
            st.session_state.immersive_mode = True
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # 底部提示
    st.markdown('<p class="footer-text">每个测试都是一次独特的沉浸式体验</p>', unsafe_allow_html=True)

# ==================== 测试页面 ====================
elif not st.session_state.show_result:
    test = TEST_DATA[st.session_state.current_test]
    question = test["questions"][st.session_state.current_question]

    # 测试标题
    st.markdown(f'<p class="subtitle">{test["title"]}</p>', unsafe_allow_html=True)

    # 进度条
    progress = (st.session_state.current_question + 1) / len(test["questions"]) * 100
    st.markdown(f"""
    <div class="progress-container">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem; color: #9ca3af; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase;">
            <span>Progress</span>
            <span>{st.session_state.current_question + 1}/{len(test["questions"])}</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 题目
    st.markdown(f'<p class="question-text">{question["text"]}</p>', unsafe_allow_html=True)

    # 选项
    st.markdown('<div class="options-container">', unsafe_allow_html=True)
    for i, option in enumerate(question["options"]):
        if st.button(option["text"], key=f"option_{i}", use_container_width=True):
            st.session_state.answers.append(option["type"])
            st.session_state.current_question += 1

            # 检查是否完成
            if st.session_state.current_question >= len(test["questions"]):
                st.session_state.result_key = calculate_result(st.session_state.current_test, st.session_state.answers)
                st.session_state.show_result = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== 结果页面 - 沉浸式 + 趣味引导 ====================
else:
    test = TEST_DATA[st.session_state.current_test]
    result = test["results"][st.session_state.result_key]

    # 核心标签 - 大号动画
    st.markdown(f'<p class="result-label">{result["label"]}</p>', unsafe_allow_html=True)

    # 标签图片
    label_img = generate_label_image(result["label"])
    st.markdown('<div class="image-container">', unsafe_allow_html=True)
    st.image(label_img, width=180)
    st.markdown('</div>', unsafe_allow_html=True)

    # 全国占比
    st.markdown(f'<p class="percentage-text">全国占比 {result["percentage"]}</p>', unsafe_allow_html=True)

    # 分割线
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # 评价内容
    for eval_text in result["evaluations"]:
        st.markdown(f'<p class="evaluation-text">{eval_text}</p>', unsafe_allow_html=True)

    # 分割线
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # 操作按钮容器
    st.markdown('<div class="button-container">', unsafe_allow_html=True)

    # 复制结果
    copy_text = f"【{test['title']}】\n我的结果是：{result['label']}\n全国占比：{result['percentage']}\n\n"
    for eval_text in result["evaluations"]:
        copy_text += eval_text + "\n\n"
    copy_text += "来测测你是什么人格？"

    if st.button("📋 复制结果", key="copy_result"):
        st.code_area = copy_text
        st.success("✅ 已复制到剪贴板")

    # 生成分享图
    if st.button("🖼️ 生成分享图", key="share_image"):
        share_img = generate_share_image(st.session_state.current_test, st.session_state.result_key)
        img_base64 = image_to_base64(share_img)

        # 创建下载链接
        href = f'<a href="data:file/png;base64,{img_base64}" download="{result["label"]}_测试结果.png" style="color: #ffffff; text-decoration: none; display: block; text-align: center; padding: 0.5rem; font-size: 0.875rem;">↓ 下载分享图</a>'
        st.markdown(href, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ==================== 趣味引导区域 ====================
    st.markdown('<br><br>', unsafe_allow_html=True)
    
    # 引导标题
    st.markdown('<p style="text-align: center; color: #95a5a6; font-size: 0.875rem; margin-bottom: 1rem; letter-spacing: 0.1em; text-transform: uppercase;">还想探索更多人格？</p>', unsafe_allow_html=True)

    # 其他测试推荐 - 趣味动画
    st.markdown('<div class="button-container">', unsafe_allow_html=True)

    for test_key, test_data in TEST_DATA.items():
        if test_key != st.session_state.current_test:
            # 使用Streamlit按钮，添加脉冲光环动画
            st.markdown('<div class="pulse-ring">', unsafe_allow_html=True)
            if st.button(f"✨ {test_data['title']}", key=f"other_test_{test_key}"):
                st.session_state.current_test = test_key
                st.session_state.current_question = 0
                st.session_state.answers = []
                st.session_state.result_key = None
                st.session_state.show_result = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 返回首页按钮 - 趣味样式
    st.markdown('<div class="button-container outline-button">', unsafe_allow_html=True)
    
    # 趣味返回按钮
    if st.button("🏠 返回首页探索更多", key="back_home"):
        st.session_state.current_test = None
        st.session_state.current_question = 0
        st.session_state.answers = []
        st.session_state.result_key = None
        st.session_state.show_result = False
        st.session_state.immersive_mode = False
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

    # 底部趣味提示 - 动画
    st.markdown('''
    <div style="text-align: center; margin-top: 3rem;">
        <p class="footer-text">
            <span class="arrow-bounce">↓</span> 
            分享结果，看看朋友是什么人格 
            <span class="arrow-bounce">↓</span>
        </p>
    </div>
    ''', unsafe_allow_html=True)
