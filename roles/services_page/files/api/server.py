import subprocess
import yaml
from fastapi import FastAPI, Response, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    with open("servers.yml") as file:
        app.state.servers = yaml.safe_load(file)
        yield
        app.state.servers = None


router = APIRouter()


class ServiceResponse(BaseModel):
    name: str
    port: int


class ServerResponse(BaseModel):
    name: str
    services: list[ServiceResponse]


@router.get("/servers")
async def get_servers() -> list[ServerResponse]:
    result = []
    for server in app.state.servers:
        services = []
        for service in server["services"]:
            services.append(ServiceResponse(
                name=service["name"], port=service["port"]))
        result.append(ServerResponse(name=server["name"], services=services))
    return result


@router.get("/server/{server_name}/status")
async def server_status(server_name: str) -> bool:
    for server in app.state.servers:
        if server["name"] == server_name:
            ip = server["ip"]
            try:
                subprocess.run(["ping", "-c", "1", "-w", "5", ip], check=True)
                return True
            except subprocess.CalledProcessError:
                return False


@router.post("/server/{server_name}/start", status_code=200)
async def start_server(server_name: str, response: Response):
    for server in app.state.servers:
        if server["name"] == server_name:
            mac = server["mac_addr"]
            try:
                subprocess.run(["wakeonlan", "-i", server["net_addr"], mac])
            except subprocess.CalledProcessError:
                response.status_code = 500
            return
    response.status_code = 404


app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/api/v1")


origins = [
    "http://localhost",
    "http://localhost:5173"]
app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=False,
                   allow_methods=["*"],
                   allow_headers=["*"])
