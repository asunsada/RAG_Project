Langchain RAG_Project

This is a sample project of RAG (Retrieval Augmented Generation as a Service)

Please note I am not a professional developer. I just love tech.

Thank you to all those people who are sharing their knowledge openly in different media.

Please note you will need to Install dependencies. Depending on your system and set up, you will need to install different packages.
As you run and debug your code, you will be able to learn which ones.

You'll also need to set up an OpenAI account (and set the OpenAI key in your environment variable) for this to work. Quick tutorial to set Python: https://platform.openai.com/docs/quickstart?context=python including how to set the API Key https://platform.openai.com/api-keys.


Make domain data available to the program, Load it, process it, embed it and load it in a Chroma DB.

```python
python Loader.py
```

Query the Chroma DB. Retrieve the relevant Domain data chunks, enhance the promot, call OpenAI LLM
and generate the answer 

```python
python query_data.py "How do the different AI strategies of Cisco, Amazon, Alphabet and Meta compare?"
```

