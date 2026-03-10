import os
import json
import google.generativeai as genai
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class AIMapper:
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API Key is required.")
        genai.configure(api_key=api_key)
        # Try a few common model names to ensure compatibility
        self.model_names = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro']
        self.current_model_index = 0
        self._init_model()

    def _init_model(self):
        model_name = self.model_names[self.current_model_index]
        self.model = genai.GenerativeModel(model_name)

    def find_best_match(self, source_tables: List[Dict[str, Any]], zoho_dataset: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses Gemini to find the best matching table from the source (PDF/Excel/CSV) 
        and map its columns to the merged Zoho dataset.
        """
        
        prompt = f"""
        You are an expert data architect. I have source data (extracted from PDF tabs, Excel sheets, or CSVs) 
        and a merged Zoho Analytics dataset. I need to identify which source table matches the Zoho data.

        ZOHO DATASET (MERGED):
        Columns: {zoho_dataset['columns']}
        Sample Data: {json.dumps(zoho_dataset['sample_rows'][:2])}
        
        SOURCE TABLES TO CHOOSE FROM:
        {json.dumps([{ 'name': t['name'], 'columns': t['columns'], 'sample': t['sample_rows'][:1] } for t in source_tables], indent=2)}
        
        Rules:
        1. Compare column names and sample data patterns. Note: column names are normalized (lowercase_underscores).
        2. Identify the source table that is the "parent" or "source" for the Zoho dataset.
        3. Create a mapping from Source Column -> Zoho Column.
        4. Provide a confidence score between 0.0 and 1.0.
        
        Return ONLY a JSON object:
        {{
            "best_match_sheet": "NAME_OF_SOURCE_TABLE",
            "confidence": 0.95,
            "column_mapping": {{
                "source_col_1": "zoho_col_a",
                "source_col_2": "zoho_col_b"
            }},
            "reasoning": "Brief explanation of why this match was chosen"
        }}
        """
        
        last_exception = None
        for _ in range(len(self.model_names)):
            response = None
            try:
                response = self.model.generate_content(prompt)
                # Successful response!
                clean_res = response.text.strip().replace("```json", "").replace("```", "")
                return json.loads(clean_res)
            except Exception as e:
                last_exception = e
                # If it's a 404/not found error, try the next model
                if "404" in str(e) or "not found" in str(e).lower():
                    self.current_model_index = (self.current_model_index + 1) % len(self.model_names)
                    self._init_model()
                    print(f"Falling back to model: {self.model_names[self.current_model_index]}")
                    continue
                else:
                    # Generic error handling
                    raw_text = "No response text"
                    if response:
                        try:
                            raw_text = response.text
                        except:
                            raw_text = str(response)
                    return {
                        "error": f"AI Mapping failed: {str(e)}",
                        "raw_response": raw_text
                    }
        
        return {
            "error": f"AI Mapping failed after trying all models. Last error: {str(last_exception)}",
            "raw_response": "All fallback models failed."
        }

if __name__ == "__main__":
    print("Upgraded AIMapper loaded.")
