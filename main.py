import uvicorn
import os
from api import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True) 