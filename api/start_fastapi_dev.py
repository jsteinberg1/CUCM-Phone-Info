import os
import uvicorn


if __name__ == "__main__":
    os.environ["SECRET_KEY"] = str(os.urandom(12))
    os.environ["REDIS_HOST"] = "127.0.0.1"
    os.environ["REDIS_PORT"] = "6379"
    
    log_level = "info"
    reload_state = True

    uvicorn.run("api.Main:api", host="0.0.0.0", port=8080, log_level=log_level, reload=reload_state)