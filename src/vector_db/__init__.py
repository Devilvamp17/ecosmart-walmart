import json
import chromadb
from google import genai
import os

class VectorDB:
    def __init__(self, sku_map_data):
        self.chroma_client = chromadb.Client()
        self.genai_client = genai.Client(api_key="AIzaSyC-FGEwwx4ZUXLB64B5X-bveI0El1J5gR8")
        
        # Ensure the collection is created or retrieved
        try:
            self.collection = self.chroma_client.get_collection(name="catalog")
        except Exception: # Collection does not exist, create it
            self.collection = self.chroma_client.create_collection(name="catalog")

        if sku_map_data:
            documents = []
            metadatas = []
            ids = []
            for item_name, item_details in sku_map_data.items():
                documents.append(json.dumps({"name": item_name, "details": item_details}))
                metadatas.append({'name': item_name})
                ids.append(item_name)
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Loaded {len(sku_map_data)} items into the collection.")

    def query(self, query_text, top_k=5):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k
        )['documents']
        
        response = self.genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Query: {query_text}\nResults: {results}. For each item, provide its carbon footprint and suggest sustainable alternatives. If no carbon footprint or alternative is found, state that.",
            config=genai.types.GenerateContentConfig(
                system_instruction="You are an AI assistant providing information about grocery items. Given a query and relevant item data, generate a concise response that includes the item's carbon footprint and sustainable alternatives. If information is not available, state that clearly. Do not use markdown formatting, just write simple text.",
            )
        )

        return response.text if response else "No results found or error in generating response."


