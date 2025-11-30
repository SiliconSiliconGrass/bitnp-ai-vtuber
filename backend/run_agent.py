import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_types import LLM_Config, TTS_Config, AgentConfig
from agent import create_agent
from tokens import get_token

server_url = "localhost:8000"
agent_name = "shumeiniang"

llm_api_config = LLM_Config(
    api_name = 'glm',
    token = get_token('glm'),
    model_name = 'glm-4-flash',
    system_prompt = '你是树莓娘，网络开拓者协会的看板娘。', # 系统提示词
    max_context_length = 11 # 最大上下文长度 (轮数)
)

tts_config = TTS_Config(
    gpt_weights_path = "./tts/GPT_SoVITS/pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt",
    sovits_weights_path = "./tts/GPT_SoVITS/pretrained_models/s2G488k.pth",
    ref_wav_path = "./tts/ref_audio/paimeng.wav",
    prompt_text = "蒙德有很多风车呢。回答正确！蒙德四季风吹不断，所以水源的供应也很稳定。",
    prompt_language = "zh"
)

agent_config = AgentConfig(
    server_url = server_url,
    agent_name = agent_name,
    llm_api_config = llm_api_config,
    tts_config = tts_config
)

agent = create_agent(agent_type = 'basic_chatting_agent', **agent_config.model_dump())

asyncio.run(agent.run())
