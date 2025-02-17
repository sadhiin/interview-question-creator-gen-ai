QUESTION_PROMPT_TEMPLATE = """You are an expert at analyzing documents and creating comprehensive questions. Your task is to generate 3-4 high-quality questions from the given text. Follow these guidelines:

1. Create questions that cover different aspects:
   - Main concepts and key ideas
   - Important details and specific information
   - Relationships between different concepts
   - Technical terms and their meanings
   - Practical applications or implications

2. Questions should be:
   - Clear and well-formulated
   - Specific to the content provided
   - Varied in complexity (mix of straightforward and analytical questions)
   - Focused on important information
   - End with a question mark

3. Avoid:
   - Repetitive or overlapping questions
   - Overly simple yes/no questions
   - Questions about irrelevant details
   - Ambiguous or unclear questions

Here is the text to analyze:
{text}

Generate questions that would help someone thoroughly understand this content. Each question should be on a new line."""