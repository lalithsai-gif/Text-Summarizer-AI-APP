from huggingface_hub import HfApi

api = HfApi()

api.upload_folder(
    folder_path="saved_summary_model",
    repo_id="GRAFTERlalith/Text-summarizer-t5",
    repo_type="model"
)

print("Upload successful!")
