import io
from pyapns_client import TokenBasedAuth


class TestTokenBasedAuth:
    def test_get_auth_key_file(self, tmp_path):
        # Create a temporary file containing the auth key
        auth_key = "my_auth_key"
        auth_key_path = tmp_path / "auth_key.txt"
        with open(auth_key_path, "w") as f:
            f.write(auth_key)

        # Call the _get_auth_key method with the path to the temporary file
        result = TokenBasedAuth._get_auth_key(auth_key_path)

        # Assert that the method returns the correct auth key
        assert result == auth_key

    def test_get_auth_key_readable(self, tmp_path):
        # Create a temporary file containing the auth key
        auth_key = "my_auth_key"
        auth_key_file = io.StringIO(auth_key)

        # Call the _get_auth_key method with a file-like object
        result = TokenBasedAuth._get_auth_key(auth_key_file)

        # Assert that the method returns the correct auth key
        assert result == auth_key
