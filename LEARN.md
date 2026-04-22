# Learning Guide: Ollama Chainlit Application

This guide helps you understand, configure, and extend the Ollama-powered Chainlit application in this repository. It covers prerequisites, environment setup, how the app flows, supported features (file processing, chat profiles, MCP tools, persistence), and common customization points.

## Quick Start

### What You'll Need

- [Python 3.13+](https://www.python.org/downloads/) installed

- [Basic Python knowledge](https://www.geeksforgeeks.org/python/python-programming-language-tutorial/)

- [uv package manager](https://docs.astral.sh/uv/getting-started/installation/)

- [Ollama Cloud Account](https://ollama.com/cloud) (free tier)

- [ElevenLabs API Key](https://elevenlabs.io/pricing/api)

- [PostgreSQL installer](https://www.postgresql.org/download/) or [Supabase](https://supabase.com/docs/guides/database/connecting-to-postgres#pooler-session-mode)

- Create an [Auth0 app](https://auth0.com/docs/get-started/auth0-overview/create-applications) or [GitHub OAuth app](https://github.com/settings/apps)

- [Create an Azure storage account](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-create?toc=%2Fazure%2Fstorage%2Fblobs%2Ftoc.json&tabs=azure-portal) (optional)

- [Railway Account](https://railway.com/) (optional)

- Code editor of choice

### Installation & Setup

1.**Clone the Repository**

```bash
git clone https://github.com/EliAbdiel/ollama-chat-application.git

cd ollama-chat-application
```

2.**Install dependencies**

```bash
uv sync
```

3.**Create and fill .env**

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

4.**Run the app**

```bash
# Linux/Mac
source .venv/bin/activate

# Windows (CMD)
.venv\Scripts\activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

chainlit run mani.py -w
```

## Environment Variables

The app reads configuration from `.env` via `src/utils/config.py`. All keys are required unless noted.

- `OLLAMA_SECRET_KEY`: Bearer token for Ollama API (if your deployment requires auth).
- `OLLAMA_BASE_URL`: Base URL for your Ollama server (e.g., `https://ollama.com` or a hosted endpoint).
- `DEFAULT_MODEL`: Fallback text model used when no profile mapping is found.
- `VISION_MODEL`: Vision-capable model used for image analysis.
- `ELEVENLABS_API_KEY`: API key for ElevenLabs transcription (voice input).
- `LOCAL_DATABASE`: SQLAlchemy connection string (e.g., `sqlite+aiosqlite:///chainlit.db` or `postgresql+asyncpg://user:pass@host/db`).
- `CONTAINER_NAME`: Azure Blob container name for storage of files.
- `STORAGE_ACCOUNT_NAME`: Azure Storage account name.
- `STORAGE_KEY`: Azure Storage account key.

Example `.env`:

```
OLLAMA_SECRET_KEY=your_ollama_token
OLLAMA_BASE_URL=https://ollama.com
DEFAULT_MODEL=deepseek-v3.1:671b
VISION_MODEL=qwen3-vl:235b

ELEVENLABS_API_KEY=your_elevenlabs_key

LOCAL_DATABASE=sqlite+aiosqlite:///chainlit.db
CONTAINER_NAME=yourcontainer
STORAGE_ACCOUNT_NAME=youraccount
STORAGE_KEY=yourkey
```

## Project Structure

- `main.py`: Entry point and Chainlit callbacks.
- `src/llm/call_model.py`: Ollama chat loop, MCP tool-calls, and profile→model mapping.
- `src/document/`: Document processing and configuration.
- `src/ui/`: Chat profiles, starters, and chat resume helpers.
- `src/database/persistent_data_layer.py`: SQLAlchemy data layer and Azure storage client setup.
- `src/log/logger.py`: Simple logger helper.
- `.chainlit/config.toml`: Chainlit feature flags (file upload, MCP, UI options).
- `public/`: Static assets (icons, logos).

## How the App Works

1. Session setup
   - `@cl.on_chat_start` initializes `chat_history` and `mcp_tools` in the user session.
2. MCP tooling discovery
   - `@cl.on_mcp_connect` lists tools from connected MCP servers and caches them in `mcp_tools`.
3. Message handling
   - `@cl.on_message` receives text and optional file attachments.
   - If files are attached, `DocumentProcessor.process_single_file_async` extracts/summarizes content and appends it to the user message.
   - The selected chat profile maps to an Ollama model via `model_name`.
   - `call_ollama` runs a streaming chat loop and, if the model requests a tool, automatically calls the matching MCP tool and feeds results back to the model.
4. Persistence
   - `@cl.data_layer` configures the SQLAlchemy data layer with Azure Blob storage for file content.
5. Resume threads
   - `@cl.on_chat_resume` rebuilds `chat_history` from archived thread steps, allowing continuation of past conversations.
6. Voice input
   - `@cl.on_audio_chunk` buffers microphone audio and `@cl.on_audio_end` transcribes it via ElevenLabs, then routes the text into `on_message`.

## Running Locally

- Start your Ollama server and ensure `OLLAMA_BASE_URL` is reachable.
- Confirm models referenced in your configuration are available on your Ollama server.
- Launch the app: `chainlit run main.py -h`.
- Open the UI in your browser; select a chat profile, and start chatting or upload files.

## Chat Profiles

Defined in `src/ui/chat_profiles.py`. Each profile has:

- `name`: A label shown in the UI and used for mapping.
- `markdown_description`: Shown to users in the profile picker.
- `icon`: Path in `public/model/`.

Profile names map to Ollama models in `model_name` (in `src/llm/call_model.py`). If a profile isn’t recognized, the app uses `DEFAULT_MODEL`.

To add a new profile:

- Add a `cl.ChatProfile` entry in `src/ui/chat_profiles.py`.
- Update `model_name` mapping in `src/llm/call_model.py` to return your Ollama model string.
- Add an icon under `public/model/`.

## Document & Image Processing

Implemented in `src/document/document_processor.py` with settings in `src/document/processor_config.py`.

- Supported file types: `.pdf`, `.docx`, `.txt`, `.jpg`, `.jpeg`, `.png`.
- Validation: extension, MIME type, file size, basic filename safety.
- Text documents: extracted and summarized using the text model (`ProcessingConfig.ollama_model`).
- Images: analyzed using the vision model (`ProcessingConfig.vision_model`) with a structured prompt; results are summarized.
- Limits: `text_extract_limit` and `max_file_size` configurable via `ProcessingConfig`.

To support new file types:

- Extend `ProcessingConfig.allowed_extensions` and `allowed_mime_types`.
- Add a processor in `DocumentProcessor.file_processor_map` and implement the extraction method.

## MCP Tooling

MCP (Model Context Protocol) tooling is enabled in `.chainlit/config.toml` under `[features.mcp]`. When the model issues a tool call, the app:

- Looks up the tool by name in `mcp_tools` derived from connected MCP servers.
- Executes the tool through the MCP session.
- Appends the tool output back to the conversation as a `tool` role message.

Notes:

- Stdio connections are allowed for executables listed in `allowed_executables` (e.g., `uv`, `uvx`, `npx`). Ensure your MCP server is reachable via the chosen transport (stdio, SSE, or HTTP) and exposes tools via `list_tools`.

### Manual tool invocation helper

- A utility step is available to call a specific tool by name during a thread: it locates the MCP connection exposing the tool and invokes it with arguments, returning JSON output.

#### Basic Usage

| MCP Connection is established | Tavily MCP Server | GitHub MCP Server |
|:-----------------------------:|:-----------------:|:-----------------:|
|![MCP Server](public/gif/mcp-connection.gif)|![Tavily MCP](public/gif/tavily-mcp-server.gif)|![GitHub MCP](public/gif/github-mcp-server.gif)|

## Persistence & Storage

- Data layer: `SQLAlchemyDataLayer` initialized in `src/database/persistent_data_layer.py` with `LOCAL_DATABASE`.
- File storage: `AzureBlobStorageClient` configured by `CONTAINER_NAME`, `STORAGE_ACCOUNT_NAME`, `STORAGE_KEY`.

Examples:

- SQLite (local dev): `LOCAL_DATABASE=sqlite+aiosqlite:///chainlit.db`
- Postgres: `LOCAL_DATABASE=postgresql+asyncpg://user:pass@host/db`

### Database Setup

The system uses PostgreSQL for data persistence. Here's the database schema:

```sql
CREATE TABLE users (
    "id" UUID PRIMARY KEY,
    "identifier" TEXT NOT NULL UNIQUE,
    "metadata" JSONB NOT NULL,
    "createdAt" TEXT
);

CREATE TABLE IF NOT EXISTS threads (
    "id" UUID PRIMARY KEY,
    "createdAt" TEXT,
    "name" TEXT,
    "userId" UUID,
    "userIdentifier" TEXT,
    "tags" TEXT[],
    "metadata" JSONB,
    FOREIGN KEY ("userId") REFERENCES users("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS steps (
    "id" UUID PRIMARY KEY,
    "name" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "threadId" UUID NOT NULL,
    "parentId" UUID,
    "streaming" BOOLEAN NOT NULL,
    "waitForAnswer" BOOLEAN,
    "isError" BOOLEAN,
    "metadata" JSONB,
    "tags" TEXT[],
    "input" TEXT,
    "output" TEXT,
    "createdAt" TEXT,
    "command" TEXT,
    "start" TEXT,
    "end" TEXT,
    "generation" JSONB,
    "showInput" TEXT,
    "language" TEXT,
    "indent" INT,
    "defaultOpen" BOOLEAN,
    FOREIGN KEY ("threadId") REFERENCES threads("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS elements (
    "id" UUID PRIMARY KEY,
    "threadId" UUID,
    "type" TEXT,
    "url" TEXT,
    "chainlitKey" TEXT,
    "name" TEXT NOT NULL,
    "display" TEXT,
    "objectKey" TEXT,
    "size" TEXT,
    "page" INT,
    "language" TEXT,
    "forId" UUID,
    "mime" TEXT,
    "props" JSONB,
    FOREIGN KEY ("threadId") REFERENCES threads("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS feedbacks (
    "id" UUID PRIMARY KEY,
    "forId" UUID NOT NULL,
    "threadId" UUID NOT NULL,
    "value" INT NOT NULL,
    "comment" TEXT,
    FOREIGN KEY ("threadId") REFERENCES threads("id") ON DELETE CASCADE
);

ALTER TABLE elements ADD COLUMN IF NOT EXISTS "autoPlay" BOOLEAN DEFAULT false;

ALTER TABLE steps ADD COLUMN IF NOT EXISTS "autoCollapse" BOOLEAN DEFAULT false;

ALTER TABLE steps ADD COLUMN IF NOT EXISTS "defaultOpen" BOOLEAN DEFAULT false;
```

## Logging

- `setup_logger` configures a simple `StreamHandler` with `INFO` level.
- Logs are emitted from core modules to help trace message flow, file handling, and tool calls.

## Chainlit UI & Uploads

Key settings in `.chainlit/config.toml`:

- File upload: `[features.spontaneous_file_upload]` accepts `*/*`, up to `500MB`, max `20` files.
- MCP: Multiple transports enabled (`stdio`, `sse`, `streamable-http`).
- UI options: alert style, CoT display (`cot = "full"`), optional custom CSS/JS.

You can tweak these without code changes to adjust the front-end experience and feature flags.

### Audio & Voice

- Audio input is enabled via `[features.audio]` with `enabled = true` and `sample_rate = 24000`.
- On audio end, recorded chunks are assembled into a WAV buffer and transcribed using ElevenLabs `scribe_v1`.
- The transcription is posted as a user message and processed like any text input.

## Common Tasks

- Install dependencies: `pip install .` or `uv pip sync`.
- Run dev server: `chainlit run main.py -h`.
- Change the welcome screen: edit `chainlit.md`.
- Add a chat profile: edit `src/ui/chat_profiles.py` and `src/llm/call_model.py`.
- Tune document processing: adjust `src/document/processor_config.py`.
- Switch database: update `LOCAL_DATABASE` in `.env`.

## Troubleshooting

- Missing env vars: `KeyError` on startup indicates a required key is unset; verify `.env` and reload.
- Ollama connectivity: ensure `OLLAMA_BASE_URL` is reachable; confirm model names exist on your server.
- Tool call errors: check MCP server is running and that the tool name matches what the model requests.
- File type mismatch: invalid MIME or unsupported extension triggers validation errors; verify the upload and allowed types.
- Azure storage: confirm container/account/key are correct and the account has permissions.

## Authentication

- OAuth callback is implemented to support provider-based sign-in.
- Configure providers and UI in Chainlit settings if you plan to enable login flows.

## Extensibility Tips

- New models: add a profile and mapping; set `DEFAULT_MODEL` to the most stable model for fallbacks.
- Custom prompts: refine summarization in `DocumentProcessor._clean_and_summarize_text` and image analysis prompts.
- New tools: run an MCP server exposing your functions; the app auto-discovers tools on connect.
- Security: consider tightening upload `accept` types and lowering size limits in `.chainlit/config.toml` for production.

## Deploying your project from GitHub

>Railway is an all-in-one intelligent cloud provider that makes it easy to provision infrastructure, develop locally, and deploy to the cloud.

To get started deploying your *ollama chat application*, it is recommended to [forking](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) the previously configure [chainlit app](https://github.com/EliAbdiel/ollama-chat-application.git) repository so that you can follow along.

First make a [new project](https://docs.railway.com/overview/the-basics#project--project-canvas).

- Open up the [dashboard](https://docs.railway.com/overview/the-basics#dashboard--projects) $\rightarrow$ Click **New Project**.

- Choose the **GitHub repo** option.

   ![New project and choose the GitHub repo](/public/railway/railway-new-project.png)

   >Railway requires a valid GitHub account to be linked. If your Railway account isn't associated with one, you will be prompted to link it.

- Search for your GitHub project and click on it.

   ![Search for your github project](/public/railway/search-your-github-project.png)

- Choose either **Deploy Now** or **Add variables**.

    *Deploy Now* will immediately start to build and deploy your selected repo.

    *Add Variables* will bring you to your service and ask you to add variables, when done you will need to click the Deploy button at the top of your canvas to initiate the first deployment.

   ![Deploy now or add variables](/public/railway/deploy-or-add-variables.png)

- Expose your Railway services to the internet via `HTTP`/`HTTPS`.

    1. Go to your service's **Settings**.
    2. Find **Networking** $\rightarrow$ **Public Networking**.
    3. Click **Generate Domain** to get a Railway-provided domain.

   ![Public networking](/public/railway/public-networking.png)

- Override the detected *start command* by setting a value in your service **Settings**.

   Go to your service's **Settings** $\rightarrow$ **Deploy** $\rightarrow$ **Custom Start Command**

   ![Custom start command](/public/railway/start-command.png)

- Set the `CHAINLIT_URL` environment variable. For instance, if you host your application at `https://mydomain.com`, `CHAINLIT_URL` should be set to `https://mydomain.com`

- Go to your GitHub OAuth apps, set the callback URL should be: `CHAINLIT_URL/auth/oauth/github/callback`.

   ![GitHub OAuth app](/public/railway/chainlit-url.png)

- Test your deployed app

   ![Test deploy chat](/public/gif/streaming-response.gif)

## References

- [Chainlit documentation](https://docs.chainlit.io/get-started/overview)

- [Ollama documentation](https://docs.ollama.com/cloud)

- [Create a new GitHub OAuth app](https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/about-creating-github-apps#building-a-github-app)

- [Create an Auth0 application](https://auth0.com/docs/get-started/auth0-overview/create-applications)

- [Azure Storage documentation](https://learn.microsoft.com/en-us/azure/storage/)

- [Railway documentation](https://docs.railway.com/quick-start)