from langchain_community.document_loaders import PyPDFLoader

def extract_text_from_pdf(path: str) -> str:
    loader = PyPDFLoader(path, mode="page")
    docs = loader.load()
    return "\n".join(page.page_content for page in docs)