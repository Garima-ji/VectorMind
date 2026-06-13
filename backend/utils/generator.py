"""RAG Answer generator using serverless LLM API and local CPU fallback model."""
import os
import requests

try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

class RAGGenerator:
    """Intelligent Answer Generator utilizing context documents and LLM text generation."""
    
    def __init__(self, local_model="google/flan-t5-small", hf_api_model="meta-llama/Meta-Llama-3-8B-Instruct"):
        """
        Initialize the generator.
        
        Args:
            local_model: Local Hugging Face Seq2Seq model (e.g. flan-t5-small)
            hf_api_model: Serverless inference API model ID
        """
        self.local_model_name = local_model
        self.hf_api_model = hf_api_model
        self.local_tokenizer = None
        self.local_model = None
        self.hf_token = os.getenv("HF_TOKEN")
        
    def _load_local_model(self):
        """Lazy load local transformer model & tokenizer to save RAM on startup."""
        if self.local_model is None and HAS_TRANSFORMERS:
            try:
                print(f"Loading local RAG Seq2Seq model: {self.local_model_name}...")
                from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
                self.local_tokenizer = AutoTokenizer.from_pretrained(self.local_model_name)
                self.local_model = AutoModelForSeq2SeqLM.from_pretrained(self.local_model_name)
            except Exception as e:
                print(f"Error loading local model components: {e}")
                
    def generate_answer(self, query, context_docs):
        """
        Generate an answer grounded strictly in the provided documents.
        
        Args:
            query: User search query
            context_docs: List of text documents retrieved
            
        Returns:
            Tuple: (answer_string, list_of_referenced_sources)
        """
        if not context_docs:
            return "No relevant documents found in the database to answer your query.", []
            
        # Format the context block with tags
        context_text = "\n\n".join([f"[Source {i+1}]: {doc}" for i, doc in enumerate(context_docs)])
        
        # Option A: Call Hugging Face Serverless API if HF_TOKEN is present
        if self.hf_token:
            try:
                headers = {"Authorization": f"Bearer {self.hf_token}"}
                prompt = (
                    "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
                    "You are a helpful AI assistant. Answer the user's question based strictly on the provided context. "
                    "If the answer cannot be found in the context, say 'I cannot find the answer in the provided documents.' "
                    "Cite your sources using brackets like [Source 1], [Source 2]. Do not make up information.<|eot_id|>"
                    "<|start_header_id|>user<|end_header_id|>\n\n"
                    f"Context:\n{context_text}\n\n"
                    f"Question: {query}<|eot_id|>"
                    "<|start_header_id|>assistant<|end_header_id|>\n\n"
                )
                payload = {
                    "inputs": prompt,
                    "parameters": {"max_new_tokens": 256, "temperature": 0.2}
                }
                api_url = f"https://api-inference.huggingface.co/models/{self.hf_api_model}"
                response = requests.post(api_url, headers=headers, json=payload, timeout=8)
                
                if response.status_code == 200:
                    result = response.json()
                    # Clean output text
                    raw_answer = result[0]["generated_text"]
                    # Extract assistant segment
                    if "<|start_header_id|>assistant<|end_header_id|>" in raw_answer:
                        answer = raw_answer.split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()
                    elif "assistant\n\n" in raw_answer:
                        answer = raw_answer.split("assistant\n\n")[-1].strip()
                    else:
                        answer = raw_answer.replace(prompt, "").strip()
                        
                    answer = answer.replace("<|eot_id|>", "").replace("<|end_of_text|>", "").strip()
                    
                    # Deduce sources
                    sources = []
                    for i in range(len(context_docs)):
                        src_tag = f"Source {i+1}"
                        if src_tag.lower() in answer.lower() or f"[{i+1}]" in answer or f"source {i+1}" in answer.lower():
                            sources.append(src_tag)
                    if not sources:
                        sources = [f"Source {i+1}" for i in range(len(context_docs))]
                        
                    return answer, sources
            except Exception as e:
                print(f"Hugging Face serverless RAG API failed: {e}. Falling back to local model.")
                
        # Option B: Fallback to local seq2seq text generation (Flan-T5-small)
        self._load_local_model()
        if self.local_model and self.local_tokenizer:
            try:
                # Instruction-tuning prompt format for Flan-T5
                prompt = (
                    f"Answer the question based only on the context provided.\n\n"
                    f"Context: {context_text}\n\n"
                    f"Question: {query}\n\n"
                    f"Answer:"
                )
                inputs = self.local_tokenizer(prompt, return_tensors="pt")
                outputs = self.local_model.generate(**inputs, max_length=200)
                answer = self.local_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
                
                # Deduce sources from text
                sources = []
                for i in range(len(context_docs)):
                    src_tag = f"Source {i+1}"
                    if src_tag.lower() in answer.lower() or f"[{i+1}]" in answer or f"source {i+1}" in answer.lower():
                        sources.append(src_tag)
                if not sources:
                    sources = [f"Source {i+1}" for i in range(len(context_docs))]
                    
                return answer, sources
            except Exception as e:
                print(f"Local RAG generation model execution failed: {e}")
                
        # Base hardcoded summary answer if models fail
        first_doc_summary = context_docs[0][:150].replace('\n', ' ')
        return f"Based on retrieved sources, the topic deals with: '{first_doc_summary}...'", ["Source 1"]

