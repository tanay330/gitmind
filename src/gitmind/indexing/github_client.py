import httpx
from urllib.parse import urlparse

from gitmind.config import settings
import base64

    
def parse_repo_url(url:str):
    parsed=urlparse(url)
    if parsed.netloc!="github.com":
        
        raise ValueError("Invalid GitHub repository URL")
       
    parts=parsed.path.strip("/").split("/")
    if len(parts)!=2:
        raise ValueError("GitHub URL must contain owner and repository")
        
    return parts[0],parts[1]

def get_repo_info(owner:str,repo:str):
    api_url=f"https://api.github.com/repos/{owner}/{repo}" 
    headers = {
    "Authorization": f"Bearer {settings.github_token}"
}
    response=httpx.get(api_url,headers=headers,timeout=10.0)
    response.raise_for_status()
    data=response.json()
    return {
    "default_branch": data["default_branch"],
    "size": data["size"]
}

def list_repo_files(owner:str,repo:str,default_branch:str):
    api_url=f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1" 
    headers = {
    "Authorization": f"Bearer {settings.github_token}"
}
    response=httpx.get(api_url,headers=headers,timeout=10.0)
    response.raise_for_status()
    data = response.json()
    files=[]
    for item in data["tree"]:
        if item["type"]=="blob":
            files.append({
                "path":item["path"],
                "size":item["size"]})

    return files        
    

def fetch_file(owner:str,repo:str,path:str):
    api_url=f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers={
        "Authorization": f"Bearer {settings.github_token}"
    }
    response=httpx.get(api_url,headers=headers,timeout=10.0)
    response.raise_for_status()
    data=response.json()
    if data["type"] != "file":
        return None
    content=base64.b64decode(data["content"])
    try:
        text=content.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return text
        