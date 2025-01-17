import json
import logging
import os
from typing import Dict, Any

def load_config(config_file: str) -> Dict[str, Any]:
    """
    Load and validate configuration from a JSON file.
    
    Args:
        config_file (str): Path to the configuration JSON file
        
    Returns:
        dict: Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file isn't valid JSON
        KeyError: If required keys are missing
    """
    try:
        # Check if file exists
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
            
        # Read and parse JSON
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        # Required configuration keys
        required_keys = ['base_url', 'jwt_token']
        
        # Validate required keys exist
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise KeyError(f"Missing required configuration keys: {', '.join(missing_keys)}")
            
        # Log successful config load without sensitive info
        safe_keys = [k for k in config.keys() if k not in ['jwt_token', 'password']]
        logging.info(f"Successfully loaded configuration with keys: {safe_keys}")
        
        return config
        
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse configuration file: {str(e)}")
        raise
        
    except Exception as e:
        logging.error(f"Error loading configuration: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage and testing
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Test the config loader
        config_file = 'openmetadata_config.json'
        config = load_config(config_file)
        print("Configuration loaded successfully!")
        print("Available keys:", [k for k in config.keys() if k not in ['jwt_token', 'password']])
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)