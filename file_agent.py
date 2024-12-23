from swarm import Agent
import os

class FileAgent:
    def read_file(self, file_path: str) -> str:
        """Read contents of a file
        
        Args:
            file_path: Path to the file to read
        """
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def write_file(self, file_path: str, content: str) -> str:
        """Write content to a file
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
        """
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    def list_files(self, directory: str = ".") -> str:
        """List files in a directory
        
        Args:
            directory: Directory path to list files from
        """
        try:
            files = os.listdir(directory)
            return "\n".join(files)
        except Exception as e:
            return f"Error listing files: {str(e)}"

    def create_agent(self) -> Agent:
        """Create and return a Swarm Agent with file capabilities"""
        return Agent(
            name="File Helper",
            model="gemini/gemini-2.0-flash-exp",
            instructions="""You are a helpful AI assistant with file editing capabilities.
            You can read, write and list files when needed.
            Always be careful when modifying files and confirm before making changes.
            Provide clear feedback about file operations.""",
            functions=[self.read_file, self.write_file, self.list_files]
        ) 