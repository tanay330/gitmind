import httpx
from urllib.parse import urlparse
import time
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
    

def fetch_file(owner: str, repo: str, path: str):
    api_url = (
        f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    )

    headers = {
        "Accept": "application/vnd.github.raw+json",
        "Authorization": f"Bearer {settings.github_token}",
    }

    for attempt in range(3):
        try:
            response = httpx.get(
                api_url,
                headers=headers,
                timeout=httpx.Timeout(30.0, connect=10.0),
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.text

        except (httpx.TimeoutException, httpx.NetworkError):
            if attempt == 2:
                raise

            time.sleep(2 ** attempt)

    return None
        