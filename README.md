# Chainlit x Swarm

A chat interface combining Chainlit's UI capabilities with Open-Swarm's agent system to create an interactive AI-powered conversation platform.

## Features

- **Multiple Specialized Agents:**
  - SQL Agent: Database operations and queries
  - Selenium Agent: Web automation and scraping
  - CLI Agent: Command-line operations and process management
  - File Agent: File system operations

- **Real-time Process Monitoring:**
  - Live output from running processes
  - Command execution feedback
  - Process management capabilities

- **Web Automation:**
  - Browser control through Selenium
  - Page navigation and interaction
  - Element inspection and manipulation

- **Database Operations:**
  - SQL query execution
  - Schema inspection
  - Table management

## Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chainlit-swarm.git
cd chainlit-swarm
```

2. Create a `.env` file with your configuration:
```env
GEMINI_API_KEY=your_api_key
ODBC_CONNECTION_STRING=your_connection_string
ADMIN_QUERY=your_admin_query
```

`ODBC_CONNECTION_STRING` and `ADMIN_QUERY` are used for the SQL Agent.

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

4. Access the interface at `http://localhost:8000`

### Manual Installation

1. Install dependencies:
```bash
pip install .
```

2. Run the application:
```bash
chainlit run app.py
```

## Usage

### SQL Operations
```python
# Example SQL query
"Show me all tables in the database"
"Get the schema for users table"
```

### Web Automation
```python
# Example web automation
"Navigate to google.com"
"Click the search button"
```

### CLI Operations
```python
# Example CLI commands
"Start npm run swall in the frontend directory"
"Show me the current process output"
```

## Development

### Project Structure
```
chainlit-swarm/
├── agents/
│   ├── sql_agent.py
│   ├── selenium_agent.py
│   ├── cli_agent.py
│   └── file_agent.py
├── app.py
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

### Adding New Agents

1. Create a new agent file in the `agents` directory
2. Implement the agent class with required methods
3. Add the agent to `app.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see [LICENSE.md](LICENSE.md) for details

## Acknowledgments

- [Chainlit](https://github.com/Chainlit/chainlit)
- [Open-Swarm](https://github.com/marcusschiesser/open-swarm)
```

This README now includes:
1. Detailed feature list
2. Installation instructions for both Docker and manual setup
3. Usage examples
4. Project structure
5. Development guidelines
6. Contributing instructions

Let me know if you'd like to add or modify any sections!
