from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from chainlit.data.storage_clients.azure_blob import AzureBlobStorageClient
from src.utils.config import (
    DATABASE,
    CONTAINER,
    STORAGE_ACCOUNT,
    STORAGE_SECRET,
)

storage_client = AzureBlobStorageClient(
    container_name=CONTAINER,
    storage_account=STORAGE_ACCOUNT,
    storage_key=STORAGE_SECRET,
)

def init_data_layer():
    """
    Initializes the SQLAlchemy data layer for Chainlit.
    
    Returns:
        SQLAlchemyDataLayer: The initialized data layer instance.
    """
    return SQLAlchemyDataLayer(
        conninfo=DATABASE,
        # ssl_require=True,
        storage_provider=storage_client,
    )