## Python Migration Guide: Vertex AI to Google Gen AI SDK

The **Vertex AI SDK (google-cloud-aiplatform)** will be deprecated after June 24, 2026. Migrate to the **Google Gen AI SDK (google-genai)**.

### Key Changes & Migration Steps:

* **Installation:**
    * **Before:** `pip install -U -q "google-cloud-aiplatform"`
    * **After:** `pip install -U -q "google-genai"`

* **Imports:**
    * Replace `from google.cloud import aiplatform`, `import vertexai`, `from vertexai.generative_models import GenerativeModel, Image` with `from google import genai`, `from google.genai.types import ...`, `from google.genai import Client`.

* **Initialization:**
    * **Vertex AI SDK:** `vertexai.init(project=..., location=...)`
    * **Google Gen AI SDK:** `client = genai.Client(http_options=HttpOptions(api_version="v1"))` (or `client = Client(vertexai=True, project=..., location=...)` for grounding).

* **Context Caching:**
    * **Create:** `vertexai.caching.CachedContent.create(...)` becomes `client.caches.create(...)`.
    * **Get:** `vertexai.caching.CachedContent.get(...)` becomes `client.caches.list()` and iterate.
    * **Delete:** `cache_content.delete()` becomes `client.caches.delete(name=cache_name)`.
    * **Update:** `cache_content.update(...)` becomes `client.caches.update(...)`.
    * **List:** `vertexai.caching.CachedContent.list()` becomes `client.caches.list()`.

* **Configuration & System Instructions:**
    * `GenerativeModel(..., system_instruction=..., generation_config=..., safety_settings=...)` becomes `client.models.generate_content(model=..., contents=..., config=types.GenerateContentConfig(system_instruction=..., max_output_tokens=..., temperature=..., safety_settings=[...]))`.

* **Embeddings:**
    * `vertexai.vision_models.MultiModalEmbeddingModel.from_pretrained(...).get_embeddings(...)` becomes `client.models.embed_content(model="gemini-embedding-001", contents=..., config=types.EmbedContentConfig(...))`.

* **Function Calling:**
    * `generative_models.FunctionDeclaration`, `generative_models.Tool`, `model.start_chat()`, `chat.send_message(...)`, `Part.from_function_response(...)` are replaced by defining a Python function and passing it to `config=types.GenerateContentConfig(tools=[your_function])` in `client.models.generate_content(...)`.

* **Grounding (Google Search Retrieval):**
    * `generative_models.Tool.from_Google Search_retrieval(...)` becomes `config=types.GenerateContentConfig(tools=[types.Tool(Google Search=types.GoogleSearch())])` in `client.models.generate_content(...)` after initializing `Client(vertexai=True, project=..., location=...)`.

* **Safety Settings:**
    * `safety_settings={generative_models.HarmCategory.HARM_CATEGORY_...: generative_models.HarmBlockThreshold....}` becomes `config=types.GenerateContentConfig(safety_settings=[types.SafetySetting(category='HARM_CATEGORY_...', threshold='BLOCK_ONLY_HIGH')])`.

* **Chat Sessions:**
    * **Before:** `model.start_chat()`, `chat.send_message(...)`.
    * **After:** `chat = client.chats.create(model=...)`, `response = chat.send_message(...)` (synchronous) or `chat = client.aio.chats.create(model=...)`, `response = await chat.send_message(...)` (asynchronous). Streaming also available (`send_message_stream`).

* **Multimodal Inputs:**
    * **Before:** `Image.load_from_file(...)`, `generative_models.Part.from_uri(...)`.
    * **After:** `Part.from_uri(file_uri=..., mime_type=...)` directly in `client.models.generate_content(contents=[Part.from_uri(...)])`.

* **Text Generation:**
    * **Synchronous:** `model.generate_content(...)` becomes `client.models.generate_content(model=..., contents=...)`.
    * **Asynchronous:** `await model.generate_content_async(...)` becomes `await client.aio.models.generate_content(model=..., contents=...)`.
    * **Streaming:** `model.generate_content(stream=True)` becomes `for chunk in chat.send_message_stream(...)` (sync) or `async for chunk in await chat.send_message_stream(...)` (async).