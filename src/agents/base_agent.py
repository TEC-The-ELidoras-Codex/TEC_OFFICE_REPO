"""
Base Agent class for all TEC agents.
This serves as the foundation for all agent types in the TEC ecosystem.
"""
import os
import sys
import logging
from typing import Dict, Any, Optional

from dotenv import load_dotenv
import json # Added for agent-specific JSON config
import psycopg2 # Added for PostgreSQL connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseAgent:
    """Base class for all TEC agents to inherit from."""
    
    def __init__(self, name: str, config_path: Optional[str] = None):
        """
        Initialize the base agent with a name and optional configuration.
        
        Args:
            name: Name of the agent
            config_path: Optional path to a main configuration file or directory
        """
        self.name = name
        self.logger = logging.getLogger(f"TEC.{name}")
        self.logger.info(f"Initializing {name} agent")
        
        # Load environment variables from the specific path
        # Assuming project root is two levels up from this file's directory (src/agents)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        env_path = os.path.join(project_root, 'config', '.env')
        load_dotenv(env_path, override=True)
        
        # Load configuration
        self.config: Dict[str, Any] = {}
        self._load_config(config_path, project_root)

        # Initialize database connection placeholder
        self.db_connection: Optional[Any] = None # Replace Any with your DB connection type
        self._connect_db()

        # Initialize LLM client placeholder
        self.llm_client: Optional[Any] = None # Replace Any with your LLM client type
        self._initialize_llm()
    
    def _load_config(self, main_config_path: Optional[str], project_root: str) -> None:
        """
        Load configuration from a main YAML file and an agent-specific JSON file.
        Agent-specific JSON keys will override main YAML keys.
        
        Args:
            main_config_path: Path to the main configuration file or directory containing config.yaml
            project_root: The root directory of the project.
        """
        try:
            # Import yaml with error handling
            try:
                import yaml
            except ImportError:
                self.logger.error("PyYAML not found. Please run 'pip install pyyaml'")
                # We can decide if this is fatal or if we can proceed with defaults/env vars only
                return 

            # Determine path for main config.yaml
            actual_main_config_path = ""
            if main_config_path:
                if os.path.isdir(main_config_path):
                    actual_main_config_path = os.path.join(main_config_path, "config.yaml")
                else:
                    actual_main_config_path = main_config_path
            else: # Default path if none provided
                actual_main_config_path = os.path.join(project_root, "config", "config.yaml")

            if os.path.exists(actual_main_config_path):
                with open(actual_main_config_path, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
                self.logger.info(f"Loaded main configuration from {actual_main_config_path}")
            else:
                self.logger.warning(f"Main configuration file not found: {actual_main_config_path}")

            # Load agent-specific JSON configuration
            agent_config_filename = f"{self.name.lower()}_config.json" # e.g., airth_config.json
            agent_config_path = os.path.join(project_root, "config", "agents", agent_config_filename)
            
            if os.path.exists(agent_config_path):
                with open(agent_config_path, 'r') as f:
                    agent_specific_config = json.load(f)
                self.config.update(agent_specific_config) # Merge, agent-specific overrides
                self.logger.info(f"Loaded and merged agent-specific configuration from {agent_config_path}")
            else:
                self.logger.info(f"No agent-specific configuration file found at {agent_config_path}")

        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            # Continue with empty/partial config rather than failing

    def _connect_db(self) -> None:
        """
        Establish a PostgreSQL database connection using credentials from environment variables
        or the configuration file.
        """
        try:
            db_name = os.getenv("DB_NAME") or self.config.get("database", {}).get("name")
            db_user = os.getenv("DB_USER") or self.config.get("database", {}).get("user")
            db_password = os.getenv("DB_PASSWORD") or self.config.get("database", {}).get("password")
            db_host = os.getenv("DB_HOST") or self.config.get("database", {}).get("host")
            db_port = os.getenv("DB_PORT") or self.config.get("database", {}).get("port", "5432")

            if not all([db_name, db_user, db_password, db_host, db_port]):
                self.logger.warning("Database connection parameters not fully configured. Skipping DB connection.")
                self.db_connection = None
                return

            self.logger.info(f"Attempting to connect to PostgreSQL database: {db_name} at {db_host}:{db_port}")
            self.db_connection = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            self.logger.info("Successfully connected to PostgreSQL database.")
            # You can create a cursor here if needed for immediate operations:
            # cur = self.db_connection.cursor()
            # cur.execute("SELECT version();")
            # db_version = cur.fetchone()
            # self.logger.info(f"PostgreSQL version: {db_version}")
            # cur.close()

        except psycopg2.Error as e:
            self.logger.error(f"Error connecting to PostgreSQL database: {e}")
            self.db_connection = None
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during DB connection: {e}")
            self.db_connection = None

    def _disconnect_db(self) -> None:
        """
        Close the PostgreSQL database connection if it exists.
        """
        if self.db_connection:
            try:
                self.db_connection.close()
                self.logger.info("PostgreSQL database connection closed.")
            except psycopg2.Error as e:
                self.logger.error(f"Error closing PostgreSQL database connection: {e}")
            finally:
                self.db_connection = None

    def _initialize_llm(self) -> None:
        """
        Placeholder for initializing the LLM client.
        Subclasses should override this method.
        """
        self.logger.info("LLM client initialization not implemented in BaseAgent. Override in subclass.")
        # Example:
        # api_key = os.getenv("OPENAI_API_KEY") or self.config.get("llm", {}).get("api_key")
        # if api_key:
        #     self.logger.info("LLM API key found, ready to initialize client.")
        #     # self.llm_client = ... initialize here ...
        # else:
        #     self.logger.warning("LLM API key not configured.")

    def _interact_llm(self, prompt: str, **kwargs) -> Optional[str]:
        """
        Placeholder for interacting with an LLM.
        Subclasses should override this method.
        
        Args:
            prompt: The prompt to send to the LLM.
            **kwargs: Additional arguments for the LLM interaction.
            
        Returns:
            The LLM's response as a string, or None if an error occurs.
        """
        self.logger.warning(f"LLM interaction called with prompt: '{prompt[:50]}...' - Not implemented in BaseAgent.")
        return None

    def perform_task(self, task_description: str, task_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform a specific task. This method should be overridden by subclasses.
        
        Args:
            task_description: A string describing the task to be performed.
            task_details: An optional dictionary containing details or parameters for the task.
            
        Returns:
            A dictionary containing the result of the task execution.
        """
        self.logger.warning(f"perform_task called for '{task_description}' - should be overridden by subclass.")
        return {"status": "not_implemented", "message": "This method should be overridden by the agent subclass."}
    
    def run(self) -> Dict[str, Any]:
        """
        Run the agent's main functionality by calling perform_task.
        This method can be adapted if a more complex lifecycle is needed.
        
        Returns:
            Dict containing the result of the agent's execution
        """
        self.logger.info(f"Agent {self.name} starting run...")
        # Default task, can be made more dynamic or configured
        result = self.perform_task(f"Default task for {self.name}", {}) 
        self.logger.info(f"Agent {self.name} run completed.")
        return result

    def __del__(self):
        """Ensure resources like database connections are cleaned up."""
        self.logger.info(f"Cleaning up agent {self.name}.")
        self._disconnect_db()

# Example usage (for testing purposes, typically not here)
if __name__ == '__main__':
    # This assumes your project structure allows this import path
    # and that config files might be in ../../config/
    # You might need to adjust paths or run from the project root.
    import yaml # Added import for the example
    import json # Added import for the example (already present globally but good for standalone example)
    import os # Added import for the example (already present globally)
    
    # Create a dummy config.yaml for testing
    dummy_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    dummy_config_dir = os.path.join(dummy_project_root, 'config')
    dummy_agent_config_dir = os.path.join(dummy_config_dir, 'agents')
    
    os.makedirs(dummy_config_dir, exist_ok=True)
    os.makedirs(dummy_agent_config_dir, exist_ok=True)

    with open(os.path.join(dummy_config_dir, 'config.yaml'), 'w') as f:
        yaml.dump({'general_setting': 'hello_world', 'database': {'host': 'db.example.com'}}, f)
    
    with open(os.path.join(dummy_agent_config_dir, 'testagent_config.json'), 'w') as f:
        json.dump({'agent_specific_setting': 'test_value', 'database': {'host': 'override.db.example.com'}}, f)

    print(f"Dummy project root for test: {dummy_project_root}")
    print(f"Attempting to load main config from: {os.path.join(dummy_config_dir, 'config.yaml')}")
    print(f"Attempting to load agent config from: {os.path.join(dummy_agent_config_dir, 'testagent_config.json')}")

    agent = BaseAgent(name="TestAgent", config_path=dummy_config_dir)
    print(f"Agent Config: {agent.config}")
    agent.run()

    # Clean up dummy files
    # os.remove(os.path.join(dummy_config_dir, 'config.yaml'))
    # os.remove(os.path.join(dummy_agent_config_dir, 'testagent_config.json'))
    # os.rmdir(dummy_agent_config_dir)
    # os.rmdir(dummy_config_dir)
