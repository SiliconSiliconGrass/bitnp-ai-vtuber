"""
To download pretrained GPT-SoVITS models
"""
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com' # use hf-mirror (for users in China)

from huggingface_hub import snapshot_download

curr_dir = os.path.dirname(os.path.abspath(__file__))
pretrained_models_dir = os.path.join(curr_dir, "GPT_SoVITS", "pretrained_models")

def download_models(repo_id: str, files_to_download: list[str], local_dir: str):
    
    snapshot_download(
        repo_id=repo_id,
        repo_type="model",
        local_dir=local_dir,
        local_dir_use_symlinks="auto",
        revision="main",
        allow_patterns=files_to_download
    )


gpt_sovits_repo_id = "lj1995/GPT-SoVITS"
gpt_sovits_files = [
    "s2G488k.pth", # SoVITS model (v1)
    "s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt", # GPT model (v1)
    "chinese-roberta-wwm-ext-large/*", # Bert model
    "chinese-hubert-base/*" # Hubert model
]

fasttext_repo_id = "facebook/fasttext-language-identification"
fasttext_files = [
    "model.bin", # FastText model
]



try:

    print("Downloading GPT-SoVITS pretrained models...")
    download_models(gpt_sovits_repo_id, gpt_sovits_files, pretrained_models_dir)

    print("Downloading FastText pretrained models...")
    if not os.path.exists(os.path.join(pretrained_models_dir, "fast_langdetect")):
        os.makedirs(os.path.join(pretrained_models_dir, "fast_langdetect"))
    
    if not os.path.exists(os.path.join(pretrained_models_dir, "fast_langdetect", "lid.176.bin")):
        download_models(fasttext_repo_id, fasttext_files, os.path.join(pretrained_models_dir, "fast_langdetect"))
        os.rename(os.path.join(pretrained_models_dir, "fast_langdetect", "model.bin"), os.path.join(pretrained_models_dir, "fast_langdetect", "lid.176.bin"))



except Exception as e:
    print(f"Failed: {e}")
else:
    print("Download completed successfully!")