from kubernetes import client, config
import base64

def copy_secret():
    try:
        # Load the kubernetes configuration
        config.load_incluster_config()
        
        # Create API client
        v1 = client.CoreV1Api()
        
        # Get the source secret from mongodb namespace
        source_secret = v1.read_namespaced_secret("mongodb", "mongodb")
        
        # Extract the specific key we need
        password = source_secret.data.get('mongodb-passwords')
        if not password:
            raise Exception("mongodb-passwords key not found in source secret")
            
        # Create new secret object
        target_secret = client.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=client.V1ObjectMeta(
                name="app-mongodb-credentials"  # שם הsecret החדש
            ),
            data={
                "mongodb-passwords": password
            }
        )
        
        # Create the secret in the target namespace
        v1.create_namespaced_secret("default", target_secret)
        print("Secret successfully copied!")
        
    except Exception as e:
        print(f"Error copying secret: {str(e)}")
        raise e

if __name__ == "__main__":
    copy_secret()