from typing import Dict, Any
import re
class PromptGenerator:
    def generate_new_prompt(self, original_prompt: str, settings: Dict[str, Any]) -> str:
        """将设定的信息添加到新的提示词中"""
        new_prompt = f"{original_prompt}\n\n"
        
        #把历史对话改为加入上一章节的内容
        # if 'history' in settings:
        #     new_prompt += "历史对话:\n"
        #     for item in settings['history']:
        #         print("--------------历史对话:", len(item))
        #         new_prompt += f"{item}\n"
        if 'part_chapter' in settings:
            new_prompt += f"最新的章节的内容:\n{settings['part_chapter']}\n\n"

        if 'full_outline' in settings:
             new_prompt += f"小说完整大纲:\n{settings['full_outline']}\n\n"

        if 'chapter_titles' in settings:
            chapter_list = settings['chapter_titles'].splitlines()
            turn = settings.get('turn',0)
            if turn > 1 and len(chapter_list) >= turn -1:
                previous_chapter_title = chapter_list[turn - 2].strip()
                new_prompt += f"上一章节的标题: {previous_chapter_title}\n"
            
            current_chapter_title = ""
            if len(chapter_list) >= turn:
                current_chapter_title = chapter_list[turn - 1].strip()
            new_prompt += f"当前章节的标题: {current_chapter_title}\n"
        
        #new_prompt += f"\n\n以下是截至目前为止生成的设定:\n{settings}"
        return new_prompt
