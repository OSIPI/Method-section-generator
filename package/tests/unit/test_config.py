import os
import tempfile
import yaml
from pyaslreport.core.config import Config


def test_config_load_with_minimal_yaml():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create allowed_file_types.yaml
        allowed_file_types_path = os.path.join(tmpdir, "allowed_file_types.yaml")
        with open(allowed_file_types_path, "w") as f:
            yaml.dump({
                "allowed_file_types": ["json"],
                "paths": {"input": "in", "output": "out"}
            }, f)

        # Create schemas directory
        schemas_dir = os.path.join(tmpdir, "schemas")
        os.makedirs(schemas_dir)

        schema_file = os.path.join(schemas_dir, "test_schema.yaml")
        with open(schema_file, "w") as f:
            yaml.dump({"TestSchema": {"field": "value"}}, f)

        config = Config(tmpdir)
        loaded = config.load()

        assert "allowed_file_type" in loaded
        assert "schemas" in loaded
        assert "TestSchema" in loaded["schemas"]