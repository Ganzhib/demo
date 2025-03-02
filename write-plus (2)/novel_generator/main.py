import time
from novel_generator.utils.file_handler import FileHandler
from novel_generator.agents.ai_agent import AI_Agent
from novel_generator.agents.dialogue_manager import DialogueManager
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_agents_and_manager(file_handler):
    """初始化AI Agent和对话管理器"""
    try:
        ai1_prompt = file_handler.read_text_from_file("config/ai1_prompt.txt")
        ai2_prompt = file_handler.read_text_from_file("config/ai2_prompt.txt")
        settings = file_handler.read_json_from_file("config/settings.json")

        ai1 = AI_Agent(ai1_prompt, settings["model"], settings["max_retries"], settings["retry_delay"])
        ai2 = AI_Agent(ai2_prompt, settings["model"], settings["max_retries"], settings["retry_delay"])
        dialogue_manager = DialogueManager(ai1, ai2, export_frequency=settings["export_frequency"], output_dir=settings["output_dir"])
        return ai1, ai2, dialogue_manager
    except Exception as e:
        logging.error(f"初始化失败：{e}")
        return None, None, None
def initial_setting(ai1, ai2):
    """初始化设定，生成基础内容"""
    print("开始初始化设定...")
    initial_prompt = "开始创作, 请使用中文"
    response_ai1 = ai1.send_message(initial_prompt)

    
    # print(f"AI1: {response_ai1}")    
    theme = input("请输入小说的主题:")
    # theme = "武侠修仙"
    response_ai2 = ai2.send_message("小说的主题是{}，请给出小说创作的基础方向, 包括类型, 主角, 世界背景等，并且按照以下格式给出: 【名称】:内容, 例如【类型】:武侠修仙".format(theme))
    print(f"AI2: {response_ai2}")

    for i in range(3):
      print("---------第{}轮完善设定---------".format(i+1))
      response_ai1 = ai1.send_message(f"请根据以下方向, 不断完善设定: {response_ai2},请注意保持格式不变")
      print(f"AI1: {response_ai1}")
      time.sleep(1)
    return response_ai1,response_ai2

def read_file(filename):
    # 构建文件路径
        file_path = os.path.join("output", filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"读取文件失败: {e}")
            return None


def main():
    # 读取配置文件
    load_filename = input("是否从上次断档处续写？如要续写，请输入上次断档处章节编号，否则直接按回车即可：")
    file_handler = FileHandler()
    ai1, ai2, dialogue_manager = initialize_agents_and_manager(file_handler)
    if not ai1 or not ai2 or not dialogue_manager:
        print("程序初始化失败，退出。")
        return
    
    if load_filename == "":
        response_ai1, response_ai2 = initial_setting(ai1, ai2)
        bg_seettings = dialogue_manager.extract_background_settings(response_ai1)
    
        print("尊敬的田壮壮大人，已经提取到的小说设定能内容如下：")
        if len(bg_seettings) == 0:
            print("没有提取到小说设定内容")
        else:
            for key, value in bg_seettings.items():
                print(f"{key}: {value}")
                print("--------------------------------")   
            """保存小说背景设定以及章节目录"""
            dialogue_manager.save_bg_settings()
        state = "outline"
    else:
        print("开始从上次断档处续写")
        state = "continue"
    # 定义状态
    
    while True:
       if state == "outline":
          # 大纲阶段
          print("开始生成大纲...")
          outline_prompt = "我们的小说设定为80万字, 400章, 8卷, 一卷50章. 请给出小说的具体设定以及大纲目录章节"
          response_ai1 = ai1.send_message(outline_prompt)
          dialogue_manager.novel_information = f"{response_ai1}"#保存小说章节名称等信息
          print(f"AI1: {response_ai1}")
          dialogue_manager.save_novel_index()   
          
          # 章节阶段
        #   print("开始生成前五十章章节标题...")
        #   chapter_prompt = "请根据大纲, 给出前50章的标题"   
        #   response_ai2 = ai2.send_message(chapter_prompt)
        #   print(f"AI2: {response_ai2}")

          # 保存大纲, 目录, 章节信息
        #   settings_for_chapter = {
        #      "turn": 0,
        #      "history": [f"AI1:{response_ai1}", f"AI2:{response_ai2}"]
        #     }
        #   dialogue_manager.save_settings(settings_for_chapter)
          state = "chapter1"
       elif state == "chapter1":
            # 生成第一章
            print("开始生成第一章...")
            bg_settings_str = f""
            for key, value in bg_seettings.items():
                 bg_settings_str += f"{key}: {value}\n"
            first_chapter_prompt = f"请根据以下小说设定和大纲, 生成第一章内容: {dialogue_manager.novel_information} ,请将章节章节名称用中文括号包起来,如:【第一章：残阳如血】" 
            response_ai1 = ai1.send_message(first_chapter_prompt)
            print(f"AI1: {response_ai1}")
            dialogue_manager.save_chapter_content(response_ai1)#保存第一章
            # 检查第一章
            print("开始审核第一章")
            check_first_chapter_prompt = "请审核第一章内容, 检查逻辑、设定是否符合网文小说以及是否符合小说背景设定:第1章内容:{}, 背景设定:{}".format(response_ai1, bg_settings_str)
            response_ai2 = ai2.send_message(check_first_chapter_prompt)
            print(f"AI2: {response_ai2}")
        

            # 保存第一章
            # settings_for_chapter = {
            #     "turn": 1,
            #     "history": [f"AI1:{response_ai1}", f"AI2:{response_ai2}"]
            #  }
            # print("---------提取设定---------")
            # dialogue_manager.extract_settings()
            # dialogue_manager.save_settings(settings_for_chapter)
            state = "continue"
       elif state == "continue":
         if load_filename != "":
             dialogue_manager.turn = int(load_filename)
             #加载背景、文章内容、章节目录
             file_handler = FileHandler()
             load_filename = f"chapter_content_{load_filename}.txt"
             load_content = read_file(load_filename)

             load_chapter_index= read_file(f"novel_index.txt")
             dialogue_manager.novel_information = load_chapter_index

             load_bg_setting= read_file(f"novel_settings.txt")
             bg_settings = dialogue_manager.extract_background_settings(load_bg_setting)
             if len(bg_settings) == 0:
                print("没有提取到小说设定内容")
             else:
                 print("小说设定已提取：")
             check_first_chapter_prompt = "请审核本章内容, 检查逻辑、设定是否符合网文小说以及是否符合小说背景设定:内容:{}, 背景设定:{}".format(load_content, load_bg_setting)
             response_ai2 = ai2.send_message(check_first_chapter_prompt)
             print(f"AI2: {response_ai2}")
             response_ai1 = load_content
             
         # 开始后续章节
         dialogue_manager.start_dialogue(f"请根据上一章的设定和内容, 继续输出下一章, 确保逻辑连贯, 请使用中文, 并且每一章的字数不少于2000字",response_ai1, response_ai2 )
       elif state == "stop":
           break
    # 展示导出
    exported_settings = dialogue_manager.get_exported_settings()
    for turn, settings in exported_settings.items():
       print(f"turn: {turn}, settings: {settings}")

    
if __name__ == "__main__":
    main()