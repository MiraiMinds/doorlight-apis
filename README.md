# hunkermoller Voicebot

## Project Structure

- **`client/`**: Frontend source code directory
- **`server/`**: Backend source code directory
- **`Dockerfile`**: Docker configuration file
- **`README.md`**: Project documentation (you're reading it!)

## Prerequisites

To run this project, you'll need the following installed on your system:

- **Python**: Version 3.12 or higher
- **Node.js**: Version 20.18
- **`uv`**: A Python package and project manager

## Installation

Follow these steps to set up and run the Hunkermoller project.

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone <repository-url>
cd hunkermoller/server
mv .env.sample .env
```

### 2 backend: Set Up the Virtual Environment and Install Dependencies

```bash
uv venv
source .venv/bin/activate
uv pip sync pyproject.toml
```

### 3 Setup shopify-mcp
```bash
cd hunkermoller/server/mcp_servers/
git clone git@github.com:MiraiMinds/shopify-mcp-server.git mcp-shopify
cd mcp-shopify
npm install
npm run build
```

### 4 Run the server

```bash
uv run app.py
```

### 5 frontend: Set Up the Virtual Environment and Install Dependencies

- **Open New Terminal Window**  
   (Keep the backend server running in the original terminal)

```bash
cd client
npm install
```

### 5 Run the client

```bash
npm run dev
```

## Running with Docker

You can also run the Hunkermoller project using Docker, which will handle both the frontend and backend in a single container.

### 1. Update the .env File

Before building the Docker image, ensure you have updated the `.env` file in the `server/` directory with your desired environment variables (e.g., `OPENAI_API_KEY`, `BOT_LANGUAGE_NAME`, `BOT_LANGUAGE_CODE`, `VITE_API_DOMAIN`). The Dockerfile will use these values during the build process.

### 2. Build the Docker Image

From the root directory of the project (where the Dockerfile is located), build the Docker image:

```bash
docker build -t hunkermoller .
```

### 3. Run the Docker Container

Run the container, mapping port 8080 on your host to port 8080 in the container:

```bash
docker run -d -p 8080:8080 hunkermoller
```

### 4. Access the Application

Once the container is running, you can access the application at:

```
http://localhost:8080
```
