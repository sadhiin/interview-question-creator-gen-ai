question_prompt_template = """
You are an expret at creating questions based on python and coding.
Your goal is to prepare a good programmer for their exam and coding tests for evaluation.
You do this by asking question about the information below:
------
{text}
------
Create questions that will prepare a programmer for their test. Make sure not to loss any important topic or information.

Questions:
"""


refine_template = ("""
You are an expert at creating practice question based on coding. Your goal is to help a programmer prepare for a coding test.
We have received some practice question to a certain extent, {existing_answer}
We have option to refine the existing question or add new ones.
(only if necessary) with some more context below.
----
{text}
----
Given the new context. refine the original question in English.
If the context is not helpful, please provide the original question.
Questions:
"""
)