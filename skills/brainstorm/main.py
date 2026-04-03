#!/usr/bin/env python3
"""
Brainstorm - 头脑风暴 Agent
组织深度讨论，产生创新方案
"""
import os, json, time
from datetime import datetime
from pathlib import Path

class BrainstormAgent:
    def __init__(self):
        self.session_dir = 'sessions/brainstorm'
        os.makedirs(self.session_dir, exist_ok=True)
        
    def organize_session(self, topic, participants=None, duration=60):
        """组织头脑风暴会议"""
        print(f"\n{'='*70}")
        print(f"🧠 头脑风暴会议")
        print(f"{'='*70}")
        print(f"主题：{topic}")
        print(f"参与者：{participants or ['AI Assistant']}")
        print(f"时长：{duration}分钟")
        print(f"{'='*70}\n")
        
        session = {
            'id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'topic': topic,
            'participants': participants or ['AI Assistant'],
            'started_at': datetime.now().isoformat(),
            'duration_minutes': duration,
            'ideas': [],
            'categories': {},
            'recommendations': [],
        }
        
        # 引导讨论
        ideas = self.facilitate_discussion(topic)
        session['ideas'] = ideas
        
        # 分类整理
        session['categories'] = self.categorize_ideas(ideas)
        
        # 方案评估
        session['recommendations'] = self.evaluate_and_recommend(ideas)
        
        # 保存会议记录
        session['ended_at'] = datetime.now().isoformat()
        self.save_session(session)
        
        return session
        
    def facilitate_discussion(self, topic):
        """引导讨论，收集想法"""
        print("💡 开始引导讨论...\n")
        
        ideas = []
        idea_id = 0
        
        # 针对自动化研发体系，引导关键议题
        discussion_points = [
            "架构设计：五层架构是否合理？需要调整吗？",
            "任务分类：15 种任务类型是否完整？有遗漏吗？",
            "流程设计：需求到交付流程是否顺畅？",
            "约束条件：6 种约束是否充分？需要补充吗？",
            "实施优先级：Phase 1-4 的时间线是否合理？",
            "风险识别：有哪些潜在风险？如何 mitigat e？",
            "资源需求：需要哪些人力/计算资源？",
            "成功标准：如何衡量系统成功？",
        ]
        
        for point in discussion_points:
            print(f"讨论点：{point}")
            # 模拟 AI 参与讨论
            ai_ideas = self.generate_ai_ideas(point, topic)
            ideas.extend(ai_ideas)
            idea_id += len(ai_ideas)
            print(f"  ✅ 收集到 {len(ai_ideas)} 个想法\n")
            
        return ideas
        
    def generate_ai_ideas(self, discussion_point, topic):
        """AI 生成想法"""
        ideas = []
        
        # 根据讨论点生成针对性想法
        if '架构' in discussion_point:
            ideas.extend([
                {
                    'category': '架构',
                    'description': '五层架构清晰分离关注点，建议保持',
                    'pros': ['职责清晰', '易于维护', '可扩展'],
                    'cons': ['层间通信开销'],
                    'feasibility': 'high',
                    'priority': 'P0',
                    'effort': 'medium',
                },
                {
                    'category': '架构',
                    'description': '增加插件层，支持第三方扩展',
                    'pros': ['生态扩展', '灵活性高'],
                    'cons': ['复杂度增加', '安全风险'],
                    'feasibility': 'medium',
                    'priority': 'P2',
                    'effort': 'large',
                },
            ])
        elif '任务' in discussion_point:
            ideas.extend([
                {
                    'category': '任务',
                    'description': '增加代码审查任务类型',
                    'pros': ['提高代码质量', '早期发现问题'],
                    'cons': ['增加执行时间'],
                    'feasibility': 'high',
                    'priority': 'P1',
                    'effort': 'small',
                },
            ])
        elif '流程' in discussion_point:
            ideas.extend([
                {
                    'category': '流程',
                    'description': '添加快速路径，紧急任务可跳过部分审查',
                    'pros': ['响应快速', '适合 P0 任务'],
                    'cons': ['风险增加'],
                    'feasibility': 'high',
                    'priority': 'P1',
                    'effort': 'small',
                },
            ])
        elif '约束' in discussion_point:
            ideas.extend([
                {
                    'category': '约束',
                    'description': '增加成本约束，控制资源使用',
                    'pros': ['避免资源浪费', '可预测成本'],
                    'cons': ['可能限制创新'],
                    'feasibility': 'medium',
                    'priority': 'P2',
                    'effort': 'medium',
                },
            ])
        elif '优先级' in discussion_point:
            ideas.extend([
                {
                    'category': '实施',
                    'description': 'Phase 1 聚焦核心能力，2 周完成',
                    'pros': ['快速见效', '降低风险'],
                    'cons': ['功能有限'],
                    'feasibility': 'high',
                    'priority': 'P0',
                    'effort': 'medium',
                },
            ])
            
        # 为每个想法添加元数据
        for idea in ideas:
            idea['id'] = len(ideas)
            idea['generated_at'] = datetime.now().isoformat()
            idea['source'] = 'AI_Assistant'
            
        return ideas
        
    def categorize_ideas(self, ideas):
        """分类整理想法"""
        print("📂 分类整理想法...\n")
        
        categories = {}
        for idea in ideas:
            cat = idea.get('category', '其他')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(idea)
            
        for cat, cat_ideas in categories.items():
            print(f"  {cat}: {len(cat_ideas)} 个想法")
            
        return categories
        
    def evaluate_and_recommend(self, ideas):
        """评估想法并提供建议"""
        print("\n📊 评估想法并生成建议...\n")
        
        # 按优先级和可行性排序
        scored_ideas = []
        for idea in ideas:
            score = self.calculate_score(idea)
            scored_ideas.append((score, idea))
            
        scored_ideas.sort(key=lambda x: -x[0])
        
        # 生成 Top 建议
        recommendations = []
        for score, idea in scored_ideas[:5]:
            if score >= 0.7:  # 高分想法
                recommendations.append({
                    'idea': idea['description'],
                    'score': score,
                    'reason': f"优先级{idea.get('priority', 'N/A')}, 可行性{idea.get('feasibility', 'N/A')}",
                })
                
        for rec in recommendations:
            print(f"  ✅ 推荐：{rec['idea']} (得分：{rec['score']:.2f})")
            
        return recommendations
        
    def calculate_score(self, idea):
        """计算想法得分"""
        priority_scores = {'P0': 1.0, 'P1': 0.7, 'P2': 0.4, 'P3': 0.1}
        feasibility_scores = {'high': 1.0, 'medium': 0.6, 'low': 0.2}
        effort_scores = {'small': 1.0, 'medium': 0.6, 'large': 0.3}
        
        priority = priority_scores.get(idea.get('priority', 'P2'), 0.4)
        feasibility = feasibility_scores.get(idea.get('feasibility', 'medium'), 0.6)
        effort = effort_scores.get(idea.get('effort', 'medium'), 0.6)
        
        # 加权平均
        score = (priority * 0.4 + feasibility * 0.4 + effort * 0.2)
        return score
        
    def save_session(self, session):
        """保存会议记录"""
        session_file = os.path.join(self.session_dir, f"session_{session['id']}.json")
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
        print(f"\n📄 会议记录已保存：{session_file}")
        
    def print_summary(self, session):
        """打印会议总结"""
        print(f"\n{'='*70}")
        print("📋 会议总结")
        print(f"{'='*70}")
        print(f"主题：{session['topic']}")
        print(f"总想法数：{len(session['ideas'])}")
        print(f"分类数：{len(session['categories'])}")
        print(f"推荐方案：{len(session['recommendations'])}")
        print(f"{'='*70}")

if __name__ == '__main__':
    import sys
    
    agent = BrainstormAgent()
    
    if len(sys.argv) > 1:
        topic = ' '.join(sys.argv[1:])
    else:
        topic = "自动化研发体系架构设计"
        
    session = agent.organize_session(
        topic=topic,
        participants=['AI Assistant', 'System Architect', 'DevOps Engineer'],
        duration=60,
    )
    
    agent.print_summary(session)
