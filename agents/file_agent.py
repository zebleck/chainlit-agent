from swarm import Agent
import os
import shutil
import subprocess


class FileAgent:
    def create_dir(self, directory: str) -> str:
        """Create a new directory

        Args:
            directory: Path of directory to create
        """
        try:
            os.makedirs(directory, exist_ok=True)
            return f"Successfully created directory: {directory}"
        except Exception as e:
            return f"Error creating directory: {str(e)}"

    def read_file(self, file_path: str) -> str:
        """Read contents of a file

        Args:
            file_path: Path to the file to read
        """
        try:
            with open(file_path, "r") as f:
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
            with open(file_path, "w") as f:
                f.write(content.encode("utf-8").decode("unicode_escape"))
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

    def copy_file(self, source_path: str, dest_path: str) -> str:
        """Copy a file from source to destination

        Args:
            source_path: Path of the file to copy
            dest_path: Destination path for the copy
        """
        try:
            shutil.copy2(source_path, dest_path)
            return f"Successfully copied {source_path} to {dest_path}"
        except Exception as e:
            return f"Error copying file: {str(e)}"

    def run_python_code(self, file_path: str) -> str:
        """Runs an existing python code file and returns the output
        Args:
            file_path: Path to the python file to run
        """
        try:
            result = subprocess.run(
                ["python", file_path], capture_output=True, text=True, check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error running code: {e.stderr}"
        except Exception as e:
            return f"Error running code: {str(e)}"

    def create_agent(self) -> Agent:
        """Create and return a Swarm Agent with file capabilities"""
        return Agent(
            name="File Helper",
            model="gemini/gemini-2.0-flash-exp",
            instructions="""You are a helpful AI assistant with file editing capabilities.
            You can read, write, copy and list files when needed.
            You can create directories when needed.
            You can also run python code files.
            You can chain together functions to perform complex tasks.
            Always be careful when modifying files and confirm before making changes.
            Provide clear feedback about file operations.""",
            functions=[
                self.create_dir,
                self.read_file,
                self.write_file,
                self.list_files,
                self.copy_file,
                self.run_python_code,
            ],
        )
