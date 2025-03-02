import os
from dotenv import load_dotenv
from openai import OpenAI
import time
import logging
from typing import List, Dict, Union
import random
import json

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AI_Agent:
    def __init__(self, system_prompt: str, model: str, max_retries: int, retry_delay: int):
        if max_retries <= 0:
            raise ValueError("max_retries must be a positive integer.")
        if retry_delay <= 0:
            raise ValueError("retry_delay must be a positive integer.")
        self.system_prompt = system_prompt
        self.model = model
        self.client = OpenAI(
            # base_url="https://xiaohumini.site/v1",  # 修改为你的 API 中转地址
            # api_key="sk-sfcpWhfMrPda4MvJohypXra0XAIk6xQnXNjZjqL0BVT6Of9a",  # 修改为你的 API 密钥
            base_url="https://i-helios.top/v1",  # 修改为你的 API 中转地址
            api_key="sk-QsKfdFa18BPjMXpe5h3I77Ic5vnfyxtHohbmUZi3gDwWQGWq",  # 修改为你的 API 密钥
        )
        self.messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]  # 对话历史
        self.max_retries = max_retries  # 最大重试次数
        self.retry_delay = retry_delay  # 重试间隔时间
        logging.info(f"AI Agent initialized with model: {model}")


    def send_message(self, message: str) -> Union[str, None]:
        """向模型发送消息，并更新对话历史"""
        self.messages.append({"role": "user", "content": message})
        retries = 0
        while retries < self.max_retries:
            try:
                logging.info(f"Sending message to model: {self.model}, attempt {retries + 1}/{self.max_retries}")
                response = self.client.chat.completions.create(
                    model="deepseek-r1",
                    messages=self.messages,
                )
                if response and response.choices and response.choices[0] and response.choices[0].message:
                    ai_response = response.choices[0].message.content
                    self.messages.append({"role": "assistant", "content": ai_response})
                    logging.info(f"Received response from model: {self.model}")
                    time.sleep(1) # 添加冷却时间
                    return ai_response
                else:
                     logging.warning(f"API returned invalid response, retrying... ({retries+1}/{self.max_retries})")
                     retries += 1
                     time.sleep(self.retry_delay * (2 ** retries) + random.uniform(0, 1))  # 指数退避重试策略

            except Exception as e:
                logging.error(f"API call failed: {e}, retrying... ({retries+1}/{self.max_retries})")
                retries += 1
                time.sleep(self.retry_delay * (2 ** retries) + random.uniform(0, 1))  # 指数退避重试策略

        logging.error("API call failed, maximum retries reached, returning None")
        return None

    def get_history(self) -> List[Dict[str, str]]:
        return self.messages

    def export_chat_history(self, filename: str):
        """导出对话历史到 JSON 文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, indent=4, ensure_ascii=False)
            logging.info(f"Chat history exported to {filename}")
        except Exception as e:
            logging.error(f"Failed to export chat history: {e}")
