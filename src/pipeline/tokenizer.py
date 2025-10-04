from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

def count_tokens(text, model="gpt-3.5-turbo"):
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def chunk_text(text: str, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)

def chunk_with_metadata(all_pdfs_data, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )

    chunks_results = []
    chunk_id = 0
    for pdf in all_pdfs_data:
        for page in pdf:
            chunks = splitter.split_text(page["text"])
            for chunk in chunks: 
                chunk_id += 1

                chunks_results.append({
                    "chunk_id": chunk_id,
                    "file_id": page["file_id"],
                    "file_name": page["file_name"],
                    "page": page["page"],
                    "text": chunk
                })
    print("Les 6 premiers chunks", chunks_results[:6])
    return chunks_results